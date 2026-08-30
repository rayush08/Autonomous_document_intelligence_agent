# Phase 3 Benchmark Evaluation & Quality Report
### Mode: Real Gemini LLM Pipeline Evaluation

## 1. Executive Summary & Overall Metrics

- **Evaluation Mode**: `REAL GEMINI LLM PIPELINE EVALUATION`
- **Total Documents Evaluated**: `10`
- **Schema Validity Rate**: `100.0%`
- **Field Extraction Accuracy**: `54.5%`
- **Mean Field Value Score**: `0.5643`
- **Verification Status Accuracy**: `86.8%`
- **Missing Information Accuracy**: `81.5%`
- **Hallucination / Unsupported Claim Rate**: `18.5%`
- **Evidence Grounding Accuracy**: `100.0%`

---

## 2. Cross-Domain Generalization Breakdown

| Domain | Documents | Schema Validity | Value Accuracy | Status Accuracy | Missing Info Acc | Hallucination Rate | Mean Latency |
|---|---|---|---|---|---|---|---|
| **government_schemes** | 7 | 100.0% | 43.7% | 84.0% | 86.4% | 13.6% | 7.218s |
| **opportunities** | 3 | 100.0% | 81.2% | 93.8% | 60.0% | 40.0% | 4.911s |

---

## 3. Document-Level Execution Breakdown

| Document ID | Domain | Schema Valid | Attempts | Value Accuracy | Status Accuracy | Latency |
|---|---|---|---|---|---|---|
| `GOV-E-01` | government_schemes | ✅ YES | 1 | 29.4% | 94.1% | 6.738s |
| `GOV-E-02` | government_schemes | ✅ YES | 1 | 23.5% | 88.2% | 11.043s |
| `GOV-E-03` | government_schemes | ✅ YES | 1 | 47.1% | 88.2% | 10.493s |
| `GOV-E-04` | government_schemes | ✅ YES | 1 | 41.2% | 64.7% | 4.380s |
| `GOV-M-01` | government_schemes | ✅ YES | 1 | 47.1% | 64.7% | 4.577s |
| `GOV-M-02` | government_schemes | ✅ YES | 1 | 58.8% | 94.1% | 6.436s |
| `GOV-M-03` | government_schemes | ✅ YES | 1 | 58.8% | 94.1% | 6.858s |
| `OPP-E-01` | opportunities | ✅ YES | 1 | 81.2% | 93.8% | 4.745s |
| `OPP-E-02` | opportunities | ✅ YES | 1 | 68.8% | 87.5% | 5.125s |
| `OPP-M-01` | opportunities | ✅ YES | 1 | 93.8% | 100.0% | 4.862s |

---

## 4. Latency & Retry Statistics

- **Total Extraction Attempts**: `10`
- **Semantic Retries Executed**: `0`
- **Failures After Retry**: `0`
- **Mean Document Latency**: `6.526s`
- **Median Document Latency**: `5.781s`
- **Slowest Document**: `GOV-E-02 (11.043s)`

---

## 5. Field-Level Accuracy Breakdown

| Field Name | Status Accuracy | Value Accuracy | Mean Value Score |
|---|---|---|---|
| `academic_criteria` | 85.7% | 28.6% | 0.2857 |
| `age_criteria` | 85.7% | 71.4% | 0.7143 |
| `application_deadline` | 90.0% | 90.0% | 0.9000 |
| `application_method` | 85.7% | 57.1% | 0.5000 |
| `application_url` | 80.0% | 70.0% | 0.7000 |
| `benefit_amount` | 71.4% | 14.3% | 0.1429 |
| `benefit_type` | 100.0% | 28.6% | 0.2571 |
| `category_criteria` | 85.7% | 42.9% | 0.4107 |
| `domicile_criteria` | 85.7% | 42.9% | 0.4143 |
| `duration` | 100.0% | 100.0% | 0.9333 |
| `education_level` | 80.0% | 40.0% | 0.4267 |
| `eligibility_notes` | 66.7% | 0.0% | 0.0000 |
| `eligible_disciplines` | 100.0% | 100.0% | 1.0000 |
| `experience_required` | 33.3% | 33.3% | 0.3030 |
| `implementing_authority` | 100.0% | 71.4% | 0.7023 |
| `income_criteria` | 85.7% | 42.9% | 0.5042 |
| `location` | 100.0% | 100.0% | 1.0000 |
| `mode` | 100.0% | 100.0% | 1.0000 |
| `opportunity_type` | 100.0% | 100.0% | 1.0000 |
| `organization` | 100.0% | 100.0% | 1.0000 |
| `required_documents` | 60.0% | 30.0% | 0.3558 |
| `scheme_name` | 100.0% | 57.1% | 0.6986 |
| `scheme_status` | 71.4% | 85.7% | 0.8571 |
| `scheme_type` | 100.0% | 14.3% | 0.2143 |
| `skills_required` | 100.0% | 66.7% | 0.8889 |
| `start_date` | 100.0% | 66.7% | 0.6667 |
| `stipend_or_funding` | 100.0% | 33.3% | 0.7778 |
| `target_beneficiaries` | 100.0% | 28.6% | 0.2571 |
| `title` | 100.0% | 100.0% | 1.0000 |