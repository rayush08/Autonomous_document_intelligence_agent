# Phase 6 Engineering Improvement & Hardening Log

---

### 1. Fixes & Engineering Enhancements Applied

- **Evaluator Substring Bug Fix ([src/evaluation/comparison.py](file:///c:/Users/ayush/OneDrive/Documents/GitHub/autonomous_document_intelligence_agent/src/evaluation/comparison.py))**:
  - Corrected `compare_values` where substring matching was incorrectly assigning a 0.9 similarity score to unequal numeric tokens (e.g. `$600` vs `$6,000`).
  - Added tokenized numeric comparison logic enforcing exact word boundary equality for numeric tokens when present in expected and extracted values.

- **Grouped Extraction Integration ([src/llm/llm_extractor.py](file:///c:/Users/ayush/OneDrive/Documents/GitHub/autonomous_document_intelligence_agent/src/llm/llm_extractor.py))**:
  - Added `extract_grouped_fields()` inside `LLMExtractor` to execute evidence-first domain group prompts (`metadata`, `eligibility`, `benefits`, `application` for Government Schemes; `metadata`, `eligibility`, `details` for Opportunities).
  - Integrated domain group execution on primary extraction attempt.

- **Adversarial Regression Test Suite ([tests/test_phase6_accuracy_hardening.py](file:///c:/Users/ayush/OneDrive/Documents/GitHub/autonomous_document_intelligence_agent/tests/test_phase6_accuracy_hardening.py))**:
  - Created 6 test groups covering Paraphrases (Group A), Non-equivalent Similar Terms (Group B), Partial Lists (Group C), Numeric & Currency Normalization (Group D), Unsupported Claim Detection (Group E), and Gold Dataset Integrity (Group F). All 121 repository tests pass cleanly.

---

### 2. Gold Dataset Audit Summary

- Audited all failures in `SEMANTIC_PARAPHRASE_EQUIVALENCE`, `GOLD_STANDARD_AMBIGUITY`, `TAXONOMY_OR_CATEGORY_MISMATCH`, and `NUMERIC_NORMALIZATION_ERROR`.
- Verified that original gold ground truth fixtures (`GOV-E-01.json` through `OPP-M-01.json`) remain 100% compliant with source documents without artificial alteration.
