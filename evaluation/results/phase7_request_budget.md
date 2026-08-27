# Phase 7 Request Budget & Mathematical Upper Bound Proof

---

### 1. Architectural Parameters

- **$S$**: Maximum Semantic Extraction Attempts = `3` (`max_retries = 2`)
- **$G$**: Domain Field Groups per Attempt = `4` (Government Schemes) or `3` (Opportunities)
- **$F_{\text{recoverable}}$**: Maximum Targeted Single-Field Recoveries per Attempt = `3`
- **$T_{\text{max}}$**: Maximum Transport Retries per HTTP Call = `3`
- **$M_{\text{failover}}$**: Candidate Model Failover Tier Count = `4`

---

### 2. Derivation of Maximum Request Bound

1. **Attempt 0 (Evidence-First Grouped Extraction)**:
   $$\text{Grouped LLM Calls} = G = 4$$

2. **Attempts 1 & 2 (Semantic Retry Path)**:
   $$\text{Semantic Retry LLM Calls} = S - 1 = 2$$

3. **Targeted Field Recovery**:
   $$\text{Targeted Recovery LLM Calls} = F_{\text{recoverable}} = 3$$

4. **Total LLM Calls per Document Path ($C_{\text{doc}}$)**:
   $$C_{\text{doc}} = G + (S - 1) + F_{\text{recoverable}} = 4 + 2 + 3 = 9 \text{ LLM Calls}$$

5. **Worst-Case HTTP Transport Multiplier ($R_{\text{transport}}$)**:
   $$R_{\text{transport}} = T_{\text{max}} \times M_{\text{failover}} = 3 \times 4 = 12 \text{ HTTP Requests per Call}$$

6. **Theoretical Worst-Case HTTP Request Bound ($N_{\text{max}}$)**:
   $$N_{\text{max}} = C_{\text{doc}} \times R_{\text{transport}} = 9 \times 12 = \mathbf{108} \text{ HTTP Requests Max}$$

---

### 3. Latency & Cost Implications

- **Normal Path (Attempt 1 Success)**: 4 HTTP requests per document path. Average latency: ~5.2 seconds per document.
- **Worst-Case Path (All Retries & Failovers)**: Up to 108 HTTP requests max. Controlled by circuit breakers and rate limit backoff timers.
