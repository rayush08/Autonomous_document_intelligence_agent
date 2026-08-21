# Dataset Curation Plan

## 1. Overview and Purpose
This document establishes the operational dataset curation plan for Phase 0 of the Autonomous Document Intelligence Agent. It defines abstract document slots across the primary domain (*Government Welfare & Scholarship Schemes*) and secondary domain (*Opportunities*). 

The curation plan ensures target structural diversity, layout variation, format balance (PDF, HTML, OCR candidates), and schema coverage across 24 planned document slots without inventing synthetic data or pre-populating fake document titles or URLs.

---

## 2. Document ID Convention

All document slots and acquired documents follow a standardized identifier naming scheme:

- **Primary Domain (Government Schemes)**: `GOV-[E/M/H]-XX`
- **Secondary Domain (Opportunities)**: `OPP-[E/M/H]-XX`

Where:
- `GOV` = Government Welfare and Scholarship Scheme domain
- `OPP` = Scholarship, Internship, Fellowship, Research Opportunity domain
- `E` = Easy difficulty
- `M` = Medium difficulty
- `H` = Hard difficulty
- `XX` = Sequential two-digit slot index (`01`, `02`, `03`, etc.)

---

## 3. Candidate Acceptance Checklist

Before a real-world document is acquired, registered in `sources.csv`, and included in the evaluation dataset, it must satisfy all 7 criteria in the Candidate Acceptance Checklist:

- [ ] **Authoritative First-Party Source**: The document originates from an official first-party website (government portal, university, research institute, or official organization/company domain). Third-party aggregators or blog summaries are rejected.
- [ ] **Recordable Source URL**: The exact live URL of the source document or HTML web page is available and documented.
- [ ] **Document Accessibility**: The raw file (PDF or HTML) can be downloaded or fetched cleanly without login paywalls or broken links.
- [ ] **Schema Mapping Sufficiency**: The document contains sufficient information to populate a meaningful subset of target schema fields.
- [ ] **Justified Difficulty Level**: The document's structural layout, visual complexity, and extraction challenges match its designated slot difficulty classification (`Easy`, `Medium`, or `Hard`).
- [ ] **Structural Non-Redundancy**: The document offers distinct layout, structural, or domain features rather than duplicating an existing document's structure unnecessarily.
- [ ] **Manual Inspection Sign-Off**: The candidate document has been manually inspected and approved prior to annotation.

---

## Slot Flexibility

Slot descriptions define desired structural characteristics and layout complexity rather than mandatory exact document topics. A slot may be filled by a different authoritative first-party document if it provides an equivalent or stronger structural challenge while preserving:
- the domain
- the intended difficulty level
- dataset diversity
- the required 12-document distribution per domain

Documents labeled as scanned/OCR candidates represent preferred target candidates rather than mandatory requirements. If a suitable authoritative scanned document cannot be obtained, the slot may be replaced by another genuinely hard document with complex layout, tables, distributed conditions, or comparable extraction challenges.

---

## 4. Primary Domain Curation Plan: Government Welfare and Scholarship Schemes

Total Primary Domain Slots: **12 Documents** (4 Easy, 5 Medium, 3 Hard)

### Easy Slots (4 Documents)

#### Slot GOV-E-01
- **Document ID**: `GOV-E-01`
- **Domain**: Government Welfare and Scholarship Schemes
- **Difficulty**: Easy
- **Desired Document Type**: Central Government Post-Matric Scholarship Guideline
- **Preferred Source Category**: Central Government Ministry / Department Official Portal
- **Expected Structural Challenge**: Clean digital text, standard single-column layout, direct field-value mappings.
- **Likely Schema Fields Covered**: `scheme_name`, `scheme_type`, `implementing_authority`, `education_level`, `benefit_type`, `application_method`.

