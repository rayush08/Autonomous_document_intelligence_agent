import os
import json

results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"

taxonomy_path = os.path.join(results_dir, "phase6_failure_taxonomy.json")

with open(taxonomy_path, "r", encoding="utf-8") as f:
    tax_data = json.load(f)

records = tax_data.get("failure_records", [])

targets_by_priority = {
    "Priority 1: List Incompleteness": [],
    "Priority 2: Numeric Normalization": [],
    "Priority 3: Unit & Format Normalization": [],
    "Priority 4: Taxonomy & Category Mismatch": []
}

for r in records:
    cat = r.get("failure_category")
    f_item = {
        "document_id": r.get("document_id"),
        "field": r.get("field"),
        "expected_value": r.get("expected_value"),
        "predicted_value": r.get("predicted_value")
    }
    if cat == "LIST_INCOMPLETENESS":
        targets_by_priority["Priority 1: List Incompleteness"].append(f_item)
    elif cat == "NUMERIC_NORMALIZATION_ERROR":
        targets_by_priority["Priority 2: Numeric Normalization"].append(f_item)
    elif cat == "UNIT_OR_FORMAT_NORMALIZATION_ERROR":
        targets_by_priority["Priority 3: Unit & Format Normalization"].append(f_item)
    elif cat == "TAXONOMY_OR_CATEGORY_MISMATCH":
        targets_by_priority["Priority 4: Taxonomy & Category Mismatch"].append(f_item)

targets_summary = {
    "total_target_records": sum(len(v) for v in targets_by_priority.values()),
    "priority_breakdown": {p: len(v) for p, v in targets_by_priority.items()},
    "target_records": targets_by_priority
}

with open(os.path.join(results_dir, "phase7_failure_targets.json"), "w", encoding="utf-8") as f:
    json.dump(targets_summary, f, indent=2)

md_lines = [
    "# Phase 7 Targeted Failure Matrix & Priorities Report",
    "",
    f"Total Priority Failure Target Records: {targets_summary['total_target_records']}",
    "",
    "## Priority Breakdown",
    "",
    "| Priority Level | Target Failure Category | Total Target Count | Primary Target Fields |",
    "|---|---|---:|---|",
    f"| Priority 1 | `LIST_INCOMPLETENESS` | {len(targets_by_priority['Priority 1: List Incompleteness'])} | `required_documents`, `target_beneficiaries` |",
    f"| Priority 2 | `NUMERIC_NORMALIZATION_ERROR` | {len(targets_by_priority['Priority 2: Numeric Normalization'])} | `benefit_amount`, `stipend_or_funding`, `academic_criteria` |",
    f"| Priority 3 | `UNIT_OR_FORMAT_NORMALIZATION_ERROR` | {len(targets_by_priority['Priority 3: Unit & Format Normalization'])} | `benefit_amount`, `duration` |",
    f"| Priority 4 | `TAXONOMY_OR_CATEGORY_MISMATCH` | {len(targets_by_priority['Priority 4: Taxonomy & Category Mismatch'])} | `scheme_type`, `benefit_type` |",
]

with open(os.path.join(results_dir, "phase7_failure_targets.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print("Saved phase7_failure_targets.json and phase7_failure_targets.md successfully.")
