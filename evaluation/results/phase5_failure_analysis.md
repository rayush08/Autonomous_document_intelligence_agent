# Phase 5 Failure & Mismatch Analysis Report

## 1. Top Failure-Prone Fields Across Fresh Live Phase 5 Runs

| Field Name | Value Accuracy | Status Accuracy | Failure Category / Root Cause |
|---|---:|---:|---|
| `eligibility_notes` | 0.0% | 66.7% | Model Paraphrasing / Schema Synonyms |
| `scheme_type` | 14.3% | 85.7% | Categorical Taxonomy Paraphrase |
| `target_beneficiaries` | 14.3% | 100.0% | Partial List Extraction |
| `benefit_amount` | 14.3% | 71.4% | Multi-Tier Range Parsing |
| `benefit_type` | 23.8% | 95.2% | Categorical Taxonomy Paraphrase |
| `academic_criteria` | 28.6% | 71.4% | Model Paraphrasing / Schema Synonyms |
| `domicile_criteria` | 28.6% | 71.4% | Model Paraphrasing / Schema Synonyms |
| `required_documents` | 30.0% | 63.3% | Partial List Extraction |
| `experience_required` | 33.3% | 33.3% | Model Paraphrasing / Schema Synonyms |
| `stipend_or_funding` | 33.3% | 100.0% | Model Paraphrasing / Schema Synonyms |

## 2. Root Cause & Architectural Audit Findings

- **Integration Gap Identified & Corrected**: `LLMExtractor.extract()` in `src/llm/llm_extractor.py` was calling `build_document_extraction_prompt()` (monolithic 17-field single prompt) instead of invoking `extract_grouped_fields()`. We implemented `extract_grouped_fields()` inside `LLMExtractor`, imported domain groups (`GOVERNMENT_SCHEME_GROUPS`, `OPPORTUNITY_GROUPS`), and integrated evidence-first group prompt execution into `LLMExtractor.extract()`. Unit tests added in `tests/test_grouped_extraction.py` (115/115 passing).
- **List Completeness & Paraphrase Discrepancies**: High-impact fields (`scheme_type`, `target_beneficiaries`, `income_criteria`, `required_documents`) account for the majority of mismatches due to model paraphrasing (e.g. `Central Sector Scheme` vs `Centrally Sponsored Scheme`) or gold standard list representation differences.