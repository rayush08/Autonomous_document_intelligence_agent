# Annotation Guidelines for Gold Benchmark Dataset

## 1. Overview
This document defines the manual annotation guidelines for creating ground-truth (gold) benchmark annotations for Phase 0 of the Autonomous Document Intelligence Agent. Annotators must follow these rules to ensure consistent, evidence-grounded, and schema-compliant ground truth data across both target domains.

---

## 2. Core Annotation Principles

1. **Explicit Support Only**: Annotate only information that is explicitly stated and directly supported by the source document.
2. **Zero Unjustified Inference**: Do not infer missing facts, assume unstated conditions, or extrapolate beyond what is explicitly written in the document text.
3. **Wording Preservation**: Preserve the original text phrasing and wording from the document whenever helpful for context and ground-truth verification.
4. **Explicit Missingness**: When a target schema field is not mentioned or cannot be found in the document, record `value: null` and `verification_status: "not_found"` with an empty `evidence: []` array.

---

## 3. Verification Status Definitions

Annotators must assign one of the following five verification statuses based on available document evidence:

- **verified**: A non-null extracted value is directly supported by sufficient source evidence.
- **unverified**: A non-null candidate value has supporting evidence but has not passed the required verification step or cannot yet be fully confirmed.
- **uncertain**: A non-null candidate value is supported by evidence, but its interpretation, scope, or applicability remains ambiguous.
- **rejected**: A candidate value was considered but determined to be unsupported, invalid, or inconsistent with the accepted extraction.
- **not_found**: No supported value was found in the document. The field must use value null.

---

## 4. Evidence Selection Rules

1. **Minimal Useful Snippet**: Select the smallest concise text excerpt from the document that fully supports the extracted claim value. Avoid copying entire pages or irrelevant surrounding paragraphs.
2. **Location Provenance**: Record location locator metadata whenever available:
   - `page`: Page number in multi-page PDF documents.
   - `section`: Section heading, clause title, or paragraph header.
   - `document_location`: Line number, table coordinate, or snippet location.
   - `url`: Direct web page URL or DOM selector for HTML sources.
   - `source_reference`: Document locator identifier.
3. **Multiple Evidence Items**: When a field value is supported by multiple distinct sections or clauses within the document, include multiple `EvidenceItem` entries in the `evidence` array.

---

## 5. Handling Ambiguity and Uncertainty

1. **Do Not Force Values**: Never force an ambiguous, vague, or incomplete text statement into a definitive non-null value if the source text is unclear.
2. **Use `uncertain` Status**: When evidence exists in the text but its interpretation, scope, or applicability is ambiguous, set `verification_status: "uncertain"`, ensure `confidence` reflects the annotator's assessed level of support (rather than using a fixed default), and record the supporting excerpt in `evidence`.

---

## 6. Handling Conflicting Information

1. **Preserve All Conflicting Evidence**: When a document contains conflicting statements (e.g., different deadline dates on page 1 vs. page 4), do not silently select one value while ignoring the other.
2. **Document Multi-Evidence Conflict**: Include evidence items for all conflicting statements within the `evidence` array and assign the appropriate `verification_status` (such as `"uncertain"` or `"rejected"`).

---

## 7. Field Value Normalization Rules

1. **Consistency without Meaning Loss**: Standardize structural formats (such as ISO dates `YYYY-MM-DD`, clean web URLs, or arrays of strings for lists) while preserving the core semantic meaning of the source text.
2. **Monetary Amounts and Limits**: Retain currency units and terms (e.g., `"INR 2,50,000 per annum"` or `"50,000 INR"`) so essential qualifications (such as "up to", "per annum", or "maximum") are not lost during extraction.
3. **List Attributes**: Map multi-item lists (such as `required_documents` or `eligible_disciplines`) into JSON arrays of strings (`["Item 1", "Item 2"]`).

---

## 8. Quality Review and Verification Process

Before finalizing any gold annotation file, the annotation must pass a 3-step manual quality review:
1. **Evidence Verification**: Re-read the raw document to verify that every non-null field value is directly backed by its cited `evidence.text` snippet and locator metadata.
2. **Schema Compliance**: Validate the annotation JSON against the corresponding JSON Schema (`schemas/government_scheme.json` or `schemas/opportunity.json`) using an automated JSON Schema Draft 2020-12 validator.
3. **Missingness & Status Consistency**: Verify that missing fields have `value: null` and `verification_status: "not_found"`, while verified fields have non-null values and non-empty `evidence` arrays.
