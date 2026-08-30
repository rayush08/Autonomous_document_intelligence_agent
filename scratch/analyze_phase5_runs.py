import os
import json
import numpy as np

results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"

files = {
    "Run 1": os.path.join(results_dir, "real_run_phase5_1_results.json"),
    "Run 2": os.path.join(results_dir, "real_run_phase5_2_results.json"),
    "Run 3": os.path.join(results_dir, "real_run_phase5_3_results.json"),
}

run_data = {}

for label, fpath in files.items():
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            run_data[label] = data.get("overall", {})
    else:
        print(f"MISSING FILE: {fpath}")

print("=== REAL PHASE 5 LIVE BENCHMARK METRICS ===")
metrics_keys = [
    ("schema_validity_rate", "Schema Validity Rate"),
    ("field_extraction_accuracy", "Field Extraction Accuracy"),
    ("verification_status_accuracy", "Verification Status Accuracy"),
    ("missing_information_accuracy", "Missing Information Accuracy"),
    ("hallucination_rate", "Hallucination Rate"),
    ("evidence_grounding_accuracy", "Evidence Grounding Accuracy"),
]

parsed_metrics = {}

for key, name in metrics_keys:
    vals = [run_data[r].get(key, 0.0) for r in run_data]
    mean_val = float(np.mean(vals))
    min_val = float(np.min(vals))
    max_val = float(np.max(vals))
    std_val = float(np.std(vals))
    
    parsed_metrics[name] = {
        "Run 1": vals[0],
        "Run 2": vals[1],
        "Run 3": vals[2],
        "Mean": mean_val,
        "Min": min_val,
        "Max": max_val,
        "StdDev": std_val
    }
    
    print(f"\n{name}:")
    print(f"  Run 1: {vals[0]*100:.2f}% | Run 2: {vals[1]*100:.2f}% | Run 3: {vals[2]*100:.2f}%")
    print(f"  Mean:  {mean_val*100:.2f}% | Min: {min_val*100:.2f}% | Max: {max_val*100:.2f}% | StdDev: {std_val*100:.2f}%")

with open(os.path.join(results_dir, "phase5_live_baseline.json"), "w", encoding="utf-8") as f:
    json.dump(parsed_metrics, f, indent=2)

print("\n✅ Saved phase5_live_baseline.json")
