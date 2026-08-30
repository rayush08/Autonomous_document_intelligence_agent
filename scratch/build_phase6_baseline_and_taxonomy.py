import os
import json
import numpy as np

results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"

files = [
    ("Phase 5 Run 1", os.path.join(results_dir, "real_run_phase5_1_results.json")),
    ("Phase 5 Run 2", os.path.join(results_dir, "real_run_phase5_2_results.json")),
    ("Phase 5 Run 3", os.path.join(results_dir, "real_run_phase5_3_results.json"))
]

run_metrics = []
doc_scores = {}
field_scores = {}
all_failures = []

def classify_mismatch(field_name, gold_val, ext_val, gold_stat, ext_stat, doc_id):
    """Classify a field mismatch into exactly one of 12 primary taxonomy categories."""
    if gold_val is not None and ext_val is None:
        return "LIST_INCOMPLETENESS" if field_name in ["required_documents", "target_beneficiaries", "category_criteria"] else "PARTIAL_EXTRACTION"
    if gold_val is None and ext_val is not None:
        return "UNSUPPORTED_OR_HALLUCINATED_VALUE"
    if gold_stat != ext_stat:
        return "STATUS_CLASSIFICATION_ERROR"
    
    g_str = str(gold_val).lower()
    e_str = str(ext_val).lower()
    
    if field_name in ["scheme_type", "opportunity_type", "benefit_type"]:
        return "TAXONOMY_OR_CATEGORY_MISMATCH"
    if any(symbol in g_str or symbol in e_str for symbol in ["₹", "rs", "inr", "$", "chf"]):
        return "NUMERIC_NORMALIZATION_ERROR"
    if any(unit in g_str or unit in e_str for unit in ["per annum", "per year", "month", "annual", "percentage", "%"]):
        return "UNIT_OR_FORMAT_NORMALIZATION_ERROR"
    if len(e_str) > 0 and (g_str in e_str or e_str in g_str):
        return "SEMANTIC_PARAPHRASE_EQUIVALENCE"
    
    return "TRUE_EXTRACTION_ERROR"

for label, fpath in files:
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            overall = data.get("overall", {})
            run_metrics.append(overall)
            
            docs = data.get("document_results", {})
            for doc_id, doc_res in docs.items():
                if doc_id not in doc_scores:
                    doc_scores[doc_id] = []
                doc_scores[doc_id].append(doc_res.get("value_accuracy", 0.0))
                
                f_evals = doc_res.get("field_evaluations", {})
                for fname, f_info in f_evals.items():
                    if fname not in field_scores:
                        field_scores[fname] = []
                    field_scores[fname].append(f_info.get("value_score", 0.0))
                    
                    if not f_info.get("value_match", True) or not f_info.get("status_match", True):
                        cat = classify_mismatch(
                            fname,
                            f_info.get("gold_value"),
                            f_info.get("extracted_value"),
                            f_info.get("gold_status"),
                            f_info.get("extracted_status"),
                            doc_id
                        )
                        all_failures.append({
                            "run_id": label,
                            "document_id": doc_id,
                            "field": fname,
                            "expected_value": f_info.get("gold_value"),
                            "predicted_value": f_info.get("extracted_value"),
                            "expected_status": f_info.get("gold_status"),
                            "predicted_status": f_info.get("extracted_status"),
                            "failure_category": cat,
                            "explanation": f"Field '{fname}' mismatch in {doc_id} under {cat}",
                            "recommended_action": f"Optimize {cat.lower()} handling for field '{fname}'"
                        })

# Calculate Phase 6 Baseline Metrics
keys = ["schema_validity_rate", "field_extraction_accuracy", "verification_status_accuracy", "missing_information_accuracy", "hallucination_rate", "evidence_grounding_accuracy"]
baseline_summary = {}

for k in keys:
    vals = [m.get(k, 0.0) for m in run_metrics]
    baseline_summary[k] = {
        "Run 1": vals[0], "Run 2": vals[1], "Run 3": vals[2],
        "mean": float(np.mean(vals)), "min": float(np.min(vals)), "max": float(np.max(vals)), "std": float(np.std(vals))
    }

baseline_data = {
    "overall_metrics": baseline_summary,
    "per_document_accuracy": {d: float(np.mean(scores)) for d, scores in doc_scores.items()},
    "per_field_accuracy": {f: float(np.mean(scores)) for f, scores in field_scores.items()},
    "total_failures_recorded": len(all_failures)
}

# Save phase6_baseline.json
with open(os.path.join(results_dir, "phase6_baseline.json"), "w", encoding="utf-8") as f:
    json.dump(baseline_data, f, indent=2)

# Save phase6_baseline.md
md_baseline = [
    "# Phase 6 Frozen Baseline Performance Report",
    "",
    "## 1. Overall Baseline Metrics (Phase 5 Live Runs 1–3)",
    "",
    "| Metric | Run 1 | Run 2 | Run 3 | Mean | Min | Max | StdDev |",
    "|---|---:|---:|---:|---:|---:|---:|---:|",
]
for k in keys:
    b = baseline_summary[k]
    md_baseline.append(f"| `{k}` | {b['Run 1']*100:.2f}% | {b['Run 2']*100:.2f}% | {b['Run 3']*100:.2f}% | **{b['mean']*100:.2f}%** | {b['min']*100:.2f}% | {b['max']*100:.2f}% | {b['std']*100:.2f}% |")

with open(os.path.join(results_dir, "phase6_baseline.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_baseline))

# Failure Taxonomy Breakdown
cat_counts = {}
for fail in all_failures:
    c = fail["failure_category"]
    cat_counts[c] = cat_counts.get(c, 0) + 1

taxonomy_data = {
    "total_failures": len(all_failures),
    "category_counts": cat_counts,
    "failure_records": all_failures
}

with open(os.path.join(results_dir, "phase6_failure_taxonomy.json"), "w", encoding="utf-8") as f:
    json.dump(taxonomy_data, f, indent=2)

# Save phase6_failure_taxonomy.md
md_tax = [
    "# Phase 6 Failure Taxonomy Report",
    "",
    f"Total Failures Recorded Across 3 Live Runs: {len(all_failures)}",
    "",
    "## Category Distribution",
    "",
    "| Category | Mismatch Count | Percentage |",
    "|---|---:|---:|",
]
for cat, cnt in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
    pct = (cnt / len(all_failures)) * 100 if len(all_failures) > 0 else 0
    md_tax.append(f"| `{cat}` | {cnt} | {pct:.1f}% |")

with open(os.path.join(results_dir, "phase6_failure_taxonomy.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_tax))

print("Saved phase6_baseline.json, phase6_baseline.md, phase6_failure_taxonomy.json, phase6_failure_taxonomy.md successfully.")

