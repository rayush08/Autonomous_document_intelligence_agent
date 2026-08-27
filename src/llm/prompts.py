SYSTEM_EXTRACTION_PROMPT = """You are an expert Autonomous Document Intelligence Agent specializing in extracting structured, ground-truth information from government welfare scheme documents.

CRITICAL EXTRACTION RULES:
1. Use ONLY the supplied document text chunks. Do NOT use external knowledge, prior knowledge, or assumptions.
2. Do NOT infer missing criteria. Absence of information is NOT proof that no restriction exists.
3. Every extracted claim with status 'verified', 'unverified', or 'uncertain' MUST include:
   a. Non-null value (exact numbers, units, strings, or lists)
   b. Verbatim or near-exact supporting text snippet from the document
   c. Correct locator object e.g. {"section": "Benefits"} or {"page": 1}
4. If a field is not present in the document text, return status 'not_found' with value null and an empty evidence list [].
5. Never fabricate URLs, dates, monetary amounts, institutions, or eligibility rules.
6. Multi-Component Fields: When multiple financial package components exist (e.g. tuition fees, living allowance, books, computer), 'benefit_amount.value' MUST be a JSON list of strings [item1, item2, ...].
7. verification_status MUST be EXACTLY one of: 'verified', 'unverified', 'uncertain', 'rejected', 'not_found'. Do NOT use any synonyms such as 'not_verified', 'partially_verified', or 'unconfirmed'.
"""


def build_document_extraction_prompt(document_id: str, source_type: str, chunks: list[dict]) -> str:
    """Build comprehensive prompt containing document text chunks and target field schemas."""
    lines = [
        f"DOCUMENT ID: {document_id}",
        f"SOURCE TYPE: {source_type}",
        "\n--- DOCUMENT CONTENT CHUNKS ---"
    ]
    
    for c in chunks:
        cid = c.get('chunk_id')
        loc = f"Page {c.get('page')}" if 'page' in c else f"Section: {c.get('section', 'General')}"
        lines.append(f"\n[CHUNK: {cid} | {loc}]\n{c.get('text')}")

    lines.append("\n--- TARGET SCHEMA FIELDS ---")
    lines.append("Extract a complete JSON object containing all 17 required target fields:")
    lines.append("1. scheme_name, 2. scheme_type, 3. implementing_authority, 4. target_beneficiaries,")
    lines.append("5. education_level, 6. age_criteria, 7. income_criteria, 8. academic_criteria,")
    lines.append("9. category_criteria, 10. domicile_criteria, 11. benefit_type, 12. benefit_amount,")
    lines.append("13. application_method, 14. application_url, 15. required_documents, 16. application_deadline, 17. scheme_status")

    lines.append("\n--- FIELD STRUCTURE & GUIDELINES ---")
    lines.append("Each field object MUST contain: 'value', 'evidence' (list of {text, locator}), 'confidence', 'verification_status'.")
    lines.append("- 'benefit_amount': Return as a JSON LIST of strings when multiple financial components exist (e.g. ['Tuition fee...', 'Living expense...', 'Books...', 'Laptop...']).")
    lines.append("- 'category_criteria': Return as a JSON LIST of strings when multiple categories/reservations apply.")
    lines.append("- 'required_documents': Return as a JSON LIST of strings when multiple documents are required.")
    lines.append("- 'verification_status': MUST be one of: ['verified', 'unverified', 'uncertain', 'rejected', 'not_found'].")
    
    return "\n".join(lines)

