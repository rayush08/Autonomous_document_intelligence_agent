import os
import json
import time
from src.extraction import extract_document, validate_extracted_record, get_fields_for_record
from src.evaluation.comparison import compare_field
from src.evaluation.metrics import compute_metrics
from src.llm.base_client import LLMTransportError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GOLD_DIR = os.path.join(BASE_DIR, "evaluation", "gold")


class EvaluationEngine:
    """
    Reusable evaluation engine for cross-domain benchmark evaluation.
    Loads gold ground truth, executes extraction, runs intelligent field comparison,
    and computes Phase 3 quality metrics.
    """

    def __init__(self, gold_dir: str = GOLD_DIR, extractor = None):
        self.gold_dir = gold_dir
        self.extractor = extractor

    def load_gold_record(self, document_id: str) -> dict:
        gold_path = os.path.join(self.gold_dir, f"{document_id}.json")
        if not os.path.exists(gold_path):
            raise FileNotFoundError(f"Gold ground truth fixture not found for [{document_id}] at {gold_path}")
        with open(gold_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def evaluate_document(self, document_id: str, extracted_record: dict = None) -> dict:
        """
        Evaluate single document extraction against ground truth gold fixture.
        
        Args:
            document_id (str): Target document ID e.g. 'GOV-E-01' or 'OPP-E-01'
            extracted_record (dict, optional): Extracted record. If None, runs self.extractor or extract_document.
            
        Returns:
            dict: Document evaluation result including field comparisons and latency.
        """
        gold = self.load_gold_record(document_id)
        domain = "opportunities" if document_id.startswith("OPP-") else "government_schemes"

        start_time = time.time()
        attempts = 1
        is_infrastructure_failure = False
        infra_error_msg = ""

        if extracted_record is None:
            try:
                extracted_record = extract_document(document_id, extractor=self.extractor)
            except LLMTransportError as e:
                is_infrastructure_failure = True
                infra_error_msg = str(e)
                print(f"⚠️ [{document_id}] Provider Infrastructure / Transport Error during evaluation: {infra_error_msg}")
                target_fields = get_fields_for_record(gold)
                extracted_record = {
                    "document_metadata": {"document_id": document_id, "evaluation_error": "LLMTransportError"},
                    **{f: {"value": None, "evidence": [], "confidence": 0.0, "verification_status": "not_found"} for f in target_fields}
                }
            except Exception as e:
                infra_error_msg = str(e)
                target_fields = get_fields_for_record(gold)
                extracted_record = {
                    "document_metadata": {"document_id": document_id, "evaluation_error": str(e)},
                    **{f: {"value": None, "evidence": [], "confidence": 0.0, "verification_status": "not_found"} for f in target_fields}
                }

        latency = time.time() - start_time
        schema_valid, schema_errors = validate_extracted_record(extracted_record)

        target_fields = get_fields_for_record(gold)
        field_comparisons = []

        for fkey in target_fields:
            exp_f = gold.get(fkey, {})
            ext_f = extracted_record.get(fkey, {})
            fcomp = compare_field(fkey, exp_f, ext_f)
            field_comparisons.append(fcomp)

        return {
            "document_id": document_id,
            "domain": domain,
            "schema_valid": schema_valid and not is_infrastructure_failure,
            "schema_errors": schema_errors,
            "is_infrastructure_failure": is_infrastructure_failure,
            "infrastructure_error": infra_error_msg,
            "latency_seconds": latency,
            "extraction_attempts": attempts,
            "extracted_record": extracted_record,
            "field_comparisons": field_comparisons
        }

    def run_benchmark(self, document_ids: list[str] = None) -> dict:
        """
        Run full evaluation benchmark across specified or all discovered gold document IDs.
        """
        if document_ids is None:
            gold_files = [f for f in os.listdir(self.gold_dir) if f.endswith('.json')]
            document_ids = sorted([f.replace('.json', '') for f in gold_files])

        eval_results = []
        for doc_id in document_ids:
            res = self.evaluate_document(doc_id)
            eval_results.append(res)

        metrics = compute_metrics(eval_results)
        metrics["raw_results"] = eval_results
        return metrics

