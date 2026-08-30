# Phase 5 Dataset Adequacy Audit & Expansion Plan

## 1. Current Benchmark Dataset Limitations

The active evaluation benchmark contains **10 curated document cases**:
- **7 Government Welfare Scheme Documents**: `GOV-E-01`, `GOV-E-02`, `GOV-E-03`, `GOV-E-04`, `GOV-M-01`, `GOV-M-02`, `GOV-M-03`
- **3 Opportunity Documents**: `OPP-E-01`, `OPP-E-02`, `OPP-M-01`

While effective for controlled regression testing, 10 documents (and only 3 secondary-domain cases) are insufficient to claim production-scale generalization across all real-world document variations.

---

## 2. Proposed 15-Document Expansion Plan

To validate production robustness, the benchmark dataset should be expanded with 15 additional real-world document categories:

| Target Category | Document Identifier | Domain | Target Structure / Stress Factor |
|---|---|---|---|
| **Complex Eligibility Table** | `GOV-ADV-01` | Government | Multi-tier income & age bracket matrix |
| **Multi-Tier Benefits** | `GOV-ADV-02` | Government | Tiered stipend rates based on academic institution |
| **Conflicting Conditions** | `GOV-ADV-03` | Government | Overlapping state vs central eligibility restrictions |
| **Missing Fields Heavy** | `GOV-ADV-04` | Government | Partial policy document missing deadline & URL |
| **Long Multi-Page Document** | `GOV-ADV-05` | Government | 15-page complete PDF guideline document |
| **Research Opportunity** | `OPP-ADV-01` | Opportunity | Postdoctoral grant with lab funding & travel allowance |
| **Internship Program** | `OPP-ADV-02` | Opportunity | Corporate summer fellowship with stipend & housing |
| **Scholarship Listing** | `OPP-ADV-03` | Opportunity | International master's scholarship |
| **Noisy OCR PDF** | `GOV-ADV-06` | Government | Scanned document with formatting artifacts |
| **Deadline Heavy** | `OPP-ADV-04` | Opportunity | Multiple phased application deadlines |
| **Multi-Location Opportunity**| `OPP-ADV-05` | Opportunity | Remote / Hybrid / On-site multi-city options |
| **Multi-Category Eligibility**| `GOV-ADV-07` | Government | Complex SC/ST/OBC/EBC reservation sub-quotas |
| **Foreign Exchange Funding**| `OPP-ADV-06` | Opportunity | Stipends denominated in EUR / CHF / USD |
| **Portal Application Guidelines**| `GOV-ADV-08` | Government | Document checklist for online upload portal |
| **State Domicile Boundary** | `GOV-ADV-09` | Government | District vs taluka residence criteria |
