import os
import json
import sys

sys.path.insert(0, os.getcwd())

from src.evaluation.comparison import normalize_str, compare_values

results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"
run_files = ["real_run_1_results.json", "real_run_2_results.json", "real_run_3_results.json"]

out_json_path = os.path.join(results_dir, "phase4_baseline_failure_analysis.json")
out_md_path = os.path.join(results_dir, "phase4_baseline_failure_analysis.md")

failure_records = []

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
                    norm_exp = normalize_str(str(exp_val)) if exp_val is not None else ""
                    norm_ext = normalize_str(str(ext_val)) if ext_val is not None else ""
                    
                    # Fine-grained categorization based on prompt instructions
                    if exp_status == "not_found" and ext_status != "not_found" and ext_val is not None:
                        cat = "H — Unsupported / hallucinated extraction"
                        cause = f"Model asserted non-null claim '{ext_val}' for field absent in gold (gold status: not_found)."
                        is_det = "LLM non-deterministic generation"
                    elif ext_status == "not_found" and exp_status != "not_found":
                        cat = "A — Model omitted explicitly present information"
                        cause = f"Model returned not_found for field present in source text (gold value: {exp_val})."
                        is_det = "LLM generation omission"
                    elif isinstance(exp_val, list) and isinstance(ext_val, list) and len(ext_val) < len(exp_val):
                        cat = "B — Model extracted only partial information"
                        cause = f"Extracted partial list ({len(ext_val)} items: {ext_val}) when gold expects {len(exp_val)} items ({exp_val})."
                        is_det = "LLM partial list extraction"
                    elif not status_match and val_match:
                        cat = "G — Incorrect verification status"
                        cause = f"Value matched ({val_score:.2f}) but status mismatched (Exp: {exp_status} vs Ext: {ext_status})."
                        is_det = "Deterministic verification status assignment"
                    elif val_score >= 0.5 and val_score < 0.7:
                        cat = "D — Model paraphrased information but meaning is equivalent"
                        cause = f"Model paraphrased text '{ext_val}' vs gold '{exp_val}' (Score: {val_score:.2f})."
                        is_det = "Evaluator threshold string comparison"
                    else:
                        cat = "C — Model extracted incorrect information"
                        cause = f"Extracted value '{ext_val}' contradicts or diverges from gold value '{exp_val}' (Score: {val_score:.2f})."
                        is_det = "LLM model extraction inaccuracy"
                        
                    entry = {
                        "run_id": r_idx,
                        "document_id": doc_id,
                        "domain": domain,
                        "field_name": field_name,
                        "gold_value": exp_val,
                        "extracted_value": ext_val,
                        "gold_verification_status": exp_status,
                        "extracted_verification_status": ext_status,
                        "evidence": ext_ev,
                        "comparison_score": val_score,
                        "failure_category": cat,
                        "root_cause": cause,
                        "is_deterministic_or_llm": is_det
                    }
                    failure_records.append(entry)

print(f"Total Phase 4 Baseline Failure Records across 3 Runs: {len(failure_records)}")

# Write JSON report
with open(out_json_path, "w", encoding="utf-8") as f:
    json.dump(failure_records, f, indent=2, ensure_ascii=False)

# Write Markdown report
md_lines = [
    "# Phase 4 Baseline Field-Level Failure Analysis",
    f"Total Failure Records across Runs 1–3: `{len(failure_records)}` (averaging `{len(failure_records)//3}` mismatches per run)",
    "",
    "## 1. Failure Category Breakdown",
    ""
]

cat_counts = {}
field_counts = {}
for r in failure_records:
    cat_counts[r["failure_category"]] = cat_counts.get(r["failure_category"], 0) + 1
    field_counts[r["field_name"]] = field_counts.get(r["field_name"], 0) + 1

md_lines.append("| Category | Total Count | Per-Run Avg | Percentage |")
md_lines.append("|---|---|---|---|")
for cat, cnt in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
    md_lines.append(f"| **{cat}** | {cnt} | {cnt/3:.1f} | {cnt/len(failure_records)*100:.1f}% |")

md_lines.append("\n## 2. Top Failure-Prone Fields")
md_lines.append("| Field Name | Total Mismatches | Per-Run Avg | Primary Failure Mode |")
md_lines.append("|---|---|---|---|")
for fn, cnt in sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    md_lines.append(f"| `{fn}` | {cnt} | {cnt/3:.1f} | Partial list / Paraphrasing / Omission |")

md_lines.append("\n## 3. Complete Field Mismatch Table (Sample Excerpt across Runs 1–3)")
md_lines.append("| Run | Document ID | Domain | Field | Gold Status | Ext Status | Score | Failure Category | Root Cause |")
md_lines.append("|---|---|---|---|---|---|---|---|---|")

for r in failure_records[:30]:  # First 30 rows excerpt
    md_lines.append(
        f"| Run {r['run_id']} | `{r['document_id']}` | {r['domain']} | `{r['field_name']}` | "
        f"`{r['gold_verification_status']}` | `{r['extracted_verification_status']}` | `{r['comparison_score']:.2f}` | "
        f"**{r['failure_category']}** | {r['root_cause']} |"
    )

with open(out_md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(f"✅ Generated Phase 4 baseline failure analysis artifacts:")
print(f"   -> JSON: {out_json_path}")
print(f"   -> Markdown: {out_md_path}")
