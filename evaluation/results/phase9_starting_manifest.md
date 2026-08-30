# Phase 9 Starting State Manifest

## 1. Environment & Architecture Configuration

- **Git Commit Hash**: `bcdbd37`
- **Branch**: `main`
- **Benchmark Dataset**: 10 Gold Documents (GOV-E-01, GOV-E-02, GOV-E-03, GOV-E-04, GOV-M-01, GOV-M-02, GOV-M-03, OPP-E-01, OPP-E-02, OPP-M-01)
- **Model Discovery Mechanism**: `GeminiLLMClient.create_auto_discovered_client`
- **Grouped Extraction**: Active (`GOVERNMENT_SCHEME_GROUPS` / `OPPORTUNITY_GROUPS`)
- **Request Upper Bound ($N_{max}$)**: 108 HTTP requests max

## 2. Frozen Baseline Metrics (Historical Comparison Baseline Only)

| Metric | Frozen Baseline Value |
|---|---:|
| Schema Validity Rate | 100.00% |
| Field Extraction Accuracy | 53.49% |
| Verification Status Accuracy | 85.03% |
| Missing Information Accuracy | 83.95% |
| Hallucination Rate | 16.05% |
| Evidence Grounding Accuracy | 100.00% |