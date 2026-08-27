# Source Ingestion, Validation, and Ground-Truth Pipeline

## Overview

This document outlines the pipeline architecture for ingesting, validating, and extracting grounded gold-standard JSON records for the Government Schemes domain (`GOV-E-01`..`04` and `GOV-M-01`..`03`) in compliance with `schemas/government_scheme.json` and `docs/dataset_strategy.md`.

---

## Pipeline Architecture

```
data/government_schemes/sources.csv  (Frozen Metadata)
                 │
                 ▼
          src/ingestion.py
      ┌──────────┴──────────┐
      ▼                     ▼
 (HTML Sources)       (PDF Sources)
  GOV-E-01..04         GOV-M-03
  GOV-M-01..02
      │                     │
      ▼                     ▼
Raw: *.html           Raw: GOV-M-03.pdf
Extracted:            Extracted:
*_extracted.json      GOV-M-03_pages.json
      │                     │
      └──────────┬──────────┘
                 ▼
    data/government_schemes/documents/validation_report.json
                 │
                 ▼
     src/generate_gold_data.py
                 │
                 ▼
        evaluation/gold/*.json (7 Ground-Truth Records)
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
src/validator.py    src/medium_integrity.py
 (Schema Check)      (Integrity Check)
```

---

## Core Components & Storage

1. **Source Metadata (`data/government_schemes/sources.csv`)**:
   - Frozen tracking registry containing 7 official government scheme sources (4 Easy, 3 Medium).

2. **Raw Document Store (`data/government_schemes/documents/`)**:
   - Raw HTML files (`*.html`) and raw binary PDF (`GOV-M-03.pdf`).
   - Clean extracted HTML text objects (`*_extracted.json`).
   - Page-structured PDF text objects with page boundaries (`GOV-M-03_pages.json`).
   - Validation report artifact (`validation_report.json`).

3. **Ground-Truth Store (`evaluation/gold/`)**:
   - 7 schema-grounded JSON files (`GOV-E-01.json` through `GOV-M-03.json`) formatted strictly according to `schemas/government_scheme.json`.
   - Every field includes an `EvidenceAwareField` container with `value`, `evidence` (text snippet + locator), `confidence`, and `verification_status`.
   - For `GOV-M-03` (PDF), evidence locators include explicit PDF `page` numbers (e.g. `page: 1`, `page: 4`, `page: 6`).
   - Genuinely absent fields evaluate to `value: null` with `verification_status: "not_found"`.

---

## How to Run the Pipeline

### 1. Ingest All Sources
Run the ingestion engine to fetch sources, detect formats, verify PDF magic bytes, extract page boundaries, and save validation reports:
```bash
python src/ingestion.py
```

### 2. Generate Ground-Truth Gold Records
Generate the 7 source-grounded gold standard JSON records:
```bash
python src/generate_gold_data.py
```

### 3. Run Schema Validation
Validate all gold standard records against `schemas/government_scheme.json`:
```bash
python src/validator.py
```

### 4. Run Medium-Difficulty Integrity Check
Verify structural complexity parameters for `GOV-M-01`, `GOV-M-02`, and `GOV-M-03`:
```bash
python src/medium_integrity.py
```

### 5. Run Automated Test Suite
Run the full deterministic test suite:
```bash
python -m unittest discover -s tests
```

