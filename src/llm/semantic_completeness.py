import re

# Field-level semantic hints registry for configurable cross-domain validation
FIELD_SEMANTIC_HINTS = {
    "benefit_amount": {
        "keywords": [
            "tuition fee", "maintenance allowance", "hostel allowance", "scholarship amount",
            "stipend", "grant", "financial assistance", "financial support", "reimbursement",
            "cfa", "subsidy", "book bank"
        ],
        "trigger_keywords": ["tuition fee", "maintenance allowance", "stipend"],
        "message": "Field 'benefit_amount' was reported as 'not_found' / null, but source document text contains affirmative financial indicators ({kw_str}). Re-examine the source text and extract ALL benefit components into a JSON list."
    },
    "stipend_or_funding": {
        "keywords": [
            "stipend", "allowance", "grant", "funding", "financial support",
            "subsistence allowance", "mobility allowance", "living allowance"
        ],
        "trigger_keywords": ["stipend", "allowance", "grant"],
        "message": "Field 'stipend_or_funding' was reported as 'not_found' / null, but source document text contains affirmative funding indicators ({kw_str}). Re-examine the source text and extract ALL funding components into a JSON list."
    },
    "required_documents": {
        "keywords": [
            "aadhaar", "income certificate", "caste certificate", "domicile certificate",
            "mark sheet", "marksheet", "passport size photograph", "bank passbook",
            "ration card", "bonafide certificate", "declaration"
        ],
        "trigger_keywords": ["aadhaar", "income certificate", "caste certificate", "marksheet", "bank passbook"],
        "message": "Field 'required_documents' was reported as 'not_found' / null, but source document text contains affirmative document requirements ({kw_str}). Re-examine the source text and extract ALL required documents into a JSON list."
    }
}


EXCLUSION_INDICATOR_PATTERNS = [
    r"not eligible",
    r"ineligible",
    r"no\s+(?:tuition|stipend|financial|grant|fellowship|allowance)\s+(?:fee|support|assistance|provided|payable|given)",
    r"shall not be (?:provided|paid|given|eligible|considered)",
    r"will not be (?:provided|paid|given|eligible|considered)",
    r"excluding",
    r"neither.*nor",
    r"without any (?:stipend|financial support|grant)",
    r"does not include",
    r"does not provide",
    r"previously offered",
    r"formerly provided",
    r"no longer available",
    r"on another page",
    r"see external link"
]


def is_affirmative_indicator(text: str, keyword: str) -> bool:
    """Verify keyword appears in affirmative benefit context rather than an exclusion clause."""
    sentences = re.split(r'[\.\n;]', text.lower())
    matching_sentences = [s.strip() for s in sentences if keyword in s]

    for sent in matching_sentences:
        if any(re.search(pat, sent) for pat in EXCLUSION_INDICATOR_PATTERNS):
            continue
        return True

    return False


def validate_semantic_completeness(record: dict, chunks: list[dict]) -> tuple[bool, list[str]]:
    """
    Inspect document chunks for strong field indicators when a field is reported as not_found / None.
    Generically detects when LLM output omitted information present in source document text without document_id hardcoding.
    
    Args:
        record (dict): Extracted scheme or opportunity record.
        chunks (list[dict]): Document chunks extracted from source artifact.
        
    Returns:
        tuple[bool, list[str]]: (is_complete, error_messages)
    """
    errors = []
    if not isinstance(record, dict) or not chunks:
        return True, []

    full_doc_text = " ".join([c.get("text", "") for c in chunks if isinstance(c, dict)]).lower()

    # Iterate dynamically over field semantic hints registry
    for field_name, hint_cfg in FIELD_SEMANTIC_HINTS.items():
        if field_name in record and isinstance(record[field_name], dict):
            f_field = record[field_name]
            f_val = f_field.get("value")
            f_status = f_field.get("verification_status")

            if f_val is None or f_status == "not_found":
                matches = [kw for kw in hint_cfg["keywords"] if kw in full_doc_text and is_affirmative_indicator(full_doc_text, kw)]
                if len(matches) >= 2 or any(is_affirmative_indicator(full_doc_text, kw) for kw in hint_cfg["trigger_keywords"]):
                    found_kw_str = ", ".join(matches[:4])
                    msg_text = hint_cfg["message"].format(kw_str=found_kw_str)
                    errors.append(f"SemanticCompletenessError: {msg_text}")

    # Check for partial list completeness on required_documents
    if "required_documents" in record and isinstance(record["required_documents"], dict):
        f_val = record["required_documents"].get("value")
        if isinstance(f_val, list) and 1 <= len(f_val) <= 2:
            doc_kw_matches = [kw for kw in FIELD_SEMANTIC_HINTS["required_documents"]["keywords"] if kw in full_doc_text]
            if len(doc_kw_matches) >= len(f_val) + 2:
                errors.append(f"SemanticCompletenessError: Field 'required_documents' extracted only {len(f_val)} items, but source document contains additional requirement indicators ({', '.join(doc_kw_matches[:4])}). Re-examine source text and extract ALL required documents into a complete list.")

    is_valid = (len(errors) == 0)
    return is_valid, errors



