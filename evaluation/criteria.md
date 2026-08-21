# Evaluation Criteria

## 1. Overview
This document defines the evaluation methodology, metric categories, and assessment criteria for the Autonomous Document Intelligence Agent. The evaluation framework measures extraction precision, evidence traceability, deterministic schema compliance, handling of missing data, and cross-domain generalization.

---

## 2. Core Evaluation Dimensions

### 2.1 Extraction Correctness
- **Gold Annotation Comparison**: System outputs are evaluated by comparing extracted JSON field values against manually annotated ground-truth gold annotations.
- **Field-Level Correctness**: Evaluates individual field extractions for semantic or exact match accuracy against gold ground truth.
- **Precision and Recall**: Precision measures the accuracy of non-null extractions (minimizing false positives), while recall measures the completeness of extracted fields relative to ground truth (minimizing false negatives).

### 2.2 Evidence Traceability
- **Supporting Evidence Citation**: Every accepted non-null extracted value must be accompanied by supporting text snippets and valid locator metadata (`page`, `section`, `document_location`, `url`, `source_reference`).
- **Source Correspondence**: Evaluates whether the cited text snippet actually exists within the original document and directly supports the extracted claim value.
- **Traceability Verification**: Extractions lacking verifiable source citations or containing mismatched evidence citations are flagged as ungrounded.

### 2.3 Schema Validity
- **Deterministic Schema Compliance**: All generated JSON outputs must conform strictly to the target JSON Schema (`schemas/government_scheme.json` or `schemas/opportunity.json`) using standard JSON Schema Draft 2020-12 validation.
- **Type and Constraint Integrity**: Validates data types (string, array of strings, null), numeric confidence bounds (0.0 to 1.0), allowed `verification_status` enum values, and `if`/`then` conditional rules.

### 2.4 Missing Information Handling
- **Explicit Missingness**: Information absent from the source document must be explicitly represented with `value: null` and `verification_status: "not_found"`.
- **Grounded Missingness Handling**: Unsupported or unmentioned attributes must not be accepted as extracted facts. Such information should be represented as `null` with `verification_status: "not_found"`, or marked `uncertain`/`unverified` when evidence exists but is insufficient for verification.
- **Uncertainty Recognition**: When evidence supports a candidate value but its interpretation or reliability remains ambiguous, the field should retain the supported non-null candidate value with `verification_status: "uncertain"` and appropriate evidence. If no candidate value is supported, the field should use `value: null` and `verification_status: "not_found"`.

### 2.5 Cross-Domain Generalization
- **Independent Domain Evaluation**: Extraction performance metrics are calculated and reported separately for the primary domain (*Government Welfare Schemes*) and the secondary domain (*Opportunities*).
- **Template Independence Assessment**: Comparative analysis determines whether extraction accuracy and verification quality remain consistent across domains or depend heavily on domain-specific heuristics.

---

## 3. Metric Definitions Summary

| Evaluation Dimension | Assessment Focus | Measurement Approach |
| :--- | :--- | :--- |
| **Extraction Correctness** | Value accuracy & completeness | Field-level precision, recall, and exact/semantic match against gold annotations. |
| **Evidence Traceability** | Provenance & citation validity | Verification of cited text snippets and locators against raw document text. |
| **Schema Validity** | Structural & type compliance | Automated validation against JSON Schema Draft 2020-12 rules. |
| **Missing Information Handling** | Hallucination prevention | Detection of unmentioned fields (`null`/`not_found`) without fabricated text. |
| **Cross-Domain Generalization** | Model domain adaptability | Disaggregated performance comparison across primary and secondary evaluation sets. |
