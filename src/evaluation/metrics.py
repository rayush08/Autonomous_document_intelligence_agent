import statistics


def compute_metrics(eval_results: list[dict]) -> dict:
    """
    Compute comprehensive Phase 3 metrics across evaluation cases.
    
    Metric Definitions:
    - Schema Validity Rate: Proportion of extracted records passing JSON Schema constraints.
    - Field Extraction Accuracy: Proportion of target fields where extracted value matches ground truth (score >= 0.7).
    - Verification Status Accuracy: Proportion of target fields matching ground-truth verification_status.
    - Missing Information Accuracy: Proportion of genuinely absent fields (gold status 'not_found') correctly extracted as 'not_found'.
    - Hallucination / Unsupported Claim Rate: Proportion of genuinely absent fields where model asserted a non-null claim.
    - Evidence Grounding Accuracy: Proportion of non-null extracted claims supported by non-empty verbatim evidence snippets.
      Note: High Evidence Grounding Accuracy (100%) and non-zero Hallucination Rate (>0%) can legitimately coexist when a model attaches a verbatim document snippet to an unsupported field claim.
    
    Returns metrics dict containing:
    - Overall metrics
    - Domain-level metrics
    - Document-level metrics
    - Field-level metrics
    - Retry & Latency statistics
    """
    total_docs = len(eval_results)
    if total_docs == 0:
        return {}

    schema_valid_docs = sum(1 for r in eval_results if r.get("schema_valid", False))
    schema_validity_rate = schema_valid_docs / total_docs

    all_field_comps = []
    domain_results = {}
    doc_results = []
    latencies = []
    attempt_counts = []
    semantic_retry_counts = []

    for r in eval_results:
        doc_id = r.get("document_id")
        domain = r.get("domain", "unknown")
        lat = r.get("latency_seconds", 0.0)
        attempts = r.get("extraction_attempts", 1)
        sem_retries = max(0, attempts - 1)

        latencies.append(lat)
        attempt_counts.append(attempts)
        semantic_retry_counts.append(sem_retries)

        if domain not in domain_results:
            domain_results[domain] = {
                "total_docs": 0,
                "schema_valid_docs": 0,
                "field_comps": [],
                "latencies": [],
                "attempts": []
            }

        domain_results[domain]["total_docs"] += 1
        if r.get("schema_valid", False):
            domain_results[domain]["schema_valid_docs"] += 1
        domain_results[domain]["latencies"].append(lat)
        domain_results[domain]["attempts"].append(attempts)

        f_comps = r.get("field_comparisons", [])
        all_field_comps.extend(f_comps)
        domain_results[domain]["field_comps"].extend(f_comps)

        # Document summary
        doc_val_acc = (sum(1 for fc in f_comps if fc["value_match"]) / len(f_comps)) if f_comps else 0.0
        doc_status_acc = (sum(1 for fc in f_comps if fc["status_match"]) / len(f_comps)) if f_comps else 0.0
        doc_results.append({
            "document_id": doc_id,
            "domain": domain,
            "schema_valid": r.get("schema_valid", False),
            "latency_seconds": round(lat, 3),
            "attempts": attempts,
            "field_count": len(f_comps),
            "value_accuracy": round(doc_val_acc, 4),
            "status_accuracy": round(doc_status_acc, 4)
        })

    # Overall Field Metrics
    total_fields = len(all_field_comps)
    status_matches = sum(1 for fc in all_field_comps if fc["status_match"])
    value_matches = sum(1 for fc in all_field_comps if fc["value_match"])
    avg_value_score = (sum(fc["value_score"] for fc in all_field_comps) / total_fields) if total_fields else 0.0

    genuinely_missing = [fc for fc in all_field_comps if fc["is_genuinely_missing"]]
    missing_info_correct = sum(1 for fc in genuinely_missing if fc["missing_info_correct"])
    missing_info_accuracy = (missing_info_correct / len(genuinely_missing)) if genuinely_missing else 1.0

    hallucinations = sum(1 for fc in all_field_comps if fc["is_hallucination"])
    hallucination_rate = (hallucinations / len(genuinely_missing)) if genuinely_missing else 0.0

    grounded_claims = sum(1 for fc in all_field_comps if fc["evidence_grounded"])
    evidence_grounding_accuracy = (grounded_claims / total_fields) if total_fields else 1.0

    # Field-level Breakdown
    field_breakdown = {}
    for fc in all_field_comps:
        fname = fc["field_name"]
        if fname not in field_breakdown:
            field_breakdown[fname] = {"total": 0, "status_matches": 0, "value_matches": 0, "value_score_sum": 0.0}
        field_breakdown[fname]["total"] += 1
        if fc["status_match"]: field_breakdown[fname]["status_matches"] += 1
        if fc["value_match"]: field_breakdown[fname]["value_matches"] += 1
        field_breakdown[fname]["value_score_sum"] += fc["value_score"]

    field_level_summary = {}
    for fname, fstats in field_breakdown.items():
        tot = fstats["total"]
        field_level_summary[fname] = {
            "status_accuracy": round(fstats["status_matches"] / tot, 4) if tot else 0.0,
            "value_accuracy": round(fstats["value_matches"] / tot, 4) if tot else 0.0,
            "mean_value_score": round(fstats["value_score_sum"] / tot, 4) if tot else 0.0
        }

    # Domain-level Metrics
    domain_metrics = {}
    for dom, ddata in domain_results.items():
        dtot = ddata["total_docs"]
        dfcomps = ddata["field_comps"]
        dnum_f = len(dfcomps)
        dval_m = sum(1 for fc in dfcomps if fc["value_match"])
        dstat_m = sum(1 for fc in dfcomps if fc["status_match"])

        dmissing = [fc for fc in dfcomps if fc["is_genuinely_missing"]]
        dmissing_corr = sum(1 for fc in dmissing if fc["missing_info_correct"])
        dhalluc = sum(1 for fc in dfcomps if fc["is_hallucination"])

        domain_metrics[dom] = {
            "total_documents": dtot,
            "schema_validity_rate": round(ddata["schema_valid_docs"] / dtot, 4) if dtot else 0.0,
            "field_extraction_accuracy": round(dval_m / dnum_f, 4) if dnum_f else 0.0,
            "verification_status_accuracy": round(dstat_m / dnum_f, 4) if dnum_f else 0.0,
            "missing_info_accuracy": round(dmissing_corr / len(dmissing), 4) if dmissing else 1.0,
            "hallucination_rate": round(dhalluc / len(dmissing), 4) if dmissing else 0.0,
            "average_latency_seconds": round(sum(ddata["latencies"]) / dtot, 3) if dtot else 0.0
        }

    # Latency & Retry Statistics
    mean_latency = sum(latencies) / total_docs if total_docs else 0.0
    median_latency = statistics.median(latencies) if latencies else 0.0
    slowest_doc = max(eval_results, key=lambda x: x.get("latency_seconds", 0.0)).get("document_id") if eval_results else None

    return {
        "overall": {
            "total_documents_evaluated": total_docs,
            "schema_validity_rate": round(schema_validity_rate, 4),
            "field_extraction_accuracy": round(value_matches / total_fields, 4) if total_fields else 0.0,
            "mean_field_value_score": round(avg_value_score, 4),
            "verification_status_accuracy": round(status_matches / total_fields, 4) if total_fields else 0.0,
            "missing_information_accuracy": round(missing_info_accuracy, 4),
            "hallucination_rate": round(hallucination_rate, 4),
            "evidence_grounding_accuracy": round(evidence_grounding_accuracy, 4)
        },
        "domain_breakdown": domain_metrics,
        "document_breakdown": doc_results,
        "field_breakdown": field_level_summary,
        "retry_statistics": {
            "total_extraction_attempts": sum(attempt_counts),
            "semantic_retries_executed": sum(semantic_retry_counts),
            "failures_after_retry": sum(1 for r in eval_results if not r.get("schema_valid", False))
        },
        "latency_statistics": {
            "mean_latency_seconds": round(mean_latency, 3),
            "median_latency_seconds": round(median_latency, 3),
            "slowest_document_id": slowest_doc,
            "max_latency_seconds": round(max(latencies), 3) if latencies else 0.0
        }
    }

