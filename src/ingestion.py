import os
import sys
import csv
import json
import ssl
import re
import urllib.request
import pypdf
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# SSL context for HTTPS requests
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

MYSCHEME_API_KEY = "tYTy5eEhlu9rFjyxuCr7ra7ACp4dv1RH8gWuHTDc"

# Official myScheme URL-to-API slug mapping table
MYSCHEME_SLUG_MAP = {
    "pm-pms-sc": "pmsfss",
    "pssgtd": "psgs-deg",
    "pmy-tcc": "pm-yasasvitcceobcebcdnts"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES_CSV = os.path.join(BASE_DIR, "data", "government_schemes", "sources.csv")
DOCS_DIR = os.path.join(BASE_DIR, "data", "government_schemes", "documents")
REPORT_PATH = os.path.join(DOCS_DIR, "validation_report.json")


def clean_html_text(html_content: str) -> str:
    """Robust regex-based HTML text extractor."""
    if not isinstance(html_content, str):
        html_content = str(html_content)
    text = re.sub(r'<(script|style|noscript|svg|head)[^>]*>.*?</\1>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    lines = [re.sub(r'\s+', ' ', line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def ensure_string(val) -> str:
    """Recursively convert string, list of strings/dicts, or dict into a single clean string."""
    if not val:
        return ""
    if isinstance(val, str):
        return val
    if isinstance(val, list):
        parts = [ensure_string(item) for item in val if item]
        return "\n".join([p for p in parts if p])
    if isinstance(val, dict):
        parts = []
        for k, v in val.items():
            s_v = ensure_string(v)
            if s_v:
                parts.append(f"{k}: {s_v}")
        return "\n".join(parts)
    return str(val)


def extract_label(field) -> str:
    """Safely extract string label from dict, list of dicts, or string."""
    if isinstance(field, dict):
        return field.get('label') or field.get('name') or field.get('title') or ''
    elif isinstance(field, list) and len(field) > 0:
        first = field[0]
        if isinstance(first, dict):
            return first.get('label') or first.get('name') or first.get('title') or ''
        return str(first)
    elif isinstance(field, str):
        return field
    return ''


def format_myscheme_content(scheme_data: dict, docs_data, faqs_data, app_channels) -> str:
    """Format myScheme API response into clean, comprehensive, structured text for downstream extraction."""
    lines = []
    
    basic = scheme_data.get('basicDetails', {}) if isinstance(scheme_data, dict) else {}
    s_name = basic.get('schemeName', '')
    ministry = extract_label(basic.get('nodalMinistryName')) or extract_label(basic.get('nodalDepartmentName'))
    s_type = extract_label(basic.get('schemeCategory'))
    
    lines.append(f"SCHEME NAME: {s_name}")
    if ministry:
        lines.append(f"IMPLEMENTING AUTHORITY: {ministry}")
    if s_type:
        lines.append(f"SCHEME CATEGORY / TYPE: {s_type}")
        
    s_content = scheme_data.get('schemeContent', {}) if isinstance(scheme_data, dict) else {}
    brief = ensure_string(s_content.get('briefDescription'))
    detailed = ensure_string(s_content.get('detailedDescription'))
    
    if brief:
        lines.append(f"\nBRIEF DESCRIPTION:\n{clean_html_text(brief)}")
    if detailed:
        lines.append(f"\nDETAILED DESCRIPTION:\n{clean_html_text(detailed)}")
        
    eligibility = ensure_string((scheme_data.get('eligibilityCriteria') or {}).get('eligibilityDescription')) if isinstance(scheme_data, dict) else ''
    if eligibility:
        lines.append(f"\nELIGIBILITY CRITERIA:\n{clean_html_text(eligibility)}")
        
    benefits = ensure_string(s_content.get('benefits'))
    if benefits:
        lines.append(f"\nBENEFITS AND FINANCIAL ASSISTANCE:\n{clean_html_text(benefits)}")
        
    exclusions = ensure_string(s_content.get('exclusions'))
    if exclusions:
        lines.append(f"\nEXCLUSIONS:\n{clean_html_text(exclusions)}")

    app_process = ensure_string(s_content.get('applicationProcess'))
    if app_process:
        lines.append(f"\nAPPLICATION PROCESS:\n{clean_html_text(app_process)}")

    # Extract documents list safely
    docs_list = []
    if isinstance(docs_data, list):
        docs_list = docs_data
    elif isinstance(docs_data, dict):
        en_docs = docs_data.get('en', {})
        if isinstance(en_docs, dict):
            docs_list = en_docs.get('documents_required', [])
        else:
            docs_list = docs_data.get('documents_required', [])

    if docs_list:
        lines.append("\nREQUIRED DOCUMENTS:")
        for idx, d in enumerate(docs_list, 1):
            doc_title = (d.get('title') or d.get('documentName') or d.get('name') or str(d)) if isinstance(d, dict) else str(d)
            lines.append(f"  {idx}. {clean_html_text(str(doc_title))}")

    # Extract FAQs list safely
    faqs_list = []
    if isinstance(faqs_data, list):
        faqs_list = faqs_data
    elif isinstance(faqs_data, dict):
        en_faqs = faqs_data.get('en', {})
        if isinstance(en_faqs, dict):
            faqs_list = en_faqs.get('faqs', [])
        else:
            faqs_list = faqs_data.get('faqs', [])

    if faqs_list:
        lines.append("\nFREQUENTLY ASKED QUESTIONS (FAQs):")
        for idx, faq in enumerate(faqs_list, 1):
            if isinstance(faq, dict):
                q = ensure_string(faq.get('question'))
                a = ensure_string(faq.get('answer'))
                lines.append(f"  Q{idx}: {clean_html_text(q)}")
                lines.append(f"  A{idx}: {clean_html_text(a)}")

    return "\n".join(lines)


def fetch_myscheme_api(url_slug: str):
    """Fetch complete scheme data from official myScheme REST API v6."""
    api_slug = MYSCHEME_SLUG_MAP.get(url_slug, url_slug)
    api_headers = {
        'User-Agent': HEADERS['User-Agent'],
        'x-api-key': MYSCHEME_API_KEY,
        'Origin': 'https://www.myscheme.gov.in',
        'Referer': 'https://www.myscheme.gov.in/',
        'Accept': 'application/json, text/plain, */*'
    }
    
    main_api_url = f"https://api.myscheme.gov.in/schemes/v6/public/schemes?slug={api_slug}&lang=en"
    req = urllib.request.Request(main_api_url, headers=api_headers)
    res = urllib.request.urlopen(req, context=ssl_ctx, timeout=15)
    data = json.loads(res.read().decode('utf-8'))
    
    scheme_obj = data.get('data')
    if not scheme_obj:
        raise ValueError(f"myScheme API returned no data for slug '{api_slug}'")

    scheme_id = scheme_obj.get('_id')
    docs_url = f"https://api.myscheme.gov.in/schemes/v6/public/schemes/{scheme_id}/documents?lang=en"
    faqs_url = f"https://api.myscheme.gov.in/schemes/v6/public/schemes/{scheme_id}/faqs?lang=en"
    app_url = f"https://api.myscheme.gov.in/schemes/v6/public/schemes/{scheme_id}/applicationchannel"

    docs_data = json.loads(urllib.request.urlopen(urllib.request.Request(docs_url, headers=api_headers), context=ssl_ctx).read().decode('utf-8')).get('data', [])
    faqs_data = json.loads(urllib.request.urlopen(urllib.request.Request(faqs_url, headers=api_headers), context=ssl_ctx).read().decode('utf-8')).get('data', [])
    app_data = json.loads(urllib.request.urlopen(urllib.request.Request(app_url, headers=api_headers), context=ssl_ctx).read().decode('utf-8')).get('data', [])

    en_scheme_data = scheme_obj.get('en', {})
    
    formatted_text = format_myscheme_content(en_scheme_data, docs_data, faqs_data, app_data)

    return {
        "content_source": main_api_url,
        "api_slug": api_slug,
        "scheme_id": scheme_id,
        "formatted_text": formatted_text,
        "raw_data": {
            "scheme": scheme_obj,
            "documents": docs_data,
            "faqs": faqs_data,
            "application_channels": app_data
        }
    }


def ingest_sources():
    """Reproducible ingestion pipeline for HTML and PDF sources."""
    os.makedirs(DOCS_DIR, exist_ok=True)
    
    with open(SOURCES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        sources = list(reader)
        
    validation_report = {
        "timestamp": datetime.now().isoformat(),
        "total_sources": len(sources),
        "successful_extractions": 0,
        "failed_extractions": 0,
        "results": []
    }

    for s in sources:
        doc_id = s['document_id']
        url = s['source_url']
        expected_fmt = s['format']
        title = s['title']
        
        result = {
            "document_id": doc_id,
            "title": title,
            "source_url": url,
            "expected_format": expected_fmt,
            "fetch_status": None,
            "final_url": None,
            "content_type": None,
            "format_detected": None,
            "magic_bytes": None,
            "retrieval_method": None,
            "extraction_status": "FAILED",
            "extracted_length": 0,
            "page_count": None,
            "local_raw_path": None,
            "local_extracted_path": None,
            "notes": ""
        }
        
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            res = urllib.request.urlopen(req, context=ssl_ctx, timeout=20)
            raw_bytes = res.read()
            result["fetch_status"] = res.status
            result["final_url"] = res.geturl()
            result["content_type"] = res.headers.get('Content-Type')
            
            if expected_fmt == 'PDF':
                magic = raw_bytes[:10]
                result["magic_bytes"] = magic.decode('ascii', errors='ignore')
                if raw_bytes.startswith(b'%PDF-'):
                    result["format_detected"] = "PDF"
                else:
                    result["format_detected"] = "NON_PDF_HTML"
                    
                pdf_path = os.path.join(DOCS_DIR, f"{doc_id}.pdf")
                with open(pdf_path, 'wb') as pf:
                    pf.write(raw_bytes)
                result["local_raw_path"] = os.path.relpath(pdf_path, BASE_DIR)
                
                reader = pypdf.PdfReader(pdf_path)
                pages = []
                total_text = ""
                for idx, page in enumerate(reader.pages):
                    p_text = page.extract_text() or ""
                    pages.append({
                        "page_number": idx + 1,
                        "text": p_text,
                        "char_count": len(p_text)
                    })
                    total_text += p_text + "\n"
                    
                result["page_count"] = len(pages)
                result["extracted_length"] = len(total_text)
                result["retrieval_method"] = "pdf_text_extractor"
                result["extraction_status"] = "SUCCESS" if len(total_text) > 100 else "FAILED"
                
                # Page boundaries object
                pages_json_path = os.path.join(DOCS_DIR, f"{doc_id}_pages.json")
                with open(pages_json_path, 'w', encoding='utf-8') as jf:
                    json.dump({"document_id": doc_id, "title": title, "total_pages": len(pages), "pages": pages}, jf, indent=2, ensure_ascii=False)

                # Standard extracted JSON object
                extracted_json_path = os.path.join(DOCS_DIR, f"{doc_id}_extracted.json")
                extracted_obj = {
                    "document_id": doc_id,
                    "source_url": url,
                    "retrieval_method": "pdf_text_extractor",
                    "retrieval_timestamp": datetime.now().isoformat(),
                    "content_type": "application/pdf",
                    "content_source": url,
                    "page_count": len(pages),
                    "content": total_text
                }
                with open(extracted_json_path, 'w', encoding='utf-8') as jf:
                    json.dump(extracted_obj, jf, indent=2, ensure_ascii=False)
                    
                result["local_extracted_path"] = os.path.relpath(extracted_json_path, BASE_DIR)
                result["notes"] = f"Successfully ingested native digital PDF ({len(pages)} pages, {len(total_text)} chars)."

            elif "myscheme.gov.in" in url:
                result["format_detected"] = "HTML_MYSCHEME_SPA"
                html_path = os.path.join(DOCS_DIR, f"{doc_id}.html")
                with open(html_path, 'wb') as hf:
                    hf.write(raw_bytes)
                result["local_raw_path"] = os.path.relpath(html_path, BASE_DIR)

                # Extract URL slug from source_url (e.g. pm-pms-sc, pssgtd, pmy-tcc)
                url_slug = url.rstrip('/').split('/')[-1]
                
                api_res = fetch_myscheme_api(url_slug)
                clean_text = api_res["formatted_text"]
                
                result["retrieval_method"] = "official_api"
                result["extracted_length"] = len(clean_text)
                result["extraction_status"] = "SUCCESS" if len(clean_text) > 500 else "FAILED"

                extracted_json_path = os.path.join(DOCS_DIR, f"{doc_id}_extracted.json")
                extracted_obj = {
                    "document_id": doc_id,
                    "source_url": url,
                    "retrieval_method": "official_api",
                    "retrieval_timestamp": datetime.now().isoformat(),
                    "content_type": "application/json",
                    "content_source": api_res["content_source"],
                    "api_slug": api_res["api_slug"],
                    "scheme_id": api_res["scheme_id"],
                    "content": clean_text,
                    "raw_api_data": api_res["raw_data"]
                }
                with open(extracted_json_path, 'w', encoding='utf-8') as jf:
                    json.dump(extracted_obj, jf, indent=2, ensure_ascii=False)

                result["local_extracted_path"] = os.path.relpath(extracted_json_path, BASE_DIR)
                result["notes"] = f"Successfully ingested myScheme source via official API ({len(clean_text)} extracted text chars)."

            else:
                result["format_detected"] = "HTML"
                html_path = os.path.join(DOCS_DIR, f"{doc_id}.html")
                with open(html_path, 'wb') as hf:
                    hf.write(raw_bytes)
                result["local_raw_path"] = os.path.relpath(html_path, BASE_DIR)
                
                raw_html_str = raw_bytes.decode('utf-8', errors='ignore')
                clean_text = clean_html_text(raw_html_str)
                
                result["retrieval_method"] = "html_parsing"
                result["extracted_length"] = len(clean_text)
                result["extraction_status"] = "SUCCESS" if len(clean_text) > 500 else "FAILED"
                
                extracted_json_path = os.path.join(DOCS_DIR, f"{doc_id}_extracted.json")
                extracted_obj = {
                    "document_id": doc_id,
                    "source_url": url,
                    "retrieval_method": "html_parsing",
                    "retrieval_timestamp": datetime.now().isoformat(),
                    "content_type": "text/html",
                    "content_source": url,
                    "content": clean_text
                }
                with open(extracted_json_path, 'w', encoding='utf-8') as jf:
                    json.dump(extracted_obj, jf, indent=2, ensure_ascii=False)

                result["local_extracted_path"] = os.path.relpath(extracted_json_path, BASE_DIR)
                result["notes"] = f"Successfully ingested HTML source ({len(clean_text)} extracted text chars)."

            if result["extraction_status"] == "SUCCESS":
                validation_report["successful_extractions"] += 1
            else:
                validation_report["failed_extractions"] += 1

        except Exception as e:
            result["extraction_status"] = "FAILED"
            result["notes"] = f"Ingestion error: {str(e)}"
            validation_report["failed_extractions"] += 1

        validation_report["results"].append(result)

    with open(REPORT_PATH, 'w', encoding='utf-8') as rf:
        json.dump(validation_report, rf, indent=2, ensure_ascii=False)

    print(f"Ingestion complete. {validation_report['successful_extractions']}/{validation_report['total_sources']} sources successfully ingested.")
    print(f"Validation report saved to {REPORT_PATH}")
    return validation_report


if __name__ == "__main__":
    ingest_sources()