#### Slot GOV-E-02
- **Document ID**: `GOV-E-02`
- **Domain**: Government Welfare and Scholarship Schemes
- **Difficulty**: Easy
- **Desired Document Type**: State Government Pre-Matric Scholarship Web Notification
- **Preferred Source Category**: State Government Department Web Page (HTML)
- **Expected Structural Challenge**: Standard web page DOM structure with clear section headings.
- **Likely Schema Fields Covered**: `scheme_name`, `target_beneficiaries`, `education_level`, `income_criteria`, `application_url`, `scheme_status`.

#### Slot GOV-E-03
- **Document ID**: `GOV-E-03`
- **Domain**: Government Welfare and Scholarship Schemes
- **Difficulty**: Easy
- **Desired Document Type**: Higher Education Financial Assistance Official Circular
- **Preferred Source Category**: Higher Education Department / Authority PDF
- **Expected Structural Challenge**: Short digital PDF with explicit key-value pairs and minimal formatting clutter.
- **Likely Schema Fields Covered**: `scheme_name`, `implementing_authority`, `academic_criteria`, `benefit_amount`, `application_deadline`.

#### Slot GOV-E-04
- **Document ID**: `GOV-E-04`
- **Domain**: Government Welfare and Scholarship Schemes
- **Difficulty**: Easy
- **Desired Document Type**: Social Welfare Department Financial Support Scheme Summary
- **Preferred Source Category**: State Social Welfare Portal Web Page (HTML)
- **Expected Structural Challenge**: Clean HTML page layout with structured bullet lists.
- **Likely Schema Fields Covered**: `scheme_name`, `scheme_type`, `category_criteria`, `domicile_criteria`, `required_documents`, `application_method`.

---

### Medium Slots (5 Documents)

#### Slot GOV-M-01
- **Document ID**: `GOV-M-01`
- **Domain**: Government Welfare and Scholarship Schemes
- **Difficulty**: Medium
- **Desired Document Type**: Multi-Page State Merit-cum-Means Scholarship Operational Rules
- **Preferred Source Category**: State Education Department PDF
- **Expected Structural Challenge**: Multi-page document requiring synthesis across sections, embedded income/academic eligibility tables.
- **Likely Schema Fields Covered**: `scheme_name`, `target_beneficiaries`, `income_criteria`, `academic_criteria`, `benefit_amount`, `required_documents`, `application_deadline`.

#### Slot GOV-M-02
- **Document ID**: `GOV-M-02`
- **Domain**: Government Welfare and Scholarship Schemes
- **Difficulty**: Medium
- **Desired Document Type**: Central Department Scheme Portal Page with Application Tables
- **Preferred Source Category**: Central Government Portal Web Page (HTML)
- **Expected Structural Challenge**: Web DOM with nested HTML data tables, external links, and optional missing fields.
- **Likely Schema Fields Covered**: `scheme_name`, `implementing_authority`, `benefit_type`, `benefit_amount`, `application_url`, `required_documents`, `scheme_status`.

#### Slot GOV-M-03
- **Document ID**: `GOV-M-03`
- **Domain**: Government Welfare and Scholarship Schemes
- **Difficulty**: Medium
- **Desired Document Type**: Minorities Development Finance Corporation Scheme Guidelines
- **Preferred Source Category**: State Corporation / Board PDF
- **Expected Structural Challenge**: Distributed text across multiple pages with complex category reservation criteria.
- **Likely Schema Fields Covered**: `scheme_name`, `target_beneficiaries`, `age_criteria`, `category_criteria`, `domicile_criteria`, `application_method`, `required_documents`.

#### Slot GOV-M-04
- **Document ID**: `GOV-M-04`
- **Domain**: Government Welfare and Scholarship Schemes
- **Difficulty**: Medium
- **Desired Document Type**: National Fellowship & Scholarship Scheme Circular
- **Preferred Source Category**: National Education Council / Commission PDF
- **Expected Structural Challenge**: Multi-category eligibility rules requiring combining conditions from separate clauses.
- **Likely Schema Fields Covered**: `scheme_name`, `scheme_type`, `education_level`, `academic_criteria`, `category_criteria`, `benefit_amount`, `application_deadline`.

