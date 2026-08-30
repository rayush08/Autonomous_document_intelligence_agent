# Phase 3 Benchmark Evaluation & Quality Report
### Mode: Real Gemini LLM Pipeline Evaluation

## 1. Executive Summary & Overall Metrics

- **Evaluation Mode**: `REAL GEMINI LLM PIPELINE EVALUATION`
- **Total Documents Evaluated**: `10`
- **Schema Validity Rate**: `100.0%`
- **Field Extraction Accuracy**: `47.9%`
- **Mean Field Value Score**: `0.4992`
- **Verification Status Accuracy**: `82.6%`
- **Missing Information Accuracy**: `74.1%`
- **Hallucination / Unsupported Claim Rate**: `25.9%`
- **Evidence Grounding Accuracy**: `100.0%`

---

## 2. Cross-Domain Generalization Breakdown

| Domain | Documents | Schema Validity | Value Accuracy | Status Accuracy | Missing Info Acc | Hallucination Rate | Mean Latency |
|---|---|---|---|---|---|---|---|
| **government_schemes** | 7 | 100.0% | 37.8% | 81.5% | 81.8% | 18.2% | 20.824s |
| **opportunities** | 3 | 100.0% | 72.9% | 85.4% | 40.0% | 60.0% | 7.406s |

---

## 3. Document-Level Execution Breakdown

| Document ID | Domain | Schema Valid | Attempts | Value Accuracy | Status Accuracy | Latency |
|---|---|---|---|---|---|---|
| `GOV-E-01` | government_schemes | ✅ YES | 1 | 29.4% | 88.2% | 18.322s |
| `GOV-E-02` | government_schemes | ✅ YES | 1 | 17.6% | 94.1% | 14.033s |
| `GOV-E-03` | government_schemes | ✅ YES | 1 | 41.2% | 76.5% | 11.835s |
| `GOV-E-04` | government_schemes | ✅ YES | 1 | 41.2% | 58.8% | 8.435s |
| `GOV-M-01` | government_schemes | ✅ YES | 1 | 29.4% | 64.7% | 8.573s |
| `GOV-M-02` | government_schemes | ✅ YES | 1 | 47.1% | 94.1% | 11.340s |
| `GOV-M-03` | government_schemes | ✅ YES | 1 | 58.8% | 94.1% | 73.228s |
| `OPP-E-01` | opportunities | ✅ YES | 1 | 68.8% | 87.5% | 8.414s |
| `OPP-E-02` | opportunities | ✅ YES | 1 | 68.8% | 81.2% | 6.601s |
| `OPP-M-01` | opportunities | ✅ YES | 1 | 81.2% | 87.5% | 7.202s |

---

## 4. Latency & Retry Statistics

- **Total Extraction Attempts**: `10`
- **Semantic Retries Executed**: `0`
- **Failures After Retry**: `0`
- **Mean Document Latency**: `16.798s`
- **Median Document Latency**: `9.956s`
- **Slowest Document**: `GOV-M-03 (73.228s)`

---

## 5. Field-Level Accuracy Breakdown

| Field Name | Status Accuracy | Value Accuracy | Mean Value Score |
|---|---|---|---|
| `academic_criteria` | 71.4% | 28.6% | 0.2857 |
| `age_criteria` | 85.7% | 71.4% | 0.7143 |
| `application_deadline` | 80.0% | 80.0% | 0.8000 |
| `application_method` | 85.7% | 42.9% | 0.3163 |
| `application_url` | 80.0% | 70.0% | 0.7000 |
| `benefit_amount` | 71.4% | 14.3% | 0.1286 |
| `benefit_type` | 100.0% | 14.3% | 0.1286 |
| `category_criteria` | 85.7% | 28.6% | 0.3418 |
| `domicile_criteria` | 85.7% | 42.9% | 0.4143 |
| `duration` | 100.0% | 66.7% | 0.6333 |
| `education_level` | 80.0% | 40.0% | 0.4033 |
| `eligibility_notes` | 66.7% | 0.0% | 0.0000 |
| `eligible_disciplines` | 33.3% | 0.0% | 0.1905 |
| `experience_required` | 33.3% | 33.3% | 0.3030 |
| `implementing_authority` | 100.0% | 85.7% | 0.7694 |
| `income_criteria` | 85.7% | 42.9% | 0.5042 |
| `location` | 100.0% | 100.0% | 1.0000 |
| `mode` | 100.0% | 100.0% | 1.0000 |
| `opportunity_type` | 100.0% | 100.0% | 1.0000 |
| `organization` | 100.0% | 100.0% | 1.0000 |
| `required_documents` | 80.0% | 30.0% | 0.3546 |
| `scheme_name` | 100.0% | 71.4% | 0.7379 |
| `scheme_status` | 42.9% | 57.1% | 0.5714 |
| `scheme_type` | 85.7% | 0.0% | 0.1571 |
| `skills_required` | 66.7% | 33.3% | 0.3333 |
| `start_date` | 66.7% | 100.0% | 1.0000 |
| `stipend_or_funding` | 100.0% | 33.3% | 0.7778 |
| `target_beneficiaries` | 100.0% | 0.0% | 0.0844 |
| `title` | 100.0% | 100.0% | 1.0000 |