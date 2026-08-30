# Phase 4 Request Complexity & Request Upper-Bound Analysis

## 1. Mathematical Request Bound Derivation

The Phase 4 Grouped Extraction Architecture decomposes monolithic 17-field document extractions into focused domain field groups ($G = 4$ groups for Government Schemes, $G = 3$ groups for Opportunities).

### Control Flow & Call Breakdown

1. **Normal Execution Path (Clean Single Pass)**:
   - For Government Scheme documents ($G = 4$ groups): 4 LLM calls per document path.
   - For Opportunity documents ($G = 3$ groups): 3 LLM calls per document path.
   - **Normal Path Total**: 3–4 HTTP requests per document.

2. **Semantic Retry Loop**:
   - Up to $S = \text{max\_retries} + 1 = 3$ semantic extraction attempts per group.
   - Max group extraction calls across semantic attempts = $G \times S = 4 \times 3 = 12$ primary LLM calls.

3. **Targeted Single-Field Recovery Path**:
   - Targeted single-field recovery triggers inside the semantic attempt loop when `validate_semantic_completeness()` detects missing high-impact fields (`benefit_amount`, `stipend_or_funding`, `required_documents`) with affirmative text evidence.
   - Up to $F_{\text{recoverable}} = 3$ targeted single-field recovery calls can execute per semantic attempt.
   - Across $S = 3$ semantic attempts, max targeted recovery calls = $F_{\text{recoverable}} \times S = 3 \times 3 = 9$ LLM calls.
   - Total LLM calls across primary extraction and recovery = $S \times (G + F_{\text{recoverable}}) = 3 \times (4 + 3) = 21$ LLM calls.

4. **Transport Retry & Candidate Model Failover Multiplier**:
   - Each LLM call attempts up to $T = \text{max\_transient\_retries} + 1 = 3$ transient HTTP attempts per candidate model.
   - Under infrastructure outages, candidate model failovers execute up to $M_{\text{failovers}} = 3$ times (trying up to 4 candidate models: `model-1`, `model-2`, `model-3`, `model-4`).
   - Worst-case transport multiplier per LLM call = $T \times (1 + M_{\text{failovers}}) = 3 \times (1 + 3) = 12$ HTTP requests.

---

## 2. Corrected Mathematical Upper-Bound Formula

$$N_{\text{max}} = S \times (G + F_{\text{recoverable}}) \times T \times (1 + M_{\text{failovers}})$$

### Parameter Definitions:
- $S$: Maximum semantic attempts ($S = 3$)
- $G$: Maximum field groups per document ($G = 4$)
- $F_{\text{recoverable}}$: Maximum targeted recovery calls per semantic attempt ($F_{\text{recoverable}} = 3$)
- $T$: Maximum transient HTTP attempts per model ($T = 3$)
- $M_{\text{failovers}}$: Maximum candidate model failovers ($M_{\text{failovers}} = 3$)

### Numerical Calculation:
$$N_{\text{max}} = 3 \times (4 + 3) \times 3 \times (1 + 3) = 3 \times 7 \times 12 = 252 \text{ maximum HTTP requests per document}$$

---

## 3. Request Complexity Comparison Across Architecture Versions

| Pipeline Architecture | Normal Path Requests | Semantic Max Requests | Theoretical Worst-Case HTTP Upper Bound | Primary Driver |
|---|---|---|---|---|
| **Phase 3 Monolithic Architecture** | 1 call / doc | 3 calls / doc | **108 HTTP calls** | 17-field single prompt |
| **Phase 4 Grouped Architecture** | 3–4 calls / doc | 12–21 calls / doc | **252 HTTP calls** | 4 Field Groups + 3 Single-Field Recovery Targets |

### Cost Control & Operational Efficiency:
Under normal operation without infrastructure outages or validation retries, the 3–4 HTTP calls per document path strike an optimal balance between attention density for complex fields and API efficiency without incurring 17 individual single-field API calls per document.
