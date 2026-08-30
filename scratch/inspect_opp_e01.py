import json

results_path = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results\real_benchmark_results.json"

with open(results_path, "r", encoding="utf-8") as f:
    data = json.load(f)

raw_results = data.get("raw_results", [])
opp1 = [r for r in raw_results if r.get("document_id") == "OPP-E-01"][0]

print("DOCUMENT ID:", opp1["document_id"])
print("SCHEMA VALID:", opp1["schema_valid"])

for fc in opp1["field_comparisons"]:
    print(f"\nField: {fc['field_name']}")
    print(f"  Exp Status: {fc.get('expected_status')} | Ext Status: {fc.get('extracted_status')}")
    print(f"  Exp Value : {fc.get('expected_value') if 'expected_value' in fc else 'N/A'}")
    print(f"  Ext Value : {fc.get('extracted_value') if 'extracted_value' in fc else 'N/A'}")
