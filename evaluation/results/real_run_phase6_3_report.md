# Phase 3 Benchmark Evaluation & Quality Report
### Mode: Real Gemini LLM Pipeline Evaluation

## 1. Executive Summary & Overall Metrics

- **Evaluation Mode**: `REAL GEMINI LLM PIPELINE EVALUATION`
- **Total Documents Evaluated**: `10`
- **Schema Validity Rate**: `100.0%`
- **Field Extraction Accuracy**: `47.3%`
- **Mean Field Value Score**: `0.5057`
- **Verification Status Accuracy**: `83.2%`
- **Missing Information Accuracy**: `77.8%`
- **Hallucination / Unsupported Claim Rate**: `22.2%`
- **Evidence Grounding Accuracy**: `100.0%`

---

## 2. Cross-Domain Generalization Breakdown

| Domain | Documents | Schema Validity | Value Accuracy | Status Accuracy | Missing Info Acc | Hallucination Rate | Mean Latency |
|---|---|---|---|---|---|---|---|
| **government_schemes** | 7 | 100.0% | 37.0% | 83.2% | 86.4% | 13.6% | 18.164s |
| **opportunities** | 3 | 100.0% | 72.9% | 83.3% | 40.0% | 60.0% | 8.052s |

---

## 3. Document-Level Execution Breakdown

| Document ID | Domain | Schema Valid | Attempts | Value Accuracy | Status Accuracy | Latency |
|---|---|---|---|---|---|---|
| `GOV-E-01` | government_schemes | ✅ YES | 1 | 23.5% | 88.2% | 11.139s |
| `GOV-E-02` | government_schemes | ✅ YES | 1 | 23.5% | 100.0% | 13.878s |
| `GOV-E-03` | government_schemes | ✅ YES | 1 | 47.1% | 82.3% | 17.217s |
| `GOV-E-04` | government_schemes | ✅ YES | 1 | 29.4% | 52.9% | 43.923s |
| `GOV-M-01` | government_schemes | ✅ YES | 1 | 35.3% | 70.6% | 14.555s |
| `GOV-M-02` | government_schemes | ✅ YES | 1 | 41.2% | 94.1% | 12.601s |
| `GOV-M-03` | government_schemes | ✅ YES | 1 | 58.8% | 94.1% | 13.837s |
| `OPP-E-01` | opportunities | ✅ YES | 1 | 75.0% | 87.5% | 9.014s |
| `OPP-E-02` | opportunities | ✅ YES | 1 | 68.8% | 81.2% | 7.901s |
| `OPP-M-01` | opportunities | ✅ YES | 1 | 75.0% | 81.2% | 7.240s |

---

## 4. Latency & Retry Statistics

- **Total Extraction Attempts**: `10`
- **Semantic Retries Executed**: `0`
- **Failures After Retry**: `0`
- **Mean Document Latency**: `15.130s`
- **Median Document Latency**: `13.219s`
- **Slowest Document**: `GOV-E-04 (43.923s)`

---

## 5. Field-Level Accuracy Breakdown

| Field Name | Status Accuracy | Value Accuracy | Mean Value Score |
|---|---|---|---|
| `academic_criteria` | 71.4% | 28.6% | 0.2857 |
| `age_criteria` | 85.7% | 71.4% | 0.7143 |
| `application_deadline` | 90.0% | 90.0% | 0.9000 |
| `application_method` | 85.7% | 42.9% | 0.3762 |
| `application_url` | 80.0% | 70.0% | 0.7000 |
| `benefit_amount` | 71.4% | 14.3% | 0.1429 |
| `benefit_type` | 100.0% | 14.3% | 0.1286 |
| `category_criteria` | 85.7% | 42.9% | 0.4133 |
| `domicile_criteria` | 71.4% | 28.6% | 0.2857 |
| `duration` | 100.0% | 100.0% | 0.9524 |
| `education_level` | 90.0% | 40.0% | 0.4367 |
| `eligibility_notes` | 66.7% | 0.0% | 0.0000 |
| `eligible_disciplines` | 33.3% | 0.0% | 0.1905 |
| `experience_required` | 33.3% | 33.3% | 0.3030 |
| `implementing_authority` | 85.7% | 57.1% | 0.6750 |
| `income_criteria` | 85.7% | 42.9% | 0.5042 |
| `location` | 100.0% | 100.0% | 1.0000 |
| `mode` | 100.0% | 100.0% | 1.0000 |
| `opportunity_type` | 100.0% | 100.0% | 1.0000 |
| `organization` | 100.0% | 100.0% | 1.0000 |
| `required_documents` | 80.0% | 20.0% | 0.2808 |
| `scheme_name` | 100.0% | 71.4% | 0.7379 |
| `scheme_status` | 42.9% | 57.1% | 0.5714 |
| `scheme_type` | 100.0% | 0.0% | 0.1571 |
| `skills_required` | 66.7% | 33.3% | 0.5556 |
| `start_date` | 66.7% | 100.0% | 1.0000 |
| `stipend_or_funding` | 100.0% | 33.3% | 0.7778 |
| `target_beneficiaries` | 100.0% | 0.0% | 0.0000 |
| `title` | 100.0% | 100.0% | 1.0000 |