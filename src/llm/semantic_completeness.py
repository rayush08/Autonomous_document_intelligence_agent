import re

BENEFIT_INDICATOR_KEYWORDS = [
    "tuition fee",
    "maintenance allowance",
    "hostel allowance",
    "scholarship amount",
    "stipend",
    "grant",
    "financial assistance",
    "financial support",
    "reimbursement",
    "cfa",
    "subsidy",
    "book bank",
]


def validate_semantic_completeness(record: dict, chunks: list[dict]) -> tuple[bool, list[str]]:
    """
    Inspect document chunks for strong field indicators when a field is reported as not_found / None.
    Generically detects when LLM output omitted information present in source document text without document_id hardcoding.
    
    Args:
        record (dict): Extracted scheme record.
        chunks (list[dict]): Document chunks extracted from source artifact.
        
    Returns:
        tuple[bool, list[str]]: (is_complete, error_messages)
    """
    errors = []
    if not isinstance(record, dict) or not chunks:
        return True, []

    # Combine chunk text for generic domain keyword matching
    full_doc_text = " ".join([c.get("text", "") for c in chunks if isinstance(c, dict)]).lower()

    # 1. Generic semantic completeness check for benefit_amount
    b_field = record.get("benefit_amount", {})
    if isinstance(b_field, dict):
        b_val = b_field.get("value")
        b_status = b_field.get("verification_status")

        if b_val is None or b_status == "not_found":
            matches = [kw for kw in BENEFIT_INDICATOR_KEYWORDS if kw in full_doc_text]
            # Trigger retry if document text contains strong benefit financial indicators
            if len(matches) >= 2 or any(kw in full_doc_text for kw in ["tuition fee", "maintenance allowance", "stipend"]):
                found_kw_str = ", ".join(matches[:4])
                errors.append(
                    f"SemanticCompletenessError: Field 'benefit_amount' was reported as 'not_found' / null, "
                    f"but source document text contains benefit financial indicators ({found_kw_str}). "
                    f"Re-examine the source text and extract ALL benefit components into a JSON list."
                )

    is_valid = (len(errors) == 0)
    return is_valid, errors

