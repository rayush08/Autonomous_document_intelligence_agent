# Verified Phase 4 Baseline Failure Report
Total Mismatches across Runs 1–3: `234` (averaging `78` per run across 170 evaluated fields per run)

## 1. Top Failure Fields (Baseline)
| Field Name | Total Mismatches | Per-Run Avg | Observed Error Pattern |
|---|---|---|---|
| `required_documents` | 21 | 7.0 | Partial list / Paraphrased text / Model omission |
| `scheme_type` | 18 | 6.0 | Partial list / Paraphrased text / Model omission |
| `benefit_amount` | 18 | 6.0 | Partial list / Paraphrased text / Model omission |
| `target_beneficiaries` | 16 | 5.3 | Partial list / Paraphrased text / Model omission |
| `education_level` | 16 | 5.3 | Partial list / Paraphrased text / Model omission |
| `benefit_type` | 16 | 5.3 | Partial list / Paraphrased text / Model omission |
| `academic_criteria` | 15 | 5.0 | Partial list / Paraphrased text / Model omission |
| `domicile_criteria` | 13 | 4.3 | Partial list / Paraphrased text / Model omission |
| `income_criteria` | 12 | 4.0 | Partial list / Paraphrased text / Model omission |
| `category_criteria` | 12 | 4.0 | Partial list / Paraphrased text / Model omission |

## 2. Sample Failure Entries Excerpt
| Run | Document ID | Domain | Field | Gold Status | Ext Status | Score | Mismatch Category | Probable Root Cause |
|---|---|---|---|---|---|---|---|---|
| Run 1 | `GOV-E-01` | government_schemes | `scheme_type` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `target_beneficiaries` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `education_level` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `age_criteria` | `not_found` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `income_criteria` | `verified` | `verified` | `0.53` | **D — Model paraphrased information but meaning is equivalent** | Model paraphrased text 'None' vs gold 'None' (Score: 0.53). |
| Run 1 | `GOV-E-01` | government_schemes | `academic_criteria` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `category_criteria` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `domicile_criteria` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `benefit_type` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `benefit_amount` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `application_method` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-01` | government_schemes | `required_documents` | `verified` | `verified` | `0.29` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.29). |
| Run 1 | `GOV-E-01` | government_schemes | `scheme_status` | `verified` | `not_found` | `0.00` | **A — Model omitted explicitly present information** | Model returned not_found for field present in source text (gold: None). |
| Run 1 | `GOV-E-02` | government_schemes | `scheme_name` | `verified` | `verified` | `0.62` | **D — Model paraphrased information but meaning is equivalent** | Model paraphrased text 'None' vs gold 'None' (Score: 0.62). |
| Run 1 | `GOV-E-02` | government_schemes | `implementing_authority` | `verified` | `verified` | `0.50` | **D — Model paraphrased information but meaning is equivalent** | Model paraphrased text 'None' vs gold 'None' (Score: 0.50). |
| Run 1 | `GOV-E-02` | government_schemes | `target_beneficiaries` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-02` | government_schemes | `education_level` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-02` | government_schemes | `age_criteria` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-02` | government_schemes | `academic_criteria` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-02` | government_schemes | `category_criteria` | `verified` | `verified` | `0.12` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.12). |
| Run 1 | `GOV-E-02` | government_schemes | `domicile_criteria` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-02` | government_schemes | `benefit_type` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-02` | government_schemes | `benefit_amount` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-02` | government_schemes | `application_url` | `verified` | `verified` | `0.00` | **C — Model extracted incorrect information** | Extracted value 'None' diverges from gold 'None' (Score: 0.00). |
| Run 1 | `GOV-E-02` | government_schemes | `required_documents` | `verified` | `not_found` | `0.00` | **A — Model omitted explicitly present information** | Model returned not_found for field present in source text (gold: None). |