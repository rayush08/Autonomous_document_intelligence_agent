import os
import json


def format_markdown_report(metrics: dict, mode: str = "offline") -> str:
    """Format Phase 3 evaluation metrics into clean GitHub-flavored markdown report."""
    overall = metrics.get("overall", {})
    domains = metrics.get("domain_breakdown", {})
    docs = metrics.get("document_breakdown", [])
    fields = metrics.get("field_breakdown", {})
    retries = metrics.get("retry_statistics", {})
    latencies = metrics.get("latency_statistics", {})

    mode_title = "Real Gemini LLM Pipeline Evaluation" if mode == "real" else "Offline Evaluator Regression Baseline"

    lines = [
        f"# Phase 3 Benchmark Evaluation & Quality Report",
        f"### Mode: {mode_title}",
        "",
        "## 1. Executive Summary & Overall Metrics",
        "",
        f"- **Evaluation Mode**: `{mode_title.upper()}`",

        f"- **Total Documents Evaluated**: `{overall.get('total_documents_evaluated', 0)}`",
        f"- **Schema Validity Rate**: `{overall.get('schema_validity_rate', 0.0) * 100:.1f}%`",
        f"- **Field Extraction Accuracy**: `{overall.get('field_extraction_accuracy', 0.0) * 100:.1f}%`",
        f"- **Mean Field Value Score**: `{overall.get('mean_field_value_score', 0.0):.4f}`",
        f"- **Verification Status Accuracy**: `{overall.get('verification_status_accuracy', 0.0) * 100:.1f}%`",
        f"- **Missing Information Accuracy**: `{overall.get('missing_information_accuracy', 0.0) * 100:.1f}%`",
        f"- **Hallucination / Unsupported Claim Rate**: `{overall.get('hallucination_rate', 0.0) * 100:.1f}%`",
        f"- **Evidence Grounding Accuracy**: `{overall.get('evidence_grounding_accuracy', 0.0) * 100:.1f}%`",
        "",
        "---",
        "",
        "## 2. Cross-Domain Generalization Breakdown",
        "",
        "| Domain | Documents | Schema Validity | Value Accuracy | Status Accuracy | Missing Info Acc | Hallucination Rate | Mean Latency |",
        "|---|---|---|---|---|---|---|---|"
    ]

    for dom, dmeta in domains.items():
        lines.append(
            f"| **{dom}** | {dmeta.get('total_documents')} | "
            f"{dmeta.get('schema_validity_rate')*100:.1f}% | "
            f"{dmeta.get('field_extraction_accuracy')*100:.1f}% | "
            f"{dmeta.get('verification_status_accuracy')*100:.1f}% | "
            f"{dmeta.get('missing_info_accuracy')*100:.1f}% | "
            f"{dmeta.get('hallucination_rate')*100:.1f}% | "
            f"{dmeta.get('average_latency_seconds'):.3f}s |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 3. Document-Level Execution Breakdown",
        "",
        "| Document ID | Domain | Schema Valid | Attempts | Value Accuracy | Status Accuracy | Latency |",
        "|---|---|---|---|---|---|---|"
    ])

    for doc in docs:
        valid_icon = "✅ YES" if doc.get("schema_valid") else "❌ NO"
        lines.append(
            f"| `{doc.get('document_id')}` | {doc.get('domain')} | {valid_icon} | "
            f"{doc.get('attempts')} | {doc.get('value_accuracy')*100:.1f}% | "
            f"{doc.get('status_accuracy')*100:.1f}% | {doc.get('latency_seconds'):.3f}s |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 4. Latency & Retry Statistics",
        "",
        f"- **Total Extraction Attempts**: `{retries.get('total_extraction_attempts', 0)}`",
        f"- **Semantic Retries Executed**: `{retries.get('semantic_retries_executed', 0)}`",
        f"- **Failures After Retry**: `{retries.get('failures_after_retry', 0)}`",
        f"- **Mean Document Latency**: `{latencies.get('mean_latency_seconds', 0.0):.3f}s`",
        f"- **Median Document Latency**: `{latencies.get('median_latency_seconds', 0.0):.3f}s`",
        f"- **Slowest Document**: `{latencies.get('slowest_document_id')} ({latencies.get('max_latency_seconds', 0.0):.3f}s)`",
        "",
        "---",
        "",
        "## 5. Field-Level Accuracy Breakdown",
        "",
        "| Field Name | Status Accuracy | Value Accuracy | Mean Value Score |",
        "|---|---|---|---|"
    ])

    for fname, fmeta in sorted(fields.items()):
        lines.append(
            f"| `{fname}` | {fmeta.get('status_accuracy')*100:.1f}% | "
            f"{fmeta.get('value_accuracy')*100:.1f}% | {fmeta.get('mean_value_score'):.4f} |"
        )

    return "\n".join(lines)


def save_reports(metrics: dict, output_dir: str, mode: str = "offline", run_id: int = None):
    """Save machine-readable JSON and readable Markdown benchmark reports."""
    os.makedirs(output_dir, exist_ok=True)
    if run_id is not None:
        json_filename = f"{mode}_run_{run_id}_results.json"
        md_filename = f"{mode}_run_{run_id}_report.md"
    else:
        json_filename = f"{mode}_benchmark_results.json"
        md_filename = f"{mode}_benchmark_report.md"

    json_path = os.path.join(output_dir, json_filename)
    md_path = os.path.join(output_dir, md_filename)

    # Save JSON report
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    # Save Markdown report
    md_content = format_markdown_report(metrics, mode=mode)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"📊 Benchmark Reports Saved ({mode.upper()} mode, run_id={run_id}):\n   -> JSON: {json_path}\n   -> Markdown: {md_path}")


