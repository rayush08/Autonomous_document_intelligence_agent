SYSTEM_EXTRACTION_PROMPT = """You are an expert Autonomous Document Intelligence Agent specializing in extracting structured, ground-truth information from government welfare schemes and opportunities documents.

CRITICAL EXTRACTION RULES:
1. Use ONLY the supplied document text chunks. Do NOT use external knowledge, prior knowledge, or assumptions.
2. Do NOT infer missing criteria. Absence of information is NOT proof that no restriction exists.
3. Every extracted claim with status 'verified', 'unverified', or 'uncertain' MUST include:
   a. Non-null value (exact numbers, units, strings, or lists)
   b. Verbatim or near-exact supporting text snippet from the document
   c. Correct locator object e.g. {"section": "Benefits"} or {"page": 1}
4. If a field is not present in the document text, return status 'not_found' with value null and an empty evidence list [].
5. Never fabricate URLs, dates, monetary amounts, institutions, or eligibility rules.
6. Multi-Component Fields: When multiple financial package components exist (e.g. tuition fees, living allowance, books, computer), the financial field MUST be a JSON list of strings [item1, item2, ...].
7. verification_status MUST be EXACTLY one of: 'verified', 'unverified', 'uncertain', 'rejected', 'not_found'. Do NOT use any synonyms such as 'not_verified', 'partially_verified', or 'unconfirmed'.
"""

GOVERNMENT_SCHEME_FIELDS = [
    "scheme_name", "scheme_type", "implementing_authority", "target_beneficiaries",
    "education_level", "age_criteria", "income_criteria", "academic_criteria",
    "category_criteria", "domicile_criteria", "benefit_type", "benefit_amount",
    "application_method", "application_url", "required_documents", "application_deadline", "scheme_status"
]

OPPORTUNITY_FIELDS = [
    "title", "organization", "opportunity_type", "education_level",
    "eligible_disciplines", "skills_required", "experience_required", "eligibility_notes",
    "location", "mode", "duration", "stipend_or_funding",
    "start_date", "application_deadline", "application_url", "required_documents"
]

GOVERNMENT_SCHEME_GROUPS = {
    "metadata": ["scheme_name", "scheme_type", "implementing_authority", "scheme_status"],
    "eligibility": ["target_beneficiaries", "education_level", "age_criteria", "income_criteria", "academic_criteria", "category_criteria", "domicile_criteria"],
    "benefits": ["benefit_type", "benefit_amount"],
    "application": ["application_method", "application_url", "required_documents", "application_deadline"]
}

OPPORTUNITY_GROUPS = {
    "metadata": ["title", "organization", "opportunity_type", "application_url", "start_date", "application_deadline"],
    "eligibility": ["education_level", "eligible_disciplines", "skills_required", "experience_required", "eligibility_notes", "required_documents"],
    "details": ["location", "mode", "duration", "stipend_or_funding"]
}


def build_group_extraction_prompt(document_id: str, source_type: str, group_name: str, target_fields: list[str], chunks: list[dict]) -> str:
    """Build focused prompt for a specific field group."""
    is_opp = document_id.upper().startswith("OPP-") if document_id else False
    domain_name = "opportunity" if is_opp else "government welfare scheme"

    lines = [
        f"DOCUMENT ID: {document_id}",
        f"DOMAIN: {domain_name}",
        f"FIELD GROUP: {group_name.upper()}",
        f"SOURCE TYPE: {source_type}",
        "\n--- DOCUMENT CONTENT CHUNKS ---"
    ]

    for c in chunks:
        cid = c.get('chunk_id')
        loc = f"Page {c.get('page')}" if 'page' in c else f"Section: {c.get('section', 'General')}"
        lines.append(f"\n[CHUNK: {cid} | {loc}]\n{c.get('text')}")

    lines.append(f"\n--- TARGET GROUP FIELDS ({len(target_fields)}) ---")
    lines.append(f"Extract JSON object containing EXACTLY these target fields: {', '.join(target_fields)}")
    lines.append("\n--- FIELD-SPECIFIC GUIDELINES ---")
    lines.append("Each field object MUST contain: 'value', 'evidence' (list of {text, locator}), 'confidence', 'verification_status'.")
    lines.append("- If a field is missing, return status 'not_found' with value null and empty evidence [].")

    if "required_documents" in target_fields:
        lines.append("- 'required_documents': Extract ALL explicitly required documents into a complete JSON LIST of strings (e.g. ['Aadhaar Card', 'Income Certificate', 'Mark Sheet']). Do NOT stop after the first document.")
    if "target_beneficiaries" in target_fields:
        lines.append("- 'target_beneficiaries': Capture ALL explicitly mentioned beneficiary groups and qualifying categories.")
    if "income_criteria" in target_fields:
        lines.append("- 'income_criteria': Preserve exact numeric income limits, annual thresholds, and conditions.")
    if "academic_criteria" in target_fields:
        lines.append("- 'academic_criteria': Preserve exact percentage, CGPA/GPA, qualifying exam, and course requirements.")
    if "domicile_criteria" in target_fields:
        lines.append("- 'domicile_criteria': Preserve exact geographic restrictions without generalizing district/state bounds.")
    if "category_criteria" in target_fields:
        lines.append("- 'category_criteria': Extract ALL eligible categories as a JSON list (e.g. ['OBC', 'EBC', 'DNT']).")
    if "benefit_amount" in target_fields or "stipend_or_funding" in target_fields:
        lines.append("- Monetary Amounts / Funding: Preserve complete multi-tier financial clauses, amounts, and numeric commas (e.g. ₹50,000, $5,400).")

    lines.append("- 'verification_status': MUST be one of: ['verified', 'unverified', 'uncertain', 'rejected', 'not_found'].")
    lines.append("\nCRITICAL: Extract ONLY the requested fields for this group. Do NOT return fields outside this group.")

    return "\n".join(lines)



