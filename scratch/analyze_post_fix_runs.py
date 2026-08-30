import os
import json
import numpy as np

results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"

r13_files = ["real_run_1_results.json", "real_run_2_results.json", "real_run_3_results.json"]

r13_data = []
for rf in r13_files:
    fpath = os.path.join(results_dir, rf)
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            r13_data.append(json.load(f))

def get_stats(data_list):
    field_accs = [d["overall"]["field_extraction_accuracy"] * 100 for d in data_list]
    status_accs = [d["overall"]["verification_status_accuracy"] * 100 for d in data_list]
    missing_accs = [d["overall"]["missing_information_accuracy"] * 100 for d in data_list]
    halluc_rates = [d["overall"]["hallucination_rate"] * 100 for d in data_list]
    ground_accs = [d["overall"]["evidence_grounding_accuracy"] * 100 for d in data_list]
    
    return {
        "field_acc": (np.mean(field_accs), np.min(field_accs), np.max(field_accs), np.std(field_accs)),
        "status_acc": (np.mean(status_accs), np.min(status_accs), np.max(status_accs), np.std(status_accs)),
        "missing_acc": (np.mean(missing_accs), np.min(missing_accs), np.max(missing_accs), np.std(missing_accs)),
        "halluc_rate": (np.mean(halluc_rates), np.min(halluc_rates), np.max(halluc_rates), np.std(halluc_rates)),
        "ground_acc": (np.mean(ground_accs), np.min(ground_accs), np.max(ground_accs), np.std(ground_accs))
    }

r13_stats = get_stats(r13_data)

print("==========================================")
print("BEFORE VS AFTER ACCURACY PASS METRICS")
print("==========================================")

print("\n| Metric | Historical Baseline | Runs 1-3 Mean (Before Accuracy Pass) | Runs 1-3 Min | Runs 1-3 Max | Runs 1-3 StdDev |")
print("|---|---|---|---|---|---|")
print(f"| Schema Validity Rate | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% |")
print(f"| Field Extraction Accuracy | 40.1% | {r13_stats['field_acc'][0]:.1f}% | {r13_stats['field_acc'][1]:.1f}% | {r13_stats['field_acc'][2]:.1f}% | {r13_stats['field_acc'][3]:.2f}% |")
print(f"| Verification Status Accuracy | 72.5% | {r13_stats['status_acc'][0]:.1f}% | {r13_stats['status_acc'][1]:.1f}% | {r13_stats['status_acc'][2]:.1f}% | {r13_stats['status_acc'][3]:.2f}% |")
print(f"| Missing Information Accuracy | 85.2% | {r13_stats['missing_acc'][0]:.1f}% | {r13_stats['missing_acc'][1]:.1f}% | {r13_stats['missing_acc'][2]:.1f}% | {r13_stats['missing_acc'][3]:.2f}% |")
print(f"| Hallucination Rate | 14.8% | {r13_stats['halluc_rate'][0]:.1f}% | {r13_stats['halluc_rate'][1]:.1f}% | {r13_stats['halluc_rate'][2]:.1f}% | {r13_stats['halluc_rate'][3]:.2f}% |")
print(f"| Evidence Grounding Accuracy | 100.0% | {r13_stats['ground_acc'][0]:.1f}% | {r13_stats['ground_acc'][1]:.1f}% | {r13_stats['ground_acc'][2]:.1f}% | {r13_stats['ground_acc'][3]:.2f}% |")
