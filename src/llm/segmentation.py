import os
import json
import re


def segment_document(document_id: str, ingested_artifact: dict, docs_dir: str = None) -> list[dict]:
    """
    Segment an ingested document artifact into metadata-tagged chunks.
    
    For HTML/API documents:
      Splits according to logical section headers while preserving section titles.
      
    For PDF documents:
      Loads page-level data (e.g. from GOV-M-03_pages.json) while strictly preserving page numbers.
      
    Returns:
        list[dict]: List of chunk dicts, each containing:
            - chunk_id (str)
            - document_id (str)
            - text (str)
            - page (int, optional)
            - section (str, optional)
            - url (str, optional)
    """
    chunks = []
    source_url = ingested_artifact.get('source_url', '')
    ret_method = ingested_artifact.get('retrieval_method', '')
    
    # 1. Handle PDF page-based segmentation
    if ret_method == 'pdf_text_extractor' or ingested_artifact.get('content_type') == 'application/pdf':
        if docs_dir is None:
            docs_dir = os.path.dirname(os.path.abspath(__file__))
            # Fallback to standard documents directory
            docs_dir = os.path.join(os.path.dirname(os.path.dirname(docs_dir)), "data", "government_schemes", "documents")
            
        pages_json_path = os.path.join(docs_dir, f"{document_id}_pages.json")
        pages_data = []
        if os.path.exists(pages_json_path):
            with open(pages_json_path, 'r', encoding='utf-8') as pf:
                pages_data = json.load(pf).get('pages', [])
                
        if pages_data:
            for page_obj in pages_data:
                p_num = page_obj.get('page_number', 1)
                p_text = page_obj.get('text', '').strip()
                if p_text:
                    # Further split large pages into logical sub-chunks if needed
                    lines = p_text.splitlines()
                    chunk_id = f"{document_id}-p{p_num}-c1"
                    chunks.append({
                        "chunk_id": chunk_id,
                        "document_id": document_id,
                        "page": p_num,
                        "section": f"Page {p_num}",
                        "url": source_url,
                        "text": p_text
                    })
            return chunks

    # 2. Handle HTML / myScheme API section-based segmentation
    raw_content = ingested_artifact.get('content', '')
    if not raw_content:
        return chunks

    # Split by major section headers (e.g. SCHEME NAME:, ELIGIBILITY CRITERIA:, BENEFITS:, etc.)
    section_patterns = r'(?=\n(?:SCHEME NAME|IMPLEMENTING AUTHORITY|SCHEME CATEGORY|BRIEF DESCRIPTION|DETAILED DESCRIPTION|ELIGIBILITY CRITERIA|BENEFITS AND FINANCIAL ASSISTANCE|EXCLUSIONS|APPLICATION PROCESS|REQUIRED DOCUMENTS|FREQUENTLY ASKED QUESTIONS):)'
    sections = re.split(section_patterns, raw_content)

    c_idx = 1
    for sec_text in sections:
        sec_text = sec_text.strip()
        if not sec_text:
            continue
            
        first_line = sec_text.splitlines()[0] if sec_text.splitlines() else ""
        section_name = first_line.split(':')[0].strip() if ':' in first_line else "General"
        
        chunks.append({
            "chunk_id": f"{document_id}-sec{c_idx}",
            "document_id": document_id,
            "section": section_name,
            "url": source_url,
            "text": sec_text
        })
        c_idx += 1
        
    if not chunks:
        chunks.append({
            "chunk_id": f"{document_id}-sec1",
            "document_id": document_id,
            "section": "Document Content",
            "url": source_url,
            "text": raw_content.strip()
        })

    return chunks

