# Phase 4 Architecture Design: Evidence-First Grouped Extraction

## 1. Executive Summary & Architectural Motivation

The monolithic extraction approach extracts all 17 schema fields in a single prompt. Benchmark failure analysis revealed that extracting 17 fields simultaneously causes:
- **Attention Fragmentation**: Model truncates secondary eligibility conditions (`category_criteria`, `academic_criteria`).
- **Partial List Extraction**: Multi-item list fields (`required_documents`, `target_beneficiaries`) extract 1 item instead of complete lists.
- **Field Ambiguity**: Similar fields (`scheme_type` vs `benefit_type`) confuse the model when requested together in a generic prompt.

The **Evidence-First Grouped Extraction Architecture** decomposes target fields into 3–4 cohesive domain groups per document path. Each group prompt contains field-specific guidelines and receives filtered document chunks relevant to that group.

---

## 2. Domain-Aware Grouping Definitions

### Government Schemes (4 Field Groups)

#### GROUP A — Metadata & Identity
- **Fields**: `scheme_name`, `scheme_type`, `implementing_authority`, `scheme_status`
- **Focus**: High-precision extraction of official scheme titles, managing government bodies, and active/inactive status.

#### GROUP B — Beneficiary & Eligibility Criteria
- **Fields**: `target_beneficiaries`, `education_level`, `age_criteria`, `income_criteria`, `academic_criteria`, `category_criteria`, `domicile_criteria`
- **Focus**: Preserving exact numeric thresholds (income limits, percentages, CGPA), geographic restrictions (state vs district), and complete beneficiary categories (OBC, EBC, DNT).

#### GROUP C — Benefits
- **Fields**: `benefit_type`, `benefit_amount`
- **Focus**: Preserving multi-tier financial clauses, tuition waivers, maintenance allowances, frequency, and numeric commas (`₹50,000`).

#### GROUP D — Application & Requirements
- **Fields**: `application_method`, `application_url`, `required_documents`, `application_deadline`
- **Focus**: Complete list extraction for `required_documents` (Aadhaar, Income Certificate, Mark Sheet) and application deadlines.

---

### Opportunities (3 Field Groups)

#### GROUP A — Identity & Metadata
- **Fields**: `title`, `organization`, `opportunity_type`, `application_url`, `start_date`, `application_deadline`

#### GROUP B — Eligibility & Requirements
- **Fields**: `education_level`, `eligible_disciplines`, `skills_required`, `experience_required`, `eligibility_notes`, `required_documents`

#### GROUP C — Location & Funding
- **Fields**: `location`, `mode`, `duration`, `stipend_or_funding`

---

## 3. Evidence Filtering & Group Merging Strategy

1. **Chunk Filtering**: Each group filters document chunks by group-specific keywords (e.g. `["aadhaar", "certificate", "submit", "documents"]` for Group D).
2. **Sequential Group LLM Calls**: Extraction executes across groups (3–4 LLM calls per document path).
3. **Safe Schema Merging**: Extracted field objects from each group are merged into a complete JSON record adhering to the target schema.
4. **Targeted Recovery Fallback**: If group extraction returns `not_found` for high-impact fields (`benefit_amount`, `stipend_or_funding`, `required_documents`) despite affirmative text evidence, single-field targeted recovery executes.
