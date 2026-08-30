# Phase 5 Architecture & Request Upper-Bound Baseline

## 1. Control Flow Parameters

Inspection of `LLMExtractor.extract()` (`src/llm/llm_extractor.py`) and `FIELD_SEMANTIC_HINTS` (`src/llm/semantic_completeness.py`) establishes the following control flow parameters:

- **Field Groups ($G$)**:
  - Government Schemes ($G = 4$ groups: `metadata`, `eligibility`, `benefits`, `application`)
  - Opportunities ($G = 3$ groups: `metadata`, `eligibility`, `details`)
  - $G_{\text{max}} = 4$ field groups per document path.
- **Maximum Semantic Attempts ($S$)**:
  - `max_retries = 2` $\rightarrow$ $S = 3$ semantic extraction attempts per group.
- **Targeted Recovery Calls ($F_{\text{recoverable}}$)**:
  - Executed **inside each semantic attempt loop** when `validate_semantic_completeness()` detects missing fields with affirmative text evidence.
  - $F_{\text{recoverable}} = 3$ targeted recovery calls per attempt (`benefit_amount`, `stipend_or_funding`, `required_documents`).
- **Maximum Transient HTTP Retries ($T$)**:
  - `max_transient_retries = 2` $\rightarrow$ $T = 3$ HTTP attempts per candidate model call.
- **Maximum Candidate Model Failovers ($M_{\text{failovers}}$)**:
  - `max_model_failovers = 3` $\rightarrow$ trying up to 4 candidate models (`model-1`, `model-2`, `model-3`, `model-4`).

---

## 2. Mathematical Request Bound Derivation

$$\text{Total Max LLM Calls} = S \times (G + F_{\text{recoverable}})$$

$$N_{\text{max}} = S \times (G + F_{\text{recoverable}}) \times T \times (1 + M_{\text{failovers}})$$

### Parameter Calculation:
$$\text{Total Max LLM Calls} = 3 \times (4 + 3) = 3 \times 7 = 21 \text{ LLM calls per document path}$$

$$N_{\text{max}} = 21 \times 3 \times (1 + 3) = 21 \times 12 = 252 \text{ maximum HTTP requests per document}$$

- **Normal Path Cost**: 3–4 HTTP calls per document path.
- **Worst-Case Infrastructure Outage Cost**: 252 HTTP requests max.
