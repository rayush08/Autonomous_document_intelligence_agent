import json

results_path = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results\real_benchmark_results.json"

with open(results_path, "r", encoding="utf-8") as f:
    data = json.load(f)

raw_results = data.get("raw_results", [])
print(f"Total documents in raw_results: {len(raw_results)}")

total_mismatches = 0

for doc in raw_results:
    doc_id = doc.get("document_id")
    domain = doc.get("domain")
    f_comps = doc.get("field_comparisons", [])
    
    print(f"\n=======================================================")
    print(f"DOCUMENT: {doc_id:<10} | Domain: {domain}")
    print(f"=======================================================")
    
    for fc in f_comps:
        field_name = fc.get("field_name")
        val_score = fc.get("value_score", 0.0)
        val_match = fc.get("value_match", False)
        status_match = fc.get("status_match", False)
        exp_status = fc.get("expected_status")
        ext_status = fc.get("extracted_status")
        
        if not val_match or not status_match:
            total_mismatches += 1
            print(f"  [MISMATCH] [{field_name:<24}] ValScore: {val_score:.2f} | ValMatch: {val_match} | StatMatch: {status_match} (ExpStat: '{exp_status}' vs ExtStat: '{ext_status}')")

print(f"\nTotal Field Mismatches across all 10 documents: {total_mismatches}")
