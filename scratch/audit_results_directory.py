import os
import json

results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"

print("==========================================")
print("EVALUATION RESULTS ARTIFACTS AUDIT")
print("==========================================")

files = sorted(os.listdir(results_dir))
for fname in files:
    fpath = os.path.join(results_dir, fname)
    size = os.path.getsize(fpath)
    print(f"File: {fname:<35} | Size: {size:<7} bytes")
    if fname.endswith(".json"):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                overall = data.get("overall", {})
                mode = data.get("mode", "unknown")
                print(f"   -> Mode: {mode} | Docs: {overall.get('total_documents_evaluated')} | Schema Valid: {overall.get('schema_validity_rate')*100:.1f}% | Field Acc: {overall.get('field_extraction_accuracy')*100:.1f}%")
        except Exception as e:
            print(f"   -> Error reading JSON: {e}")