#### Slot GOV-M-05
- **Document ID**: `GOV-M-05`
- **Domain**: Government Welfare and Scholarship Schemes
- **Difficulty**: Medium
- **Desired Document Type**: Public Sector Welfare Scheme Web Page with Document Checklists
- **Preferred Source Category**: State Government Welfare Portal Web Page (HTML)
- **Expected Structural Challenge**: HTML page containing multi-item document checklists, web portal URLs, and application timelines.
- **Likely Schema Fields Covered**: `scheme_name`, `implementing_authority`, `target_beneficiaries`, `application_method`, `application_url`, `required_documents`, `application_deadline`, `scheme_status`.

---

### Hard Slots (3 Documents)

#### Slot GOV-H-01
- **Document ID**: `GOV-H-01`
- **Domain**: Government Welfare and Scholarship Schemes
- **Difficulty**: Hard
- **Desired Document Type**: Legacy State Government Welfare Scheme Guidelines Circular
- **Preferred Source Category**: Archived State Government Press / Gazette PDF (Scanned/OCR Candidate)
- **Expected Structural Challenge**: Image-based scanned document requiring OCR, non-standard layout artifacts, line noise, and fragmented text.
- **Likely Schema Fields Covered**: `scheme_name`, `implementing_authority`, `target_beneficiaries`, `income_criteria`, `category_criteria`, `benefit_amount`, `domicile_criteria`.

#### Slot GOV-H-02
- **Document ID**: `GOV-H-02`
- **Domain**: Government Welfare and Scholarship Schemes
- **Difficulty**: Hard
- **Desired Document Type**: Multi-Scheme Government Notification Circular with Mixed-Layout Tables
- **Preferred Source Category**: State Finance / Education Ministry PDF
- **Expected Structural Challenge**: Dense, table-heavy multi-column document with multi-hop eligibility conditions and nested multi-header tables.
- **Likely Schema Fields Covered**: `scheme_name`, `scheme_type`, `education_level`, `age_criteria`, `income_criteria`, `academic_criteria`, `benefit_type`, `benefit_amount`, `application_deadline`.

#### Slot GOV-H-03
- **Document ID**: `GOV-H-03`
- **Domain**: Government Welfare and Scholarship Schemes
- **Difficulty**: Hard
- **Desired Document Type**: Dense Government Policy Document with Distributed Amendments
- **Preferred Source Category**: Central/State Government Gazette / Policy Publication PDF
- **Expected Structural Challenge**: Distributed clauses, implicit rule dependencies, conditional eligibility exceptions, and multi-location evidence.
- **Likely Schema Fields Covered**: `scheme_name`, `implementing_authority`, `target_beneficiaries`, `education_level`, `category_criteria`, `domicile_criteria`, `benefit_amount`, `required_documents`, `scheme_status`.

---

## 5. Secondary Domain Curation Plan: Opportunities

Total Secondary Domain Slots: **12 Documents** (4 Easy, 5 Medium, 3 Hard)

### Easy Slots (4 Documents)

#### Slot OPP-E-01
- **Document ID**: `OPP-E-01`
- **Domain**: Opportunities
- **Difficulty**: Easy
- **Desired Document Type**: University Merit Scholarship Announcement Page
- **Preferred Source Category**: Official University Academic Portal Web Page (HTML)
- **Expected Structural Challenge**: Clean HTML page layout, single-tier hierarchy, direct field-value text blocks.
- **Likely Schema Fields Covered**: `title`, `organization`, `opportunity_type`, `education_level`, `stipend_or_funding`, `application_deadline`.

#### Slot OPP-E-02
- **Document ID**: `OPP-E-02`
- **Domain**: Opportunities
- **Difficulty**: Easy
- **Desired Document Type**: Research Institute Summer Internship Call for Applications
- **Preferred Source Category**: National Research Institute PDF Notice
- **Expected Structural Challenge**: Short digital PDF notice with explicit bullet points for eligibility and submission.
- **Likely Schema Fields Covered**: `title`, `organization`, `opportunity_type`, `eligible_disciplines`, `duration`, `application_url`, `required_documents`.

