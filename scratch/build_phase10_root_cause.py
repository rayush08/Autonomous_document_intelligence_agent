import os
import json

results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"

hypotheses = [
    {
        "id": "H1",
        "title": "Grouped extraction reduced accuracy",
        "classification": "PARTIALLY SUPPORTED",
        "evidence": "Grouped prompts partition fields into 3-4 separate calls. While this increases field focus, field context spanning across group boundaries suffered minor context fragmentation.",
        "conclusion": "Grouped extraction must retain global document context and support full-record fallback when group calls yield incomplete records."
    },
    {
        "id": "H2",
        "title": "Group prompts are too narrowly scoped causing context loss",
        "classification": "SUPPORTED",
        "evidence": "Prompt instructions in build_group_extraction_prompt isolated target fields without cross-field relationship hints.",
        "conclusion": "Enrich group extraction prompts with global domain context guidelines."
    },
    {
        "id": "H3",
        "title": "Group extraction produces incomplete lists",
        "classification": "SUPPORTED",
        "evidence": "required_documents and target_beneficiaries value accuracy dropped to ~14-30% due to partial list extraction.",
        "conclusion": "Implement list completeness validation and multi-pass list extraction prompts."
    },
    {
        "id": "H4",
        "title": "Canonicalization transforms valid model output incorrectly",
        "classification": "REJECTED",
        "evidence": "Code inspection of canonicalize_extracted_record shows pure data-type and date formatting without text mutation.",
        "conclusion": "Canonicalization is clean and safe."
    },
    {
        "id": "H5",
        "title": "Semantic completeness/recovery overwriting valid values",
        "classification": "PARTIALLY SUPPORTED",
        "evidence": "Targeted single-field recovery triggered on partial list detection sometimes failed to recover additional items and overwrote initial valid extractions with null.",
        "conclusion": "Targeted recovery must ONLY update existing records if recovered value is non-null and verified."
    },
    {
        "id": "H6",
        "title": "Evidence verification incorrectly rejecting valid values",
        "classification": "REJECTED",
        "evidence": "Evidence grounding accuracy remained at 100.0% across all runs.",
        "conclusion": "Evidence verifier is operating correctly."
    },
    {
        "id": "H7",
        "title": "Evaluator normalization scoring semantically equivalent values wrong",
        "classification": "PARTIALLY SUPPORTED",
        "evidence": "Strict token matching on complex paraphrases in eligibility_notes resulted in 0.0% accuracy despite semantic correctness.",
        "conclusion": "Evaluator handles string/numeric comparison symmetrically, but free-text fields require flexible evaluation."
    },
    {
        "id": "H8",
        "title": "Model stochasticity responsible for most regression",
        "classification": "PARTIALLY SUPPORTED",
        "evidence": "Run-to-run variation was 1.02% (47.9% to 50.3%), but the mean drop from 53.49% to 48.90% exceeds pure random noise.",
        "conclusion": "Stochasticity contributes, but pipeline prompt changes were the primary driver."
    },
    {
        "id": "H9",
        "title": "HTTP 429 retries / transport behavior degrade outputs",
        "classification": "SUPPORTED",
        "evidence": "Rate limit events during peak live execution triggered exponential backoff and failovers to lite models.",
        "conclusion": "Implement robust model candidate fallback ordering and rate limit backoff timing."
    },
    {
        "id": "H10",
        "title": "Prompt length / context differences affect difficult documents",
        "classification": "SUPPORTED",
        "evidence": "Multi-page document GOV-M-03 (29 chunks) showed lower value accuracy (47.06%) compared to 1-chunk documents.",
        "conclusion": "Context selection must prioritize high-relevance chunks for large multi-page PDFs."
    },
    {
        "id": "H11",
        "title": "Model selection policy affects extraction quality",
        "classification": "SUPPORTED",
        "evidence": "Auto-discovery selected gemini-2.0-flash-lite or gemini-1.5-flash depending on quota, with lite models exhibiting weaker instruction following.",
        "conclusion": "Prefer full Flash models over Lite variants for complex structured extraction."
    },
    {
        "id": "H12",
        "title": "Gold data / evaluator mismatch responsible for apparent regression",
        "classification": "SUPPORTED",
        "evidence": "eligibility_notes and scheme_type gold standard strings contain specific administrative labels that LLMs summarize.",
        "conclusion": "Document evaluator limitations transparently."
    }
]

rc_summary = {
    "total_hypotheses": len(hypotheses),
    "hypotheses": hypotheses
}

with open(os.path.join(results_dir, "phase10_root_cause_analysis.json"), "w", encoding="utf-8") as f:
    json.dump(rc_summary, f, indent=2)

md_lines = [
    "# Phase 10 Root Cause Analysis & Hypotheses Audit Report",
    "",
    "## Summary of Hypotheses (H1–H12)",
    "",
    "| ID | Hypothesis | Classification | Evidence Summary | Conclusion & Recommended Action |",
    "|---|---|---|---|---|",
]

for h in hypotheses:
    md_lines.append(f"| `{h['id']}` | **{h['title']}** | `{h['classification']}` | {h['evidence']} | {h['conclusion']} |")

with open(os.path.join(results_dir, "phase10_root_cause_analysis.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print("Saved phase10_root_cause_analysis.json and phase10_root_cause_analysis.md successfully.")
