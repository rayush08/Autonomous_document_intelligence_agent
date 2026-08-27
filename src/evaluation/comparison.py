import re


def normalize_str(s: str) -> str:
    """Normalize string for intelligent comparison, mapping equivalent currency symbols and period terms."""
    if not isinstance(s, str):
        return ""
    s = s.lower().strip()
    s = re.sub(r'\s+', ' ', s)

    # Normalize currency symbols & abbreviations
    s = re.sub(r'\b(?:rs|rs\.|inr|₹)\b', 'rupees', s)
    s = re.sub(r'\b(?:usd|\$)\b', 'dollars', s)
    s = re.sub(r'\b(?:eur|€)\b', 'euros', s)
    
    # Normalize period / frequency expressions
    s = re.sub(r'\b(?:per annum|annually|p\.a\.|per year)\b', 'per year', s)
    s = re.sub(r'\b(?:per month|monthly|p\.m\.)\b', 'per month', s)
    s = re.sub(r'\b(?:per week|weekly|p\.w\.)\b', 'per week', s)

    s = re.sub(r'[^\w\s]', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s



def compare_values(exp_val, ext_val) -> float:
    """
    Intelligently compare expected value vs extracted value.
    Returns float score between 0.0 (mismatch) and 1.0 (exact match).
    """
    if exp_val is None and ext_val is None:
        return 1.0
    if exp_val is None or ext_val is None:
        return 0.0

    # List comparisons
    if isinstance(exp_val, list) or isinstance(ext_val, list):
        exp_list = exp_val if isinstance(exp_val, list) else [str(exp_val)]
        ext_list = ext_val if isinstance(ext_val, list) else [str(ext_val)]

        if not exp_list and not ext_list:
            return 1.0
        if not exp_list or not ext_list:
            return 0.0

        matches = 0
        for exp_item in exp_list:
            exp_norm = normalize_str(str(exp_item))
            if any(exp_norm in normalize_str(str(ext_item)) or normalize_str(str(ext_item)) in exp_norm for ext_item in ext_list):
                matches += 1

        return matches / max(len(exp_list), len(ext_list))

    # Single string / numeric comparison
    exp_norm = normalize_str(str(exp_val))
    ext_norm = normalize_str(str(ext_val))

    if exp_norm == ext_norm:
        return 1.0

    # Extract all numeric numbers from both strings
    exp_nums = re.findall(r'\b\d+(?:\.\d+)?\b', exp_norm)
    ext_nums = re.findall(r'\b\d+(?:\.\d+)?\b', ext_norm)

    # If numbers exist in both and differ, return 0.0 (do NOT perform substring/partial match for different numbers!)
    if exp_nums and ext_nums and set(exp_nums) != set(ext_nums):
        return 0.0

    if exp_norm in ext_norm or ext_norm in exp_norm:
        return 0.9

    # Partial word overlap
    exp_words = set(exp_norm.split())
    ext_words = set(ext_norm.split())
    if exp_words and ext_words:
        overlap = len(exp_words.intersection(ext_words))
        union = len(exp_words.union(ext_words))
        jaccard = overlap / union if union > 0 else 0.0
        if jaccard >= 0.5:
            return jaccard

    return 0.0


def compare_field(field_name: str, exp_field: dict, ext_field: dict) -> dict:
    """
    Compare single field container between expected ground truth and extracted record.
    Returns field comparison metrics dictionary.
    """
    exp_status = exp_field.get("verification_status", "not_found") if isinstance(exp_field, dict) else "not_found"
    ext_status = ext_field.get("verification_status", "not_found") if isinstance(ext_field, dict) else "not_found"
    
    exp_val = exp_field.get("value") if isinstance(exp_field, dict) else None
    ext_val = ext_field.get("value") if isinstance(ext_field, dict) else None

    exp_ev = exp_field.get("evidence", []) if isinstance(exp_field, dict) else []
    ext_ev = ext_field.get("evidence", []) if isinstance(ext_field, dict) else []

    status_match = (exp_status == ext_status)
    value_score = compare_values(exp_val, ext_val)
    value_match = (value_score >= 0.7)

    # Missing information accuracy check (genuinely absent field identified correctly as not_found)
    is_genuinely_missing = (exp_status == "not_found")
    missing_info_correct = (is_genuinely_missing and ext_status == "not_found")

    # Hallucination / Unsupported claim check: extracted non-null claim when ground truth is not_found
    is_hallucination = (is_genuinely_missing and ext_status != "not_found" and ext_val is not None)

    # Evidence grounding check: verified claim has non-empty evidence
    evidence_grounded = False
    if ext_status in {"verified", "unverified", "uncertain"} and ext_val is not None:
        evidence_grounded = (isinstance(ext_ev, list) and len(ext_ev) >= 1)
    elif ext_status == "not_found":
        evidence_grounded = True

    return {
        "field_name": field_name,
        "status_match": status_match,
        "value_score": value_score,
        "value_match": value_match,
        "is_genuinely_missing": is_genuinely_missing,
        "missing_info_correct": missing_info_correct,
        "is_hallucination": is_hallucination,
        "evidence_grounded": evidence_grounded,
        "expected_status": exp_status,
        "extracted_status": ext_status
    }