#### Slot OPP-E-03
- **Document ID**: `OPP-E-03`
- **Domain**: Opportunities
- **Difficulty**: Easy
- **Desired Document Type**: Corporate Foundation Student Fellowship Notification
- **Preferred Source Category**: Official Corporate Foundation Web Page (HTML)
- **Expected Structural Challenge**: Structured Web DOM with clear headings for eligibility, benefits, and deadlines.
- **Likely Schema Fields Covered**: `title`, `organization`, `opportunity_type`, `education_level`, `skills_required`, `stipend_or_funding`, `application_url`.

#### Slot OPP-E-04
- **Document ID**: `OPP-E-04`
- **Domain**: Opportunities
- **Difficulty**: Easy
- **Desired Document Type**: Government Research Council Student Travel Grant Notice
- **Preferred Source Category**: Science & Engineering Research Council PDF Notice
- **Expected Structural Challenge**: Brief single-page digital PDF with clear eligibility parameters.
- **Likely Schema Fields Covered**: `title`, `organization`, `opportunity_type`, `education_level`, `eligible_disciplines`, `stipend_or_funding`, `application_deadline`.

---

### Medium Slots (5 Documents)

#### Slot OPP-M-01
- **Document ID**: `OPP-M-01`
- **Domain**: Opportunities
- **Difficulty**: Medium
- **Desired Document Type**: University Postdoctoral Research Fellowship Call for Proposals
- **Preferred Source Category**: Central University / Academic Research Office PDF
- **Expected Structural Challenge**: Multi-page PDF document with embedded stipend tables, academic experience rules, and application package lists.
- **Likely Schema Fields Covered**: `title`, `organization`, `opportunity_type`, `education_level`, `eligible_disciplines`, `experience_required`, `stipend_or_funding`, `duration`, `required_documents`, `application_deadline`.

#### Slot OPP-M-02
- **Document ID**: `OPP-M-02`
- **Domain**: Opportunities
- **Difficulty**: Medium
- **Desired Document Type**: National Science Foundation Research Grant Portal Web Page
- **Preferred Source Category**: National Research Funding Agency Web Page (HTML)
- **Expected Structural Challenge**: Web page containing nested HTML tables, discipline guidelines, and external application portal links.
- **Likely Schema Fields Covered**: `title`, `organization`, `opportunity_type`, `eligible_disciplines`, `skills_required`, `location`, `mode`, `stipend_or_funding`, `application_url`.

#### Slot OPP-M-03
- **Document ID**: `OPP-M-03`
- **Domain**: Opportunities
- **Difficulty**: Medium
- **Desired Document Type**: International Graduate Student Scholarship Brochure
- **Preferred Source Category**: International Education Commission / University PDF
- **Expected Structural Challenge**: Distributed multi-section text, country-specific eligibility notes, and multi-step application requirements.
- **Likely Schema Fields Covered**: `title`, `organization`, `opportunity_type`, `education_level`, `eligibility_notes`, `location`, `stipend_or_funding`, `start_date`, `required_documents`, `application_deadline`.

#### Slot OPP-M-04
- **Document ID**: `OPP-M-04`
- **Domain**: Opportunities
- **Difficulty**: Medium
- **Desired Document Type**: Industry-Academia Joint Internship & Mentorship Program Notice
- **Preferred Source Category**: Official Research Center / Partner Company Web Page (HTML)
- **Expected Structural Challenge**: HTML page containing technical skill lists, internship mode (remote/on-site), and submission checklists.
- **Likely Schema Fields Covered**: `title`, `organization`, `opportunity_type`, `skills_required`, `experience_required`, `mode`, `duration`, `stipend_or_funding`, `application_url`, `required_documents`.

