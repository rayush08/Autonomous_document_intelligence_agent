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
    "phase": "Phase 11 Autonomous Closed-Loop Regression Recovery",
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
    }
}

with open(os.path.join(results_dir, "phase11_starting_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

md_lines = [
    "# Phase 11 Starting State Manifest",
    "",
    "## 1. Baseline & Repository Configuration",
    "",
    f"- **Starting Commit**: `{manifest['starting_commit']}`",
    f"- **Branch**: `{manifest['branch']}`",
    f"- **Total Gold Documents**: {manifest['total_gold_documents']}",
    "",
    "## 2. Immutable Frozen Phase 6 Baseline vs Phase 9 Observed Regression",
    "",
    "| Metric | Frozen Phase 6 Baseline | Phase 9 Observed Mean | Delta |",
    "|---|---:|---:|---:|",
    f"| Schema Validity Rate | {manifest['frozen_phase6_baseline']['schema_validity_rate']*100:.2f}% | {manifest['phase9_observed_regression']['schema_validity_rate']*100:.2f}% | 0.00% |",
    f"| Field Extraction Accuracy | {manifest['frozen_phase6_baseline']['field_extraction_accuracy']*100:.2f}% | {manifest['phase9_observed_regression']['field_extraction_accuracy']*100:.2f}% | {manifest['phase9_observed_regression']['field_extraction_accuracy']*100 - manifest['frozen_phase6_baseline']['field_extraction_accuracy']*100:+.2f}% |",
    f"| Verification Status Accuracy | {manifest['frozen_phase6_baseline']['verification_status_accuracy']*100:.2f}% | {manifest['phase9_observed_regression']['verification_status_accuracy']*100:.2f}% | {manifest['phase9_observed_regression']['verification_status_accuracy']*100 - manifest['frozen_phase6_baseline']['verification_status_accuracy']*100:+.2f}% |",
    f"| Missing Information Accuracy | {manifest['frozen_phase6_baseline']['missing_information_accuracy']*100:.2f}% | {manifest['phase9_observed_regression']['missing_information_accuracy']*100:.2f}% | {manifest['phase9_observed_regression']['missing_information_accuracy']*100 - manifest['frozen_phase6_baseline']['missing_information_accuracy']*100:+.2f}% |",
    f"| Hallucination Rate | {manifest['frozen_phase6_baseline']['hallucination_rate']*100:.2f}% | {manifest['phase9_observed_regression']['hallucination_rate']*100:.2f}% | {manifest['phase9_observed_regression']['hallucination_rate']*100 - manifest['frozen_phase6_baseline']['hallucination_rate']*100:+.2f}% |",
    f"| Evidence Grounding Accuracy | {manifest['frozen_phase6_baseline']['evidence_grounding_accuracy']*100:.2f}% | {manifest['phase9_observed_regression']['evidence_grounding_accuracy']*100:.2f}% | 0.00% |",
]

with open(os.path.join(results_dir, "phase11_starting_manifest.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print("Saved phase11_starting_manifest.json and phase11_starting_manifest.md successfully.")
