# Phase 3 Benchmark Evaluation & Quality Report

## 1. Executive Summary & Overall Metrics

- **Total Documents Evaluated**: `10`
- **Schema Validity Rate**: `100.0%`
- **Field Extraction Accuracy**: `40.1%`
- **Mean Field Value Score**: `0.4012`
- **Verification Status Accuracy**: `40.1%`
- **Missing Information Accuracy**: `100.0%`
- **Hallucination / Unsupported Claim Rate**: `0.0%`
- **Evidence Grounding Accuracy**: `100.0%`

---

## 2. Cross-Domain Generalization Breakdown

| Domain | Documents | Schema Validity | Value Accuracy | Status Accuracy | Missing Info Acc | Hallucination Rate | Mean Latency |
|---|---|---|---|---|---|---|---|
| **government_schemes** | 7 | 100.0% | 52.1% | 52.1% | 100.0% | 0.0% | 0.006s |
| **opportunities** | 3 | 100.0% | 10.4% | 10.4% | 100.0% | 0.0% | 0.005s |

---

## 3. Document-Level Execution Breakdown

| Document ID | Domain | Schema Valid | Attempts | Value Accuracy | Status Accuracy | Latency |
|---|---|---|---|---|---|---|
| `GOV-E-01` | government_schemes | ✅ YES | 1 | 100.0% | 100.0% | 0.008s |
| `GOV-E-02` | government_schemes | ✅ YES | 1 | 11.8% | 11.8% | 0.005s |
| `GOV-E-03` | government_schemes | ✅ YES | 1 | 11.8% | 11.8% | 0.005s |
| `GOV-E-04` | government_schemes | ✅ YES | 1 | 23.5% | 23.5% | 0.004s |
| `GOV-M-01` | government_schemes | ✅ YES | 1 | 17.6% | 17.6% | 0.004s |
| `GOV-M-02` | government_schemes | ✅ YES | 1 | 100.0% | 100.0% | 0.008s |
| `GOV-M-03` | government_schemes | ✅ YES | 1 | 100.0% | 100.0% | 0.007s |
| `OPP-E-01` | opportunities | ✅ YES | 1 | 6.2% | 6.2% | 0.005s |
| `OPP-E-02` | opportunities | ✅ YES | 1 | 12.5% | 12.5% | 0.004s |
| `OPP-M-01` | opportunities | ✅ YES | 1 | 12.5% | 12.5% | 0.005s |

---

## 4. Latency & Retry Statistics

- **Total Extraction Attempts**: `10`
- **Semantic Retries Executed**: `0`
- **Failures After Retry**: `0`
- **Mean Document Latency**: `0.006s`
- **Median Document Latency**: `0.005s`
- **Slowest Document**: `GOV-M-02 (0.008s)`

---

## 5. Field-Level Accuracy Breakdown

| Field Name | Status Accuracy | Value Accuracy | Mean Value Score |
|---|---|---|---|
| `academic_criteria` | 57.1% | 57.1% | 0.5714 |
| `age_criteria` | 85.7% | 85.7% | 0.8571 |
| `application_deadline` | 70.0% | 70.0% | 0.7000 |
| `application_method` | 42.9% | 42.9% | 0.4286 |
| `application_url` | 30.0% | 30.0% | 0.3000 |
| `benefit_amount` | 42.9% | 42.9% | 0.4286 |
| `benefit_type` | 42.9% | 42.9% | 0.4286 |
| `category_criteria` | 42.9% | 42.9% | 0.4286 |
| `domicile_criteria` | 42.9% | 42.9% | 0.4286 |
| `duration` | 0.0% | 0.0% | 0.0000 |
| `education_level` | 40.0% | 40.0% | 0.4000 |
| `eligibility_notes` | 33.3% | 33.3% | 0.3333 |
| `eligible_disciplines` | 0.0% | 0.0% | 0.0000 |
| `experience_required` | 33.3% | 33.3% | 0.3333 |
| `implementing_authority` | 42.9% | 42.9% | 0.4286 |
| `income_criteria` | 71.4% | 71.4% | 0.7143 |
| `location` | 0.0% | 0.0% | 0.0000 |
| `mode` | 0.0% | 0.0% | 0.0000 |
| `opportunity_type` | 0.0% | 0.0% | 0.0000 |
| `organization` | 0.0% | 0.0% | 0.0000 |
| `required_documents` | 30.0% | 30.0% | 0.3000 |
| `scheme_name` | 42.9% | 42.9% | 0.4286 |
| `scheme_status` | 42.9% | 42.9% | 0.4286 |
| `scheme_type` | 42.9% | 42.9% | 0.4286 |
| `skills_required` | 66.7% | 66.7% | 0.6667 |
| `start_date` | 33.3% | 33.3% | 0.3333 |
| `stipend_or_funding` | 0.0% | 0.0% | 0.0000 |
| `target_beneficiaries` | 42.9% | 42.9% | 0.4286 |
| `title` | 0.0% | 0.0% | 0.0000 |