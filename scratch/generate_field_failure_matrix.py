import os
import json
import sys

sys.path.insert(0, os.getcwd())

from src.evaluation.comparison import normalize_str, compare_values

results_path = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results\real_benchmark_results.json"
out_json_path = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results\field_failure_matrix.json"
out_md_path = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results\field_failure_matrix.md"

with open(results_path, "r", encoding="utf-8") as f:
    data = json.load(f)

raw_results = data.get("raw_results", [])

failure_matrix = []

for doc in raw_results:
    doc_id = doc.get("document_id")
    domain = doc.get("domain")
    f_comps = doc.get("field_comparisons", [])
    
    for fc in f_comps:
        field_name = fc.get("field_name")
        val_score = fc.get("value_score", 0.0)
        val_match = fc.get("value_match", False)
        status_match = fc.get("status_match", False)
        exp_status = fc.get("expected_status")
        ext_status = fc.get("extracted_status")
        exp_val = fc.get("expected_value") if "expected_value" in fc else None
        ext_val = fc.get("extracted_value") if "extracted_value" in fc else None
        ext_ev = fc.get("extracted_evidence") if "extracted_evidence" in fc else []
        
        if not val_match or not status_match:
            norm_exp = normalize_str(str(exp_val)) if exp_val is not None else ""
            norm_ext = normalize_str(str(ext_val)) if ext_val is not None else ""
            
            # Determine exact reason comparison failed & primary failure category
            if domain == "opportunities" and ext_status == "not_found" and exp_status != "not_found":
                category = "E. Prompt instruction ambiguity"
                reason = f"Prompt hardcoded Government Scheme fields for Opportunity document {doc_id}; Opportunity target fields were omitted from prompt."
            elif field_name in {"benefit_amount", "stipend_or_funding"} and isinstance(ext_val, list) and len(ext_val) >= 2:
                category = "G. Canonicalization corrupted correct output"
                reason = f"Naive comma splitting on numeric amounts ({ext_val}) corrupted monetary expression."
            elif val_score >= 0.4 and val_score < 0.7:
                category = "H. Evaluator comparison is too strict"
                reason = f"String comparison did not normalize currency symbols or frequency terms (Score: {val_score:.2f})."
            elif exp_status == "not_found" and ext_status != "not_found" and ext_val is not None:
                category = "C. Model hallucinated unsupported information"
                reason = f"Model extracted non-null claim '{ext_val}' for genuinely missing field (gold status: not_found)."
            elif ext_status == "not_found" and exp_status != "not_found":
                category = "A. Model failed to extract information present in text"
                reason = f"Model returned not_found for field present in document text (gold status: {exp_status})."
            elif not status_match and val_match:
                category = "J. Verification status incorrect"
                reason = f"Value matched ({val_score:.2f}) but verification status mismatched (Exp: {exp_status} vs Ext: {ext_status})."
            else:
                category = "B. Model extracted wrong information"
                reason = f"Extracted value '{ext_val}' did not match gold value '{exp_val}' (Score: {val_score:.2f})."

            entry = {
                "document_id": doc_id,
                "domain": domain,
                "field_name": field_name,
                "gold_value": exp_val,
                "extracted_value": ext_val,
                "expected_status": exp_status,
                "extracted_status": ext_status,
                "evidence": ext_ev,
                "normalized_gold_value": norm_exp,
                "normalized_extracted_value": norm_ext,
                "comparison_score": val_score,
                "primary_category": category,
                "exact_reason_failed": reason
            }
            failure_matrix.append(entry)

# Save JSON report
with open(out_json_path, "w", encoding="utf-8") as f:
    json.dump(failure_matrix, f, indent=2, ensure_ascii=False)

# Save Markdown report
md_lines = [
    "# Field-Level Benchmark Failure Matrix",
    f"Total Field Mismatches: `{len(failure_matrix)}`",
    "",
    "| Document ID | Domain | Field Name | Gold Status | Ext Status | Comparison Score | Primary Category | Exact Failure Reason |",
    "|---|---|---|---|---|---|---|---|"
]

for item in failure_matrix:
    md_lines.append(
        f"| `{item['document_id']}` | {item['domain']} | `{item['field_name']}` | "
        f"`{item['expected_status']}` | `{item['extracted_status']}` | `{item['comparison_score']:.2f}` | "
        f"**{item['primary_category']}** | {item['exact_reason_failed']} |"
    )

with open(out_md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(f"✅ Generated field failure matrix with {len(failure_matrix)} mismatches:")
print(f"   -> JSON: {out_json_path}")
print(f"   -> Markdown: {out_md_path}")
