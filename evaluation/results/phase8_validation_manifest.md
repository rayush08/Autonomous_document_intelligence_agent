# Phase 8 Live Validation Manifest

## 1. Reproducible Validation Parameters

- **Git Commit Hash**: `bcdbd37`
- **Benchmark Dataset**: 10 Gold Documents (GOV-E-01, GOV-E-02, GOV-E-03, GOV-E-04, GOV-M-01, GOV-M-02, GOV-M-03, OPP-E-01, OPP-E-02, OPP-M-01)
- **Grouped Extraction**: Active (`GOVERNMENT_SCHEME_GROUPS` / `OPPORTUNITY_GROUPS`)
- **Maximum Retries**: 2
- **Request Upper Bound ($N_{max}$)**: 108 HTTP requests max
- **Evaluator Normalization**: Symmetric currency & frequency normalization with exact numeric token matching