# Dataset Strategy

## 1. Overview and Dataset Scope
This document outlines the dataset collection and curation strategy for Phase 0 of the Autonomous Document Intelligence Agent. The goal is to establish a high-quality, diverse evaluation dataset comprising 24 real-world documents balanced across two distinct domains:

- **12 Government Welfare & Scholarship Scheme Documents** (Primary Domain)
- **12 Opportunity Documents** (Secondary Domain: Scholarships, Internships, Fellowships, Research Calls)

The dataset is designed to evaluate document parsing, layout inspection, evidence-grounded extraction, and claim verification without relying on template-specific assumptions.

---

## 2. Difficulty Distribution
To rigorously test the system across varying structural complexities, each domain dataset of 12 documents follows an identical difficulty breakdown:

| Difficulty Level | Documents per Domain | Total Dataset Documents | Key Layout & Structural Characteristics |
| :--- | :--- | :--- | :--- |
| **Easy** | 4 | 8 | Clean digital text, simple structures, direct field-value pairs, minimal ambiguity. |
| **Medium** | 5 | 10 | Multi-page documents, distributed text, embedded tables/lists, missing fields, multi-section synthesis. |
| **Hard** | 3 | 6 | Scanned/OCR documents, complex or messy layouts, table-heavy structures, ambiguous or distributed conditions. |
| **Total** | **12** | **24** | Balanced across both evaluation domains. |

---

## 3. Difficulty Level Definitions

### Easy
- **Format**: Native digital text (PDF or HTML).
- **Structure**: Clear layout with standard single-column or well-defined visual hierarchy.
- **Extraction Path**: Direct field-value relationships occurring in explicit key-value blocks or prose.
- **Ambiguity**: Low or no ambiguity; complete information available in local context.

### Medium
- **Format**: Native digital PDF or structured HTML web pages.
- **Structure**: Multi-page documents or web pages with distributed sections, key-value tables, or bulleted lists.
- **Extraction Path**: Requires combining information across separate sections or navigating tabular data.
- **Ambiguity**: Moderate; includes optional or missing fields that must be recognized as `null`/`not_found`.

### Hard
- **Format**: Scanned image-based PDFs requiring OCR, or dense HTML documents with complex multi-column structures.
- **Structure**: Visually complex, table-heavy, or non-standard visual layouts.
- **Extraction Path**: Requires multi-hop evidence collection across multiple pages or tables.
- **Ambiguity**: May contain ambiguous eligibility rules, implicit criteria, conflicting information, or distributed conditions requiring careful verification and evidence collection.

---

## 4. Desired Document Diversity

### Primary Domain: Government Welfare and Scholarship Schemes
To reflect real-world public sector documentation, the selection must incorporate:
- Central and state government scheme operational guidelines.
- Official scholarship notifications and press circulars.
- Beneficiary eligibility rule documents and policy guidelines.
- Official government portal web pages (HTML) and published policy papers (PDF).

### Secondary Domain: Opportunities (Scholarships, Internships, Fellowships, Research Calls)
To demonstrate cross-domain generalization without template lock-in, the selection must incorporate:
- University scholarship announcements and call for applications.
- Corporate and institutional internship program notifications.
- Academic research fellowship guidelines and stipend calls.
- Research grant metadata and call for proposals.
- Official institutional sources (universities, research centers, government research councils) across digital PDF and HTML formats.

---

## 5. Source Selection & Curation Rules

1. **Authoritative First-Party Sources**: Prefer official first-party sources, including government portals, universities, research institutions, and official organization or company websites. Third-party aggregators and unofficial summaries must not be used as source documents.
2. **No Aggregators or Unofficial Blogs**: Strictly exclude commercial blog posts, scraped aggregator sites, forums, and third-party summaries.
3. **Exact Provenance Tracking**: Record the exact source URL, file format, document type, and domain in `sources.csv`.
4. **Stability and Archiving**: Use stable official URLs or store exact raw copies in the repository data/ directory when appropriate to reduce the risk of link rot.
5. **No Metadata Fabrication**: Document entries and metadata must reflect real ingested documents; zero synthetic or placeholder entries are permitted.
6. **Manual Inspection**: Every candidate document must undergo manual review against difficulty definitions and schema coverage prior to annotation.
