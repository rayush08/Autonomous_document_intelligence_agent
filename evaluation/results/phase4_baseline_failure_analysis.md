# Phase 4 Baseline Field-Level Failure Analysis
Total Failure Records across Runs 1–3: `234` (averaging `78` mismatches per run)

## 1. Failure Category Breakdown

| Category | Total Count | Per-Run Avg | Percentage |
|---|---|---|---|
| **C — Model extracted incorrect information** | 154 | 51.3 | 65.8% |
| **A — Model omitted explicitly present information** | 49 | 16.3 | 20.9% |
| **D — Model paraphrased information but meaning is equivalent** | 26 | 8.7 | 11.1% |
| **G — Incorrect verification status** | 5 | 1.7 | 2.1% |

## 2. Top Failure-Prone Fields
| Field Name | Total Mismatches | Per-Run Avg | Primary Failure Mode |
|---|---|---|---|
| `required_documents` | 21 | 7.0 | Partial list / Paraphrasing / Omission |
| `scheme_type` | 18 | 6.0 | Partial list / Paraphrasing / Omission |
| `benefit_amount` | 18 | 6.0 | Partial list / Paraphrasing / Omission |
| `target_beneficiaries` | 16 | 5.3 | Partial list / Paraphrasing / Omission |
| `education_level` | 16 | 5.3 | Partial list / Paraphrasing / Omission |
| `benefit_type` | 16 | 5.3 | Partial list / Paraphrasing / Omission |
| `academic_criteria` | 15 | 5.0 | Partial list / Paraphrasing / Omission |
| `domicile_criteria` | 13 | 4.3 | Partial list / Paraphrasing / Omission |
| `income_criteria` | 12 | 4.0 | Partial list / Paraphrasing / Omission |
| `category_criteria` | 12 | 4.0 | Partial list / Paraphrasing / Omission |

## 3. Complete Field Mismatch Table (Sample Excerpt across Runs 1–3)
| Run | Document ID | Domain | Field | Gold Status | Ext Status | Score | Failure Category | Root Cause |
|---|---|---|---|---|---|---|---|---|
| Run 1 | `GOV-E-01` | government_schemes | `scheme_type` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `target_beneficiaries` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `education_level` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `age_criteria` | `not_found` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `income_criteria` | `verified` | `verified` | `0.53` | **D — Model paraphrased information but meaning is equivalent** | Model paraphrased text 'None' vs gold 'None' (Score: 0.53). |
| Run 1 | `GOV-E-01` | government_schemes | `academic_criteria` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `category_criteria` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `domicile_criteria` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `benefit_type` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `benefit_amount` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `application_method` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `required_documents` | `verified` | `verified` | `0.29` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.29). |
| Run 1 | `GOV-E-01` | government_schemes | `scheme_status` | `verified` | `not_found` | `0.00` | **A — Model omitted explicitly present information** | Model returned not_found for field present in source text (gold value: None). |
| Run 1 | `GOV-E-02` | government_schemes | `scheme_name` | `verified` | `verified` | `0.62` | **D — Model paraphrased information but meaning is equivalent** | Model paraphrased text 'None' vs gold 'None' (Score: 0.62). |
| Run 1 | `GOV-E-02` | government_schemes | `implementing_authority` | `verified` | `verified` | `0.50` | **D — Model paraphrased information but meaning is equivalent** | Model paraphrased text 'None' vs gold 'None' (Score: 0.50). |
| Run 1 | `GOV-E-02` | government_schemes | `target_beneficiaries` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-02` | government_schemes | `education_level` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-02` | government_schemes | `age_criteria` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-02` | government_schemes | `academic_criteria` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-02` | government_schemes | `category_criteria` | `verified` | `verified` | `0.12` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.12). |
| Run 1 | `GOV-E-02` | government_schemes | `domicile_criteria` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-02` | government_schemes | `benefit_type` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-02` | government_schemes | `benefit_amount` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-02` | government_schemes | `application_url` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-02` | government_schemes | `required_documents` | `verified` | `not_found` | `0.00` | **A — Model omitted explicitly present information** | Model returned not_found for field present in source text (gold value: None). |
| Run 1 | `GOV-E-03` | government_schemes | `scheme_type` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-03` | government_schemes | `target_beneficiaries` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-03` | government_schemes | `education_level` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-03` | government_schemes | `income_criteria` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' contradicts or diverges from gold value 'None' (Score: 0.00). |
| Run 1 | `GOV-E-03` | government_schemes | `academic_criteria` | `verified` | `not_found` | `0.00` | **A — Model omitted explicitly present information** | Model returned not_found for field present in source text (gold value: None). |