#### Slot OPP-M-05
- **Document ID**: `OPP-M-05`
- **Domain**: Opportunities
- **Difficulty**: Medium
- **Desired Document Type**: National Laboratory Doctoral Fellowship Announcement
- **Preferred Source Category**: Government Research Laboratory PDF
- **Expected Structural Challenge**: Multi-page document with stipend tier tables, discipline prerequisites, and start date timelines.
- **Likely Schema Fields Covered**: `title`, `organization`, `opportunity_type`, `education_level`, `eligible_disciplines`, `location`, `duration`, `stipend_or_funding`, `start_date`, `application_deadline`.

---

### Hard Slots (3 Documents)

#### Slot OPP-H-01
- **Document ID**: `OPP-H-01`
- **Domain**: Opportunities
- **Difficulty**: Hard
- **Desired Document Type**: Institutional Research Opportunity Notification Circular
- **Preferred Source Category**: University / Research Foundation Archives (Scanned/OCR Candidate)
- **Expected Structural Challenge**: Image-based scanned document requiring OCR, non-standard typography, line noise, and layout artifacts.
- **Likely Schema Fields Covered**: `title`, `organization`, `opportunity_type`, `education_level`, `eligible_disciplines`, `experience_required`, `location`, `stipend_or_funding`, `application_deadline`.

#### Slot OPP-H-02
- **Document ID**: `OPP-H-02`
- **Domain**: Opportunities
- **Difficulty**: Hard
- **Desired Document Type**: Multi-Track University Fellowship Guidelines with Complex Discipline Tables
- **Preferred Source Category**: Research University PDF
- **Expected Structural Challenge**: Multi-track fellowship structure with dense multi-column tables, complex discipline matrices, and multi-hop eligibility conditions.
- **Likely Schema Fields Covered**: `title`, `organization`, `opportunity_type`, `education_level`, `eligible_disciplines`, `skills_required`, `experience_required`, `eligibility_notes`, `stipend_or_funding`, `start_date`, `application_deadline`.

#### Slot OPP-H-03
- **Document ID**: `OPP-H-03`
- **Domain**: Opportunities
- **Difficulty**: Hard
- **Desired Document Type**: Global Collaborative Research Grant Call with Distributed Clauses
- **Preferred Source Category**: International Research Council PDF / Web HTML
- **Expected Structural Challenge**: Highly complex multi-institutional guidelines with distributed conditional funding clauses, country-specific eligibility notes, and multi-location evidence citations.
- **Likely Schema Fields Covered**: `title`, `organization`, `opportunity_type`, `eligible_disciplines`, `eligibility_notes`, `location`, `mode`, `duration`, `stipend_or_funding`, `start_date`, `application_url`, `required_documents`.

---

## 6. Curation Plan Verification Summary

| Evaluation Domain | Easy Slots | Medium Slots | Hard Slots | Total Slots per Domain |
| :--- | :---: | :---: | :---: | :---: |
| **Government Welfare & Scholarship Schemes** (`GOV`) | 4 (`GOV-E-01` to `GOV-E-04`) | 5 (`GOV-M-01` to `GOV-M-05`) | 3 (`GOV-H-01` to `GOV-H-03`) | **12 Slots** |
| **Opportunities** (`OPP`) | 4 (`OPP-E-01` to `OPP-E-04`) | 5 (`OPP-M-01` to `OPP-M-05`) | 3 (`OPP-H-01` to `OPP-H-03`) | **12 Slots** |
| **Total Evaluation Benchmark** | **8 Slots** | **10 Slots** | **6 Slots** | **24 Slots Total** |

- **Total Planned Slots**: **24 Document Slots**
- **Domain Distribution**: Exactly 12 Primary Domain (`GOV`) + 12 Secondary Domain (`OPP`).
- **Difficulty Distribution per Domain**: Exactly 4 Easy + 5 Medium + 3 Hard per domain.
- **Format & Layout Diversity**: Digital PDFs, HTML Web Pages, Structured Tables, Distributed Clauses, and Preferred Scanned/OCR Candidates (`GOV-H-01`, `OPP-H-01` or equivalent hard layout challenges).