def build_document_extraction_prompt(document_id: str, source_type: str, chunks: list[dict]) -> str:
    """Build domain-aware prompt containing document text chunks and target field schemas."""
    is_opportunity = document_id.upper().startswith("OPP-") if document_id else False
    domain_name = "opportunity/grant/fellowship" if is_opportunity else "government welfare scheme"
    target_fields = OPPORTUNITY_FIELDS if is_opportunity else GOVERNMENT_SCHEME_FIELDS

    lines = [
        f"DOCUMENT ID: {document_id}",
        f"DOMAIN: {domain_name}",
        f"SOURCE TYPE: {source_type}",
        "\n--- DOCUMENT CONTENT CHUNKS ---"
    ]
    
    for c in chunks:
        cid = c.get('chunk_id')
        loc = f"Page {c.get('page')}" if 'page' in c else f"Section: {c.get('section', 'General')}"
        lines.append(f"\n[CHUNK: {cid} | {loc}]\n{c.get('text')}")

    lines.append("\n--- TARGET SCHEMA FIELDS ---")
    lines.append(f"Extract a complete JSON object containing all {len(target_fields)} target fields for this document domain:")
    
    field_list_str = ", ".join([f"{idx+1}. {fname}" for idx, fname in enumerate(target_fields)])
    lines.append(field_list_str)

    lines.append("\n--- FIELD STRUCTURE & GUIDELINES ---")
    lines.append("Each field object MUST contain: 'value', 'evidence' (list of {text, locator}), 'confidence', 'verification_status'.")
    lines.append("- If a field is present in the text, extract its non-null value and verbatim evidence snippet.")
    lines.append("- If a field is missing from the document, return status 'not_found' with value null and empty evidence [].")
    lines.append("- 'required_documents': Extract ALL required documents into a complete JSON LIST of strings (e.g. ['Aadhaar Card', 'Income Certificate', 'Mark Sheet']). Do NOT stop after the first document.")
    
    if is_opportunity:
        lines.append("- 'stipend_or_funding': Return as a JSON LIST of strings when multiple funding components exist (e.g. ['Stipend $600/wk', 'Travel grant $1000']).")
        lines.append("- 'eligible_disciplines': Return as a JSON LIST of strings when multiple disciplines apply.")
    else:
        lines.append("- 'benefit_amount': Return as a JSON LIST of strings when multiple financial components exist (e.g. ['Tuition fee waiver', 'Maintenance allowance Rs 10,000/yr']).")
        lines.append("- 'category_criteria': Return as a JSON LIST of strings when multiple categories apply (e.g. ['OBC', 'EBC', 'DNT']).")
        
    lines.append("- 'verification_status': MUST be one of: ['verified', 'unverified', 'uncertain', 'rejected', 'not_found'].")
    lines.append("\nCRITICAL: Do NOT substitute fields from other domains. Extract ONLY the target schema fields listed above.")
    lines.append("CRITICAL MONETARY RULE: Do NOT split a single monetary number containing a comma (e.g. ₹50,000, $5,400, 2,700 CHF) into multiple list items.")

    
    return "\n".join(lines)
