# Phase 3 Benchmark Evaluation & Quality Report
### Mode: Real Gemini LLM Pipeline Evaluation

## 1. Executive Summary & Overall Metrics

- **Evaluation Mode**: `REAL GEMINI LLM PIPELINE EVALUATION`
- **Total Documents Evaluated**: `10`
- **Schema Validity Rate**: `100.0%`
- **Field Extraction Accuracy**: `40.1%`
- **Mean Field Value Score**: `0.4289`
- **Verification Status Accuracy**: `72.5%`
- **Missing Information Accuracy**: `85.2%`
- **Hallucination / Unsupported Claim Rate**: `14.8%`
- **Evidence Grounding Accuracy**: `100.0%`

---

## 2. Cross-Domain Generalization Breakdown

| Domain | Documents | Schema Validity | Value Accuracy | Status Accuracy | Missing Info Acc | Hallucination Rate | Mean Latency |
|---|---|---|---|---|---|---|---|
| **government_schemes** | 7 | 100.0% | 42.0% | 84.9% | 81.8% | 18.2% | 7.334s |
| **opportunities** | 3 | 100.0% | 35.4% | 41.7% | 100.0% | 0.0% | 6.982s |

---

## 3. Document-Level Execution Breakdown

| Document ID | Domain | Schema Valid | Attempts | Value Accuracy | Status Accuracy | Latency |
|---|---|---|---|---|---|---|
| `GOV-E-01` | government_schemes | ✅ YES | 1 | 29.4% | 94.1% | 6.449s |
| `GOV-E-02` | government_schemes | ✅ YES | 1 | 29.4% | 76.5% | 9.900s |
| `GOV-E-03` | government_schemes | ✅ YES | 1 | 47.1% | 82.3% | 12.052s |
| `GOV-E-04` | government_schemes | ✅ YES | 1 | 35.3% | 70.6% | 4.328s |
| `GOV-M-01` | government_schemes | ✅ YES | 1 | 47.1% | 76.5% | 4.491s |
| `GOV-M-02` | government_schemes | ✅ YES | 1 | 52.9% | 100.0% | 6.696s |
| `GOV-M-03` | government_schemes | ✅ YES | 1 | 52.9% | 94.1% | 7.423s |
| `OPP-E-01` | opportunities | ✅ YES | 1 | 31.2% | 37.5% | 6.993s |
| `OPP-E-02` | opportunities | ✅ YES | 1 | 31.2% | 43.8% | 6.739s |
| `OPP-M-01` | opportunities | ✅ YES | 1 | 43.8% | 43.8% | 7.212s |

---

## 4. Latency & Retry Statistics

- **Total Extraction Attempts**: `10`
- **Semantic Retries Executed**: `0`
- **Failures After Retry**: `0`
- **Mean Document Latency**: `7.228s`
- **Median Document Latency**: `6.866s`
- **Slowest Document**: `GOV-E-03 (12.052s)`

---

## 5. Field-Level Accuracy Breakdown

| Field Name | Status Accuracy | Value Accuracy | Mean Value Score |
|---|---|---|---|
| `academic_criteria` | 71.4% | 28.6% | 0.2857 |
| `age_criteria` | 85.7% | 71.4% | 0.7143 |
| `application_deadline` | 80.0% | 80.0% | 0.8000 |
| `application_method` | 85.7% | 71.4% | 0.6224 |
| `application_url` | 90.0% | 70.0% | 0.7000 |
| `benefit_amount` | 71.4% | 14.3% | 0.1762 |
| `benefit_type` | 100.0% | 14.3% | 0.1714 |
| `category_criteria` | 85.7% | 42.9% | 0.3929 |
| `domicile_criteria` | 71.4% | 28.6% | 0.2714 |
| `duration` | 0.0% | 0.0% | 0.0000 |
| `education_level` | 90.0% | 40.0% | 0.4467 |
| `eligibility_notes` | 33.3% | 33.3% | 0.3333 |
| `eligible_disciplines` | 0.0% | 0.0% | 0.0000 |
| `experience_required` | 33.3% | 33.3% | 0.3333 |
| `implementing_authority` | 100.0% | 57.1% | 0.6810 |
| `income_criteria` | 85.7% | 42.9% | 0.5042 |
| `location` | 0.0% | 0.0% | 0.0000 |
| `mode` | 0.0% | 0.0% | 0.0000 |
| `opportunity_type` | 0.0% | 0.0% | 0.0000 |
| `organization` | 0.0% | 0.0% | 0.0000 |
| `required_documents` | 70.0% | 30.0% | 0.3601 |
| `scheme_name` | 100.0% | 71.4% | 0.8687 |
| `scheme_status` | 85.7% | 85.7% | 0.8571 |
| `scheme_type` | 100.0% | 14.3% | 0.2143 |
| `skills_required` | 66.7% | 66.7% | 0.6667 |
| `start_date` | 33.3% | 33.3% | 0.3333 |
| `stipend_or_funding` | 100.0% | 33.3% | 0.7778 |
| `target_beneficiaries` | 100.0% | 14.3% | 0.1286 |
| `title` | 0.0% | 0.0% | 0.0000 |