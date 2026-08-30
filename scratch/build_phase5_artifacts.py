import os
import json

results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"

run_files = [
    os.path.join(results_dir, "real_run_phase5_1_results.json"),
    os.path.join(results_dir, "real_run_phase5_2_results.json"),
    os.path.join(results_dir, "real_run_phase5_3_results.json")
]

mismatches = []
field_mismatch_counts = {}

for r_idx, fpath in enumerate(run_files):
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            docs = data.get("document_results", {})
            for doc_id, doc_res in docs.items():
                domain = doc_res.get("domain", "unknown")
                f_evals = doc_res.get("field_evaluations", {})
                for field_name, f_info in f_evals.items():
                    is_val_match = f_info.get("value_match", True)
                    is_stat_match = f_info.get("status_match", True)
                    if not is_val_match or not is_stat_match:
                        field_mismatch_counts[field_name] = field_mismatch_counts.get(field_name, 0) + 1
                        mismatches.append({
                            "run_id": f"phase5_{r_idx+1}",
                            "document_id": doc_id,
                            "domain": domain,
                            "field": field_name,
                            "expected_value": f_info.get("gold_value"),
                            "actual_value": f_info.get("extracted_value"),
                            "expected_status": f_info.get("gold_status"),
                            "actual_status": f_info.get("extracted_status"),
                            "value_match": is_val_match,
                            "status_match": is_stat_match
                        })

sorted_fields = sorted(field_mismatch_counts.items(), key=lambda x: x[1], reverse=True)

failure_analysis = {
    "total_mismatches": len(mismatches),
    "mismatches_per_field": field_mismatch_counts,
    "top_failing_fields": sorted_fields[:10],
    "mismatch_records": mismatches
}

with open(os.path.join(results_dir, "phase5_failure_analysis.json"), "w", encoding="utf-8") as f:
    json.dump(failure_analysis, f, indent=2)

print(f"Total mismatches extracted: {len(mismatches)}")
print("Top failing fields:")
for fname, count in sorted_fields[:10]:
    print(f"  - {fname}: {count} mismatches")
