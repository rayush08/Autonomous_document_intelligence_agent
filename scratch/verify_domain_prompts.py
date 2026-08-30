import sys
import os
sys.path.insert(0, os.getcwd())

from src.llm.prompts import build_document_extraction_prompt, OPPORTUNITY_FIELDS, GOVERNMENT_SCHEME_FIELDS

sample_chunks = [{"chunk_id": "c1", "text": "Sample document content."}]

opp_prompt = build_document_extraction_prompt("OPP-E-01", "HTML", sample_chunks)
gov_prompt = build_document_extraction_prompt("GOV-E-01", "HTML", sample_chunks)

print("="*60)
print("PROMPT DOMAIN ISOLATION DIAGNOSTIC")
print("="*60)

print("\nDocument: OPP-E-01")
print("Detected Domain: opportunities")
print("Prompt Field Set:")
print(OPPORTUNITY_FIELDS)

print("\nDocument: GOV-E-01")
print("Detected Domain: government_schemes")
print("Prompt Field Set:")
print(GOVERNMENT_SCHEME_FIELDS)

print("\n--- Diagnostic Assertions ---")
opp_has_stipend = "stipend_or_funding" in opp_prompt and "organization" in opp_prompt
opp_has_no_scheme = "scheme_name" not in opp_prompt and "domicile_criteria" not in opp_prompt

gov_has_scheme = "scheme_name" in gov_prompt and "domicile_criteria" in gov_prompt
gov_has_no_stipend = "stipend_or_funding" not in gov_prompt

print(f"OPP-E-01 Contains Opportunity Fields Only: {opp_has_stipend and opp_has_no_scheme}")
print(f"GOV-E-01 Contains Scheme Fields Only: {gov_has_scheme and gov_has_no_stipend}")
