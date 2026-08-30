# Phase 3 Benchmark Evaluation & Quality Report
### Mode: Real Gemini LLM Pipeline Evaluation

## 1. Executive Summary & Overall Metrics

- **Evaluation Mode**: `REAL GEMINI LLM PIPELINE EVALUATION`
- **Total Documents Evaluated**: `10`
- **Schema Validity Rate**: `100.0%`
- **Field Extraction Accuracy**: `49.7%`
- **Mean Field Value Score**: `0.5241`
- **Verification Status Accuracy**: `85.6%`
- **Missing Information Accuracy**: `77.8%`
- **Hallucination / Unsupported Claim Rate**: `22.2%`
- **Evidence Grounding Accuracy**: `100.0%`

---

## 2. Cross-Domain Generalization Breakdown

| Domain | Documents | Schema Validity | Value Accuracy | Status Accuracy | Missing Info Acc | Hallucination Rate | Mean Latency |
|---|---|---|---|---|---|---|---|
| **government_schemes** | 7 | 100.0% | 39.5% | 84.9% | 86.4% | 13.6% | 19.736s |
| **opportunities** | 3 | 100.0% | 75.0% | 87.5% | 40.0% | 60.0% | 7.971s |

---

## 3. Document-Level Execution Breakdown

| Document ID | Domain | Schema Valid | Attempts | Value Accuracy | Status Accuracy | Latency |
|---|---|---|---|---|---|---|
| `GOV-E-01` | government_schemes | ✅ YES | 1 | 29.4% | 88.2% | 18.515s |
| `GOV-E-02` | government_schemes | ✅ YES | 1 | 17.6% | 100.0% | 14.836s |
| `GOV-E-03` | government_schemes | ✅ YES | 1 | 41.2% | 88.2% | 18.855s |
| `GOV-E-04` | government_schemes | ✅ YES | 1 | 41.2% | 58.8% | 47.578s |
| `GOV-M-01` | government_schemes | ✅ YES | 1 | 47.1% | 70.6% | 10.444s |
| `GOV-M-02` | government_schemes | ✅ YES | 1 | 47.1% | 94.1% | 13.951s |
| `GOV-M-03` | government_schemes | ✅ YES | 1 | 52.9% | 94.1% | 13.969s |
| `OPP-E-01` | opportunities | ✅ YES | 1 | 75.0% | 93.8% | 7.967s |
| `OPP-E-02` | opportunities | ✅ YES | 1 | 68.8% | 81.2% | 7.852s |
| `OPP-M-01` | opportunities | ✅ YES | 1 | 81.2% | 87.5% | 8.096s |

---

## 4. Latency & Retry Statistics

- **Total Extraction Attempts**: `10`
- **Semantic Retries Executed**: `0`
- **Failures After Retry**: `0`
- **Mean Document Latency**: `16.206s`
- **Median Document Latency**: `13.960s`
- **Slowest Document**: `GOV-E-04 (47.578s)`

---

## 5. Field-Level Accuracy Breakdown

| Field Name | Status Accuracy | Value Accuracy | Mean Value Score |
|---|---|---|---|
| `academic_criteria` | 85.7% | 28.6% | 0.2857 |
| `age_criteria` | 85.7% | 71.4% | 0.7143 |
| `application_deadline` | 90.0% | 90.0% | 0.9000 |
| `application_method` | 85.7% | 28.6% | 0.4024 |
| `application_url` | 80.0% | 70.0% | 0.7000 |
| `benefit_amount` | 71.4% | 14.3% | 0.1286 |
| `benefit_type` | 100.0% | 14.3% | 0.1286 |
| `category_criteria` | 85.7% | 42.9% | 0.4087 |
| `domicile_criteria` | 85.7% | 42.9% | 0.4143 |
| `duration` | 100.0% | 66.7% | 0.6333 |
| `education_level` | 90.0% | 40.0% | 0.4700 |
| `eligibility_notes` | 66.7% | 0.0% | 0.0000 |
| `eligible_disciplines` | 66.7% | 33.3% | 0.5238 |
| `experience_required` | 33.3% | 33.3% | 0.3030 |
| `implementing_authority` | 100.0% | 71.4% | 0.7451 |
| `income_criteria` | 85.7% | 42.9% | 0.5042 |
| `location` | 100.0% | 100.0% | 1.0000 |
| `mode` | 100.0% | 100.0% | 1.0000 |
| `opportunity_type` | 100.0% | 100.0% | 1.0000 |
| `organization` | 100.0% | 100.0% | 1.0000 |
| `required_documents` | 90.0% | 30.0% | 0.3608 |
| `scheme_name` | 100.0% | 85.7% | 0.7539 |
| `scheme_status` | 42.9% | 71.4% | 0.7143 |
| `scheme_type` | 85.7% | 0.0% | 0.1571 |
| `skills_required` | 66.7% | 33.3% | 0.3333 |
| `start_date` | 66.7% | 100.0% | 1.0000 |
| `stipend_or_funding` | 100.0% | 33.3% | 0.7778 |
| `target_beneficiaries` | 100.0% | 0.0% | 0.0000 |
| `title` | 100.0% | 100.0% | 1.0000 |