import re


def normalize_text_for_matching(text: str) -> str:
    """Normalize whitespace, punctuation, and casing for robust evidence snippet matching."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    # Remove common non-alphanumeric noise except numbers and currency symbols
    text = re.sub(r'[^\w\s₹$%.-]', '', text)
    return text.strip()


def check_snippet_in_chunk(snippet: str, chunk_text: str) -> bool:
    """Check if a snippet, its key numbers, or core semantic clauses appear in the chunk text."""
    norm_snip = normalize_text_for_matching(snippet)
    norm_chunk = normalize_text_for_matching(chunk_text)
    
    if not norm_snip or not norm_chunk:
        return False
        
    # 1. Exact normalized match
    if norm_snip in norm_chunk:
        return True
        
    # 2. Extract key numbers from snippet (e.g. 3.00, 1.50, 40.00, 31.12.2025)
    numbers = re.findall(r'\d+(?:[.,]\d+)*', snippet)
    if numbers:
        num_matches = sum(1 for num in numbers if normalize_text_for_matching(num) in norm_chunk)
        if num_matches > 0 and num_matches >= (len(numbers) // 2):
            return True

    # 3. Key phrase/clause match (splits by commas/semicolons/dashes)
    clauses = [re.sub(r'[^\w\s]', '', c).strip() for c in re.split(r'[,;.\-\n]', snippet) if len(c.strip()) > 5]
    if clauses:
        matching_clauses = sum(1 for cl in clauses if re.sub(r'[^\w\s]', '', cl).strip().lower() in norm_chunk)
        if matching_clauses > 0 and matching_clauses >= (len(clauses) // 2):
            return True

    return False


def verify_evidence_against_document(field_name: str, field_obj: dict, document_chunks: list[dict]) -> tuple[dict, bool]:
    """
    Deterministically verify evidence snippets and locators against actual document chunks.
    
    CRITICAL GROUNDING SAFETY RULES:
    1. If verification_status is not_found, value MUST be null and evidence MUST be [].
    2. If zero supporting evidence snippets exist in the document chunks, the unsupported claim
       MUST NOT be preserved as 'uncertain' with a non-null value! It MUST be converted to not_found.
    3. If evidence text is found on a different page than stated in the locator, the locator's page number
       is updated to the actual grounded page.
    
    Args:
        field_name (str): Name of the field.
        field_obj (dict): Field object with value, evidence, confidence, verification_status.
        document_chunks (list[dict]): Document chunks from segmentation.
        
    Returns:
        tuple[dict, bool]: (Verified/updated field_obj, is_grounded_bool)
    """
    if not isinstance(field_obj, dict):
        return {
            "value": None,
            "evidence": [],
            "confidence": 0.0,
            "verification_status": "not_found"
        }, False

    status = field_obj.get('verification_status', 'not_found')
    val = field_obj.get('value')
    evidence_list = field_obj.get('evidence', [])

    # Rule 1: not_found -> value MUST be null, evidence MUST be []
    if status == 'not_found' or val is None:
        field_obj['value'] = None
        field_obj['evidence'] = []
        field_obj['confidence'] = 0.0 if status == 'not_found' else field_obj.get('confidence', 0.0)
        field_obj['verification_status'] = 'not_found'
        return field_obj, True

    if status in {'verified', 'unverified', 'uncertain'}:
        if not isinstance(evidence_list, list) or len(evidence_list) == 0:
            # Unsupported value with no evidence -> Convert to not_found to prevent hallucinated preservation
            field_obj['value'] = None
            field_obj['evidence'] = []
            field_obj['confidence'] = 0.0
            field_obj['verification_status'] = 'not_found'
            return field_obj, False

        valid_evidence = []
        all_snippets_found = True

        for ev_item in evidence_list:
            if not isinstance(ev_item, dict):
                all_snippets_found = False
                continue
                
            snippet = ev_item.get('text', '')
            locator = ev_item.get('locator', {})
            
            if not snippet:
                all_snippets_found = False
                continue

            snippet_found_in_doc = False
            for chunk in document_chunks:
                chunk_text = chunk.get('text', '')
                if check_snippet_in_chunk(snippet, chunk_text):
                    snippet_found_in_doc = True
                    # Correct locator page number if actual chunk page is known
                    chunk_page = chunk.get('page')
                    if chunk_page is not None and locator.get('page') != chunk_page:
                        ev_item['locator']['page'] = chunk_page
                    break

            if snippet_found_in_doc:
                valid_evidence.append(ev_item)
            else:
                all_snippets_found = False

        # SAFETY CHECK FOR ZERO VALID EVIDENCE
        if len(valid_evidence) == 0:
            # Entirely unsupported claim -> Convert to not_found with null value!
            field_obj['value'] = None
            field_obj['evidence'] = []
            field_obj['confidence'] = 0.0
            field_obj['verification_status'] = 'not_found'
            return field_obj, False

        # Partial evidence found
        if not all_snippets_found:
            field_obj['verification_status'] = 'uncertain'
            field_obj['evidence'] = valid_evidence
            field_obj['confidence'] = min(field_obj.get('confidence', 1.0), 0.6)

        return field_obj, all_snippets_found

    return field_obj, True

