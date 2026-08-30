import os
import hashlib
import json

gold_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\gold"
results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"

gold_files = sorted([f for f in os.listdir(gold_dir) if f.endswith(".json")])

hashes = {}
for g in gold_files:
    fpath = os.path.join(gold_dir, g)
    with open(fpath, "rb") as f:
        hashes[g] = hashlib.sha256(f.read()).hexdigest()

manifest = {
    "phase": "Phase 14 Full Autonomous Closed-Loop Engineering Cycle",
    "starting_commit": "bcdbd37",
    "branch": "main",
    "total_gold_documents": len(gold_files),
    "gold_hashes": hashes,
    "frozen_phase6_baseline": {
        "schema_validity_rate": 1.0,
        "field_extraction_accuracy": 0.5349,
        "verification_status_accuracy": 0.8503,
        "missing_information_accuracy": 0.8395,
        "hallucination_rate": 0.1605,
        "evidence_grounding_accuracy": 1.0
    },
    "phase9_observed_regression": {
        "schema_validity_rate": 1.0,
        "field_extraction_accuracy": 0.4890,
        "verification_status_accuracy": 0.8363,
        "missing_information_accuracy": 0.7654,
        "hallucination_rate": 0.2346,
        "evidence_grounding_accuracy": 1.0
    },
    "test_suite_status": "171 repository unit & integration tests passing 100%"
}

with open(os.path.join(results_dir, "phase14_starting_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

md_lines = [
    "# Phase 14 Starting State Manifest",
    "",
    "## 1. Environment & Baseline Configuration",
    "",
    f"- **Starting Commit**: `{manifest['starting_commit']}`",
    f"- **Branch**: `{manifest['branch']}`",
    f"- **Total Gold Documents**: {manifest['total_gold_documents']}",
    f"- **Repository Test Suite**: {manifest['test_suite_status']}",
    "",
    "## 2. Frozen Baseline vs Observed Phase 9 Metrics",
    "",
    "| Metric | Frozen Phase 6 Baseline | Observed Phase 9 Mean | Delta |",
    "|---|---:|---:|---:|",
    f"| Schema Validity Rate | 100.00% | 100.00% | 0.00% |",
    f"| Field Extraction Accuracy | 53.49% | 48.90% | -4.59% |",
    f"| Verification Status Accuracy | 85.03% | 83.63% | -1.40% |",
    f"| Missing Information Accuracy | 83.95% | 76.54% | -7.41% |",
    f"| Hallucination Rate | 16.05% | 23.46% | +7.41% |",
    f"| Evidence Grounding Accuracy | 100.00% | 100.00% | 0.00% |",
]

with open(os.path.join(results_dir, "phase14_starting_manifest.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print("Saved phase14_starting_manifest.json and phase14_starting_manifest.md successfully.")
