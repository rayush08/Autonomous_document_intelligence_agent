import os
import json

results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"

manifest = {
  "phase": "Phase 8 Live Validation",
  "git_commit": "bcdbd37",
  "document_ids": [
    "GOV-E-01", "GOV-E-02", "GOV-E-03", "GOV-E-04",
    "GOV-M-01", "GOV-M-02", "GOV-M-03",
    "OPP-E-01", "OPP-E-02", "OPP-M-01"
  ],
  "total_documents": 10,
  "extraction_configuration": {
    "grouped_extraction_enabled": True,
    "max_retries": 2,
    "max_model_failovers": 3,
    "evidence_verification_enabled": True,
    "semantic_completeness_enabled": True,
    "request_upper_bound": 108
  },
  "evaluator_configuration": {
    "exact_numeric_token_matching": True,
    "currency_normalization": True,
    "frequency_unit_normalization": True
  }
}

with open(os.path.join(results_dir, "phase8_validation_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

md_lines = [
    "# Phase 8 Live Validation Manifest",
    "",
    "## 1. Reproducible Validation Parameters",
    "",
    f"- **Git Commit Hash**: `{manifest['git_commit']}`",
    f"- **Benchmark Dataset**: 10 Gold Documents ({', '.join(manifest['document_ids'])})",
    f"- **Grouped Extraction**: Active (`GOVERNMENT_SCHEME_GROUPS` / `OPPORTUNITY_GROUPS`)",
    f"- **Maximum Retries**: {manifest['extraction_configuration']['max_retries']}",
    f"- **Request Upper Bound ($N_{{max}}$)**: {manifest['extraction_configuration']['request_upper_bound']} HTTP requests max",
    f"- **Evaluator Normalization**: Symmetric currency & frequency normalization with exact numeric token matching"
]

with open(os.path.join(results_dir, "phase8_validation_manifest.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print("Saved phase8_validation_manifest.json and phase8_validation_manifest.md successfully.")
