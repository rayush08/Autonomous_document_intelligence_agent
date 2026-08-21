# Phase 0 Baseline Foundation Sign-Off

## 1. Baseline Declaration
This document records that the Phase 0 specification, schema, and dataset foundation artifacts for the Autonomous Document Intelligence Agent have successfully passed comprehensive consistency reviews and are officially **frozen** as the authoritative baseline for subsequent dataset curation, annotation, and system evaluation.

---

## 2. Frozen Baseline Artifacts

The following foundational artifacts are frozen as of Phase 0 completion:

| Artifact Path | Description | Status |
| :--- | :--- | :--- |
| [`scope.md`](file:///c:/Users/ayush/OneDrive/Documents/GitHub/autonomous_document_intelligence_agent/scope.md) | High-level project boundaries, agent responsibilities, non-goals, and domain scope definition. | **FROZEN** |
| [`schemas/government_scheme.json`](file:///c:/Users/ayush/OneDrive/Documents/GitHub/autonomous_document_intelligence_agent/schemas/government_scheme.json) | JSON Schema Draft 2020-12 target extraction schema for the Primary Domain (17 domain fields). | **FROZEN** |
| [`schemas/opportunity.json`](file:///c:/Users/ayush/OneDrive/Documents/GitHub/autonomous_document_intelligence_agent/schemas/opportunity.json) | JSON Schema Draft 2020-12 target extraction schema for the Secondary Domain (16 domain fields). | **FROZEN** |
| [`docs/dataset_strategy.md`](file:///c:/Users/ayush/OneDrive/Documents/GitHub/autonomous_document_intelligence_agent/docs/dataset_strategy.md) | 24-document dataset strategy, difficulty distribution (4 Easy, 5 Medium, 3 Hard per domain), and source rules. | **FROZEN** |
| [`evaluation/criteria.md`](file:///c:/Users/ayush/OneDrive/Documents/GitHub/autonomous_document_intelligence_agent/evaluation/criteria.md) | Benchmark evaluation dimensions (Correctness, Traceability, Schema Validity, Missingness, Generalization). | **FROZEN** |
| [`evaluation/annotation_guidelines.md`](file:///c:/Users/ayush/OneDrive/Documents/GitHub/autonomous_document_intelligence_agent/evaluation/annotation_guidelines.md) | Manual ground-truth annotation rules, evidence selection, status definitions, and quality review steps. | **FROZEN** |

---

## 3. Governance and Baseline Change Policy

To ensure rigour, auditability, and reproducibility during subsequent project phases:

1. **Adherence Requirement**: All subsequent document collection, metadata registration (`sources.csv`), and manual gold annotation creation must strictly adhere to the frozen definitions set forth in these artifacts.
2. **Controlled Modification Threshold**: Changes or revisions to the target JSON Schemas, annotation rules, or evaluation criteria should only be made if a concrete, unresolvable technical edge-case or schema flaw is discovered during live document curation.
3. **Explicit Revision Logging**: Any necessary modifications to frozen baseline artifacts must be documented explicitly with a recorded rationale and version bump, rather than silently modifying baseline files.
