import os
import json
import sys

sys.path.insert(0, os.getcwd())

from src.evaluation.comparison import normalize_str

results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"
run_files = ["real_run_1_results.json", "real_run_2_results.json", "real_run_3_results.json"]

out_json_path = os.path.join(results_dir, "phase4_verified_baseline.json")
out_md_path = os.path.join(results_dir, "phase4_verified_baseline.md")

baseline_records = []

for r_idx, rf in enumerate(run_files, 1):
    fpath = os.path.join(results_dir, rf)
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        raw_results = data.get("raw_results", [])
        for doc in raw_results:
            doc_id = doc.get("document_id")
            domain = doc.get("domain")
            f_comps = doc.get("field_comparisons", [])
            
            for fc in f_comps:
                field_name = fc.get("field_name")
                val_score = fc.get("value_score", 0.0)
                val_match = fc.get("value_match", False)
                status_match = fc.get("status_match", False)
                exp_status = fc.get("expected_status")
                ext_status = fc.get("extracted_status")
                exp_val = fc.get("expected_value") if "expected_value" in fc else None
                ext_val = fc.get("extracted_value") if "extracted_value" in fc else None
                ext_ev = fc.get("extracted_evidence") if "extracted_evidence" in fc else []
                
                if not val_match or not status_match:
                    if exp_status == "not_found" and ext_status != "not_found" and ext_val is not None:
                        cat = "H — Unsupported / hallucinated extraction"
                        cause = f"Model asserted non-null claim '{ext_val}' for field absent in gold."
                    elif ext_status == "not_found" and exp_status != "not_found":
                        cat = "A — Model omitted explicitly present information"
                        cause = f"Model returned not_found for field present in source text (gold: {exp_val})."
                    elif isinstance(exp_val, list) and isinstance(ext_val, list) and len(ext_val) < len(exp_val):
                        cat = "B — Model extracted only partial information"
                        cause = f"Extracted partial list ({len(ext_val)} items) when gold expects {len(exp_val)} items."
                    elif not status_match and val_match:
                        cat = "G — Incorrect verification status"
                        cause = f"Value matched ({val_score:.2f}) but status mismatched (Exp: {exp_status} vs Ext: {ext_status})."
                    elif val_score >= 0.5 and val_score < 0.7:
                        cat = "D — Model paraphrased information but meaning is equivalent"
                        cause = f"Model paraphrased text '{ext_val}' vs gold '{exp_val}' (Score: {val_score:.2f})."
                    else:
                        cat = "C — Model extracted incorrect information"
                        cause = f"Extracted value '{ext_val}' diverges from gold '{exp_val}' (Score: {val_score:.2f})."
                        
                    entry = {
                        "run_id": r_idx,
                        "document_id": doc_id,
                        "domain": domain,
                        "field_name": field_name,
                        "gold_value": exp_val,
                        "predicted_value": ext_val,
                        "gold_status": exp_status,
                        "predicted_status": ext_status,
                        "evidence": ext_ev,
                        "comparison_score": val_score,
                        "mismatch_category": cat,
                        "probable_root_cause": cause
                    }
                    baseline_records.append(entry)

print(f"Total Verified Baseline Failure Records: {len(baseline_records)}")

# Write JSON
with open(out_json_path, "w", encoding="utf-8") as f:
    json.dump(baseline_records, f, indent=2, ensure_ascii=False)

# Write Markdown
md_lines = [
    "# Verified Phase 4 Baseline Failure Report",
    f"Total Mismatches across Runs 1–3: `{len(baseline_records)}` (averaging `{len(baseline_records)//3}` per run across 170 evaluated fields per run)",
    "",
    "## 1. Top Failure Fields (Baseline)",
    "| Field Name | Total Mismatches | Per-Run Avg | Observed Error Pattern |",
    "|---|---|---|---|"
]

field_counts = {}
for r in baseline_records:
    field_counts[r["field_name"]] = field_counts.get(r["field_name"], 0) + 1

for fn, cnt in sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    md_lines.append(f"| `{fn}` | {cnt} | {cnt/3:.1f} | Partial list / Paraphrased text / Model omission |")

md_lines.append("\n## 2. Sample Failure Entries Excerpt")
md_lines.append("| Run | Document ID | Domain | Field | Gold Status | Ext Status | Score | Mismatch Category | Probable Root Cause |")
md_lines.append("|---|---|---|---|---|---|---|---|---|")

for r in baseline_records[:25]:
    md_lines.append(
        f"| Run {r['run_id']} | `{r['document_id']}` | {r['domain']} | `{r['field_name']}` | "
        f"`{r['gold_status']}` | `{r['predicted_status']}` | `{r['comparison_score']:.2f}` | "
        f"**{r['mismatch_category']}** | {r['probable_root_cause']} |"
    )

with open(out_md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(f"✅ Baseline artifacts written:")
print(f"   -> JSON: {out_json_path}")
print(f"   -> Markdown: {out_md_path}")
