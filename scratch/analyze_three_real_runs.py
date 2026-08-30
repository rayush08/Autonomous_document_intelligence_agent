import os
import json
import numpy as np

results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"

run_files = ["real_run_1_results.json", "real_run_2_results.json", "real_run_3_results.json"]

runs_data = []
for rf in run_files:
    fpath = os.path.join(results_dir, rf)
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            runs_data.append(json.load(f))

print("==========================================")
print("THREE-RUN REAL BENCHMARK STATISTICAL AUDIT")
print("==========================================")

metrics_list = []
for idx, data in enumerate(runs_data, 1):
    overall = data.get("overall", {})
    metrics_list.append({
        "run_id": idx,
        "schema_validity": overall.get("schema_validity_rate", 0.0) * 100,
        "field_extraction_acc": overall.get("field_extraction_accuracy", 0.0) * 100,
        "status_acc": overall.get("verification_status_accuracy", 0.0) * 100,
        "missing_info_acc": overall.get("missing_information_accuracy", 0.0) * 100,
        "hallucination_rate": overall.get("hallucination_rate", 0.0) * 100,
        "grounding_acc": overall.get("evidence_grounding_accuracy", 0.0) * 100
    })

print(f"\nTotal Live Multi-Run Artifacts Found: {len(metrics_list)}")

print("\n--- PER-RUN METRICS BREAKDOWN ---")
print(f"| Run ID | Schema Valid | Field Extr Acc | Status Acc | Missing Info Acc | Hallucination Rate | Grounding Acc |")
print(f"|---|---|---|---|---|---|---|")
for m in metrics_list:
    print(f"| Run {m['run_id']} | {m['schema_validity']:.1f}% | {m['field_extraction_acc']:.1f}% | {m['status_acc']:.1f}% | {m['missing_info_acc']:.1f}% | {m['hallucination_rate']:.1f}% | {m['grounding_acc']:.1f}% |")

# Calculate Statistical Aggregation
field_accs = [m["field_extraction_acc"] for m in metrics_list]
status_accs = [m["status_acc"] for m in metrics_list]
missing_accs = [m["missing_info_acc"] for m in metrics_list]
halluc_rates = [m["hallucination_rate"] for m in metrics_list]

print("\n--- THREE-RUN STATISTICAL AGGREGATION ---")
print(f"Field Extraction Accuracy  -> Mean: {np.mean(field_accs):.2f}% | Min: {np.min(field_accs):.2f}% | Max: {np.max(field_accs):.2f}% | StdDev: {np.std(field_accs):.2f}%")
print(f"Verification Status Acc    -> Mean: {np.mean(status_accs):.2f}% | Min: {np.min(status_accs):.2f}% | Max: {np.max(status_accs):.2f}% | StdDev: {np.std(status_accs):.2f}%")
print(f"Missing Information Acc    -> Mean: {np.mean(missing_accs):.2f}% | Min: {np.min(missing_accs):.2f}% | Max: {np.max(missing_accs):.2f}% | StdDev: {np.std(missing_accs):.2f}%")
print(f"Hallucination Rate         -> Mean: {np.mean(halluc_rates):.2f}% | Min: {np.min(halluc_rates):.2f}% | Max: {np.max(halluc_rates):.2f}% | StdDev: {np.std(halluc_rates):.2f}%")

baseline_acc = 40.1
mean_acc = np.mean(field_accs)
print(f"\n[SUMMARY] ABSOLUTE ACCURACY IMPROVEMENT: Baseline {baseline_acc}% -> Post-Fix Mean {mean_acc:.1f}% (+{mean_acc - baseline_acc:.1f}% absolute improvement!)")
