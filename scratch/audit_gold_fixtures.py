import os
import json

gold_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\gold"

files = [f for f in os.listdir(gold_dir) if f.endswith(".json")]

print(f"Total Gold Fixtures: {len(files)}")

for f_name in sorted(files):
    f_path = os.path.join(gold_dir, f_name)
    with open(f_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    doc_id = data.get("document_metadata", {}).get("document_id", f_name)
    fields = [k for k in data.keys() if k != "document_metadata"]
    verified_count = sum(1 for k in fields if isinstance(data[k], dict) and data[k].get("verification_status") in {"verified", "unverified"})
    not_found_count = sum(1 for k in fields if isinstance(data[k], dict) and data[k].get("verification_status") == "not_found")
    
    print(f"\nDocument: {doc_id:<12} | Fields: {len(fields):<2} | Verified/Unverified: {verified_count:<2} | Not Found: {not_found_count:<2}")
    print(f"  Field List: {', '.join(fields[:6])}...")
