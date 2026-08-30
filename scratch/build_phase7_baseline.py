import os
import json

results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"

p6_base_path = os.path.join(results_dir, "phase6_baseline.json")

with open(p6_base_path, "r", encoding="utf-8") as f:
    p6_data = json.load(f)

p7_baseline = {
    "status": "FROZEN_INHERITED_FROM_PHASE6",
    "description": "Immutable Phase 7 baseline metrics inherited directly from Phase 6 benchmark runs (real_run_phase5_1, real_run_phase5_2, real_run_phase5_3).",
    "metrics": p6_data.get("overall_metrics", {}),
    "per_document_accuracy": p6_data.get("per_document_accuracy", {}),
    "per_field_accuracy": p6_data.get("per_field_accuracy", {})
}

with open(os.path.join(results_dir, "phase7_baseline.json"), "w", encoding="utf-8") as f:
    json.dump(p7_baseline, f, indent=2)

md_lines = [
    "# Phase 7 Baseline Report (Inherited from Phase 6)",
    "",
    "## Immutable Benchmark Baseline (Live Gemini API Runs)",
    "",
    "| Metric | Mean | Min | Max | StdDev |",
    "|---|---:|---:|---:|---:|",
]

for k, b in p7_baseline["metrics"].items():
    md_lines.append(f"| `{k}` | **{b['mean']*100:.2f}%** | {b['min']*100:.2f}% | {b['max']*100:.2f}% | {b['std']*100:.2f}% |")

md_lines.extend([
    "",
    "## Per-Field Baseline Accuracy",
    "",
    "| Field Name | Baseline Value Accuracy |",
    "|---|---:|",
])

for field, acc in sorted(p7_baseline["per_field_accuracy"].items(), key=lambda x: x[1]):
    md_lines.append(f"| `{field}` | {acc*100:.1f}% |")

with open(os.path.join(results_dir, "phase7_baseline.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print("Saved phase7_baseline.json and phase7_baseline.md successfully.")
