import os
import json

results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"
run_files = ["real_run_1_results.json", "real_run_2_results.json", "real_run_3_results.json"]

mismatches = []

for r_idx, rf in enumerate(run_files, 1):
    fpath = os.path.join(results_dir, rf)
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        for doc in data.get("raw_results", []):
            doc_id = doc.get("document_id")
            domain = doc.get("domain")
            for fc in doc.get("field_comparisons", []):
                fname = fc.get("field_name")
                v_match = fc.get("value_match", False)
                s_match = fc.get("status_match", False)
                exp_val = fc.get("expected_value")
                ext_val = fc.get("extracted_value")
                exp_stat = fc.get("expected_status")
                ext_stat = fc.get("extracted_status")
                v_score = fc.get("value_score", 0.0)
                ev = fc.get("extracted_evidence", [])
                
                if not v_match or not s_match:
                    # Classify failure
                    if fname == "required_documents" and isinstance(exp_val, list) and isinstance(ext_val, list) and len(ext_val) < len(exp_val):
                        cat = "B — Partial extraction"
                        reason = f"Extracted partial list ({len(ext_val)} items) when gold expects {len(exp_val)} items."
                    elif ext_stat == "not_found" and exp_stat != "not_found":
                        cat = "A — Genuine model omission"
                        reason = "Model returned not_found for field present in source text."
                    elif exp_stat == "not_found" and ext_stat != "not_found" and ext_val is not None:
                        cat = "D — Over-extraction / hallucinated component"
                        reason = "Extracted non-null claim for field not present in gold."
                    elif not s_match and v_match:
                        cat = "H — Verification status mismatch"
                        reason = f"Value matched ({v_score:.2f}) but status mismatched (Exp: {exp_stat} vs Ext: {ext_stat})."
                    else:
                        cat = "C — Wrong extraction"
                        reason = f"Extracted '{ext_val}' does not match gold '{exp_val}' (Score: {v_score:.2f})."
                        
                    mismatches.append({
                        "run_id": r_idx,
                        "document_id": doc_id,
                        "domain": domain,
                        "field_name": fname,
                        "gold_value": exp_val,
                        "predicted_value": ext_val,
                        "gold_status": exp_stat,
                        "predicted_status": ext_stat,
                        "evidence": ev,
                        "comparison_score": v_score,
                        "category": cat,
                        "reason": reason
                    })

print(f"Total Mismatches across Runs 1-3: {len(mismatches)}")

# Count by Field
field_counts = {}
cat_counts = {}
for m in mismatches:
    fn = m["field_name"]
    c = m["category"]
    field_counts[fn] = field_counts.get(fn, 0) + 1
    cat_counts[c] = cat_counts.get(c, 0) + 1

print("\n--- TOP FAILURE FIELDS (Runs 1-3) ---")
for fn, cnt in sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"   - {fn:<24}: {cnt} mismatches ({cnt/3:.1f} avg per run)")

print("\n--- FAILURE CATEGORY BREAKDOWN ---")
for cat, cnt in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"   - {cat:<40}: {cnt} mismatches")
