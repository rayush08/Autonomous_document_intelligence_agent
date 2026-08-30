import os
import json

results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"

starting_manifest = {
  "phase": "Phase 9 Release Readiness",
  "git_commit": "bcdbd37",
  "branch": "main",
  "document_ids": [
    "GOV-E-01", "GOV-E-02", "GOV-E-03", "GOV-E-04",
    "GOV-M-01", "GOV-M-02", "GOV-M-03",
    "OPP-E-01", "OPP-E-02", "OPP-M-01"
  ],
  "total_documents": 10,
  "active_model_discovery": "GeminiLLMClient.create_auto_discovered_client",
  "extraction_architecture": "Evidence-first domain-grouped extraction with semantic retry & targeted recovery",
  "group_definitions": {
    "government_schemes": ["metadata", "eligibility", "benefits", "application"],
    "opportunities": ["metadata", "eligibility", "details"]
  },
  "retry_configuration": {
    "max_retries": 2,
    "max_model_failovers": 3
  },
  "semantic_completeness": "Active (FIELD_SEMANTIC_HINTS + partial list verification)",
  "evidence_verification": "Active (verify_evidence_against_document)",
  "evaluator_normalization": "Exact token numeric matching & symmetric currency/frequency canonicalization",
  "request_upper_bound": 108,
  "frozen_baseline": {
    "schema_validity_rate": 1.0,
    "field_extraction_accuracy": 0.5349,
    "verification_status_accuracy": 0.8503,
    "missing_information_accuracy": 0.8395,
    "hallucination_rate": 0.1605,
    "evidence_grounding_accuracy": 1.0
  }
}

with open(os.path.join(results_dir, "phase9_starting_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(starting_manifest, f, indent=2)

md_lines = [
    "# Phase 9 Starting State Manifest",
    "",
    "## 1. Environment & Architecture Configuration",
    "",
    f"- **Git Commit Hash**: `{starting_manifest['git_commit']}`",
    f"- **Branch**: `{starting_manifest['branch']}`",
    f"- **Benchmark Dataset**: 10 Gold Documents ({', '.join(starting_manifest['document_ids'])})",
    f"- **Model Discovery Mechanism**: `{starting_manifest['active_model_discovery']}`",
    f"- **Grouped Extraction**: Active (`GOVERNMENT_SCHEME_GROUPS` / `OPPORTUNITY_GROUPS`)",
    f"- **Request Upper Bound ($N_{{max}}$)**: {starting_manifest['request_upper_bound']} HTTP requests max",
    "",
    "## 2. Frozen Baseline Metrics (Historical Comparison Baseline Only)",
    "",
    "| Metric | Frozen Baseline Value |",
    "|---|---:|",
    f"| Schema Validity Rate | {starting_manifest['frozen_baseline']['schema_validity_rate']*100:.2f}% |",
    f"| Field Extraction Accuracy | {starting_manifest['frozen_baseline']['field_extraction_accuracy']*100:.2f}% |",
    f"| Verification Status Accuracy | {starting_manifest['frozen_baseline']['verification_status_accuracy']*100:.2f}% |",
    f"| Missing Information Accuracy | {starting_manifest['frozen_baseline']['missing_information_accuracy']*100:.2f}% |",
    f"| Hallucination Rate | {starting_manifest['frozen_baseline']['hallucination_rate']*100:.2f}% |",
    f"| Evidence Grounding Accuracy | {starting_manifest['frozen_baseline']['evidence_grounding_accuracy']*100:.2f}% |",
]

with open(os.path.join(results_dir, "phase9_starting_manifest.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print("Saved phase9_starting_manifest.json and phase9_starting_manifest.md successfully.")
