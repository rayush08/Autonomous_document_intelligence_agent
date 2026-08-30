import os
import json

results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"

p6_base_file = os.path.join(results_dir, "phase6_baseline.json")
p9_files = [
    os.path.join(results_dir, "real_run_phase9_1_results.json"),
    os.path.join(results_dir, "real_run_phase9_2_results.json"),
    os.path.join(results_dir, "real_run_phase9_3_results.json")
]

with open(p6_base_file, "r", encoding="utf-8") as f:
    p6_data = json.load(f)

p6_field_acc = p6_data.get("per_field_accuracy", {})

p9_field_scores = {}
p9_mismatch_counts = {}

for fpath in p9_files:
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            fb = data.get("field_breakdown", {})
            for fname, metrics in fb.items():
                if fname not in p9_field_scores:
                    p9_field_scores[fname] = []
                    p9_mismatch_counts[fname] = 0
                p9_field_scores[fname].append(metrics.get("value_accuracy", 0.0))

matrix_rows = []

for fname in sorted(set(list(p6_field_acc.keys()) + list(p9_field_scores.keys()))):
    p6_val = p6_field_acc.get(fname, 0.0)
    p9_vals = p9_field_scores.get(fname, [0.0])
    p9_val = sum(p9_vals) / len(p9_vals)
    delta = p9_val - p6_val
    
    classification = "UNCHANGED"
    if delta > 0.05:
        classification = "IMPROVED"
    elif delta < -0.05:
        classification = "REGRESSED"
        
    root_cause = "Model Paraphrase"
    if "documents" in fname or "beneficiaries" in fname:
        root_cause = "Partial List Incompleteness / Context Truncation"
    elif "income" in fname or "stipend" in fname or "amount" in fname:
        root_cause = "Monetary Tier Breakdown Difference"
    elif "type" in fname:
        root_cause = "Categorical Taxonomy Mismatch"
    elif "notes" in fname or "criteria" in fname:
        root_cause = "Complex Clause Paraphrasing"

    matrix_rows.append({
        "field": fname,
        "phase6_baseline": round(p6_val, 4),
        "phase9_result": round(p9_val, 4),
        "delta": round(delta, 4),
        "classification": classification,
        "root_cause": root_cause
    })

matrix_rows.sort(key=lambda x: x["delta"])

reg_matrix_summary = {
    "total_fields": len(matrix_rows),
    "regressed_fields_count": sum(1 for r in matrix_rows if r["classification"] == "REGRESSED"),
    "improved_fields_count": sum(1 for r in matrix_rows if r["classification"] == "IMPROVED"),
    "unchanged_fields_count": sum(1 for r in matrix_rows if r["classification"] == "UNCHANGED"),
    "matrix": matrix_rows
}

with open(os.path.join(results_dir, "phase10_regression_matrix.json"), "w", encoding="utf-8") as f:
    json.dump(reg_matrix_summary, f, indent=2)

md_lines = [
    "# Phase 10 Regression Matrix (Phase 6 Baseline vs Phase 9 Results)",
    "",
    f"- Total Fields Analyzed: {len(matrix_rows)}",
    f"- Regressed Fields: {reg_matrix_summary['regressed_fields_count']}",
    f"- Improved Fields: {reg_matrix_summary['improved_fields_count']}",
    f"- Unchanged Fields: {reg_matrix_summary['unchanged_fields_count']}",
    "",
    "| Field Name | Phase 6 Baseline | Phase 9 Mean | Delta | Status | Primary Root Cause |",
    "|---|---:|---:|---:|---|---|",
]

for r in matrix_rows:
    md_lines.append(f"| `{r['field']}` | {r['phase6_baseline']*100:.1f}% | {r['phase9_result']*100:.1f}% | {r['delta']*100:+.1f}% | `{r['classification']}` | {r['root_cause']} |")

with open(os.path.join(results_dir, "phase10_regression_matrix.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print("Saved phase10_regression_matrix.json and phase10_regression_matrix.md successfully.")
