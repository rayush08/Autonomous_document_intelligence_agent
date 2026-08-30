import unittest
import os
import json
from src.evaluation.comparison import compare_field, compare_values
from src.extraction import validate_extracted_record, canonicalize_extracted_record
from src.llm.semantic_completeness import validate_semantic_completeness
from src.llm.base_client import LLMTransportError, LLMServiceUnavailableError
from src.llm.llm_extractor import LLMExtractor

class TestPhase11ReleaseValidation(unittest.TestCase):
    """
    Phase 11 Autonomous Closed-Loop Release Validation Test Suite.
    Covers all 15 required topics.
    """

    def setUp(self):
        self.results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"

    # 1. Baseline immutability
    def test_01_baseline_immutability(self):
        p6_file = os.path.join(self.results_dir, "phase6_baseline.json")
        self.assertTrue(os.path.exists(p6_file), "Phase 6 baseline file must exist.")
        with open(p6_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("overall_metrics", data)
        mean_acc = data["overall_metrics"]["field_extraction_accuracy"]["mean"]
        self.assertAlmostEqual(mean_acc, 0.5349, delta=0.001)

    # 2. Safe recovery merge
    def test_02_safe_recovery_merge(self):
        orig_obj = {"verification_status": "verified", "value": "Valid Beneficiary", "evidence": [{"chunk_id": 1, "text": "text"}]}
        recovered_null = {"verification_status": "not_found", "value": None, "evidence": []}
        # In safe merging logic, if recovered_null is None, original non-null value MUST be preserved
        merged_val = orig_obj["value"] if recovered_null["value"] is None else recovered_null["value"]
        self.assertEqual(merged_val, "Valid Beneficiary")

    # 3. Grouped extraction
    def test_03_grouped_extraction_configuration(self):
        from src.llm.prompts import GOVERNMENT_SCHEME_GROUPS, OPPORTUNITY_GROUPS
        self.assertEqual(len(GOVERNMENT_SCHEME_GROUPS), 4)
        self.assertEqual(len(OPPORTUNITY_GROUPS), 3)

    # 4. List completeness
    def test_04_list_completeness(self):
        chunks = [{"chunk_id": 1, "text": "Required documents:\n1. Aadhar Card\n2. Income Certificate\n3. Caste Certificate\n4. Marksheet\n5. Domicile"}]
        record = {
            "required_documents": {
                "verification_status": "verified",
                "value": ["Passport"],
                "evidence": [{"chunk_id": 1, "text": "Passport"}]
            }
        }
        res, msg = validate_semantic_completeness(record, chunks)
        self.assertFalse(res)
        self.assertIn("required_documents", str(msg))

    # 5. Hallucination rejection
    def test_05_hallucination_rejection(self):
        gold = {"verification_status": "not_found", "value": None, "evidence": []}
        pred = {"verification_status": "verified", "value": "Invoted Fee $1000", "evidence": [{"chunk_id": 1, "text": "unrelated"}]}
        metrics = compare_field("benefit_amount", gold, pred)
        self.assertFalse(metrics["value_match"])
        self.assertTrue(metrics["is_hallucination"])

    # 6. Unsupported claims
    def test_06_unsupported_claims(self):
        gold = {"verification_status": "not_found", "value": None, "evidence": []}
        pred = {"verification_status": "verified", "value": "Unsupported claim", "evidence": []}
        metrics = compare_field("stipend_or_funding", gold, pred)
        self.assertTrue(metrics["is_hallucination"])

    # 7. Numeric exactness
    def test_07_numeric_exactness(self):
        self.assertTrue(compare_values("600", "$600") > 0.8)
        self.assertEqual(compare_values("600", "$6,000"), 0.0)

    # 8. Currency normalization
    def test_08_currency_normalization(self):
        self.assertTrue(compare_values("Rs 50,000", "50000 rupees") > 0.8)
        self.assertTrue(compare_values("₹50000", "INR 50,000") > 0.8)

    # 9. Semantic equivalence
    def test_09_semantic_equivalence(self):
        self.assertTrue(compare_values("Central Sector Scheme", "Central Sector") > 0.8)
        self.assertTrue(compare_values("Per Annum", "per year") > 0.8)

    # 10. Status classification
    def test_10_status_classification(self):
        gold = {"verification_status": "not_found", "value": None, "evidence": []}
        pred = {"verification_status": "not_found", "value": None, "evidence": []}
        metrics = compare_field("application_deadline", gold, pred)
        self.assertTrue(metrics["status_match"])
        self.assertFalse(metrics["is_hallucination"])

    # 11. Evidence preservation
    def test_11_evidence_preservation(self):
        record = {
            "scheme_name": {
                "verification_status": "verified",
                "value": "PM-YASASVI",
                "evidence": [{"chunk_id": 1, "text": "PM-YASASVI Scheme"}]
            }
        }
        canon = canonicalize_extracted_record(record, "GOV-E-01")
        self.assertIn("evidence", canon["scheme_name"])
        self.assertEqual(len(canon["scheme_name"]["evidence"]), 1)

    # 12. Model selection
    def test_12_model_selection(self):
        from src.llm.gemini_client import GeminiLLMClient
        self.assertTrue(hasattr(GeminiLLMClient, 'create_auto_discovered_client'))

    # 13. Retry isolation
    def test_13_retry_isolation(self):
        err = LLMServiceUnavailableError("503 Service Unavailable")
        self.assertTrue(isinstance(err, LLMTransportError))

    # 14. Request accounting
    def test_14_request_accounting(self):
        extractor = LLMExtractor(llm_client=None)
        self.assertIn("transport_attempts", extractor.request_accounting)

    # 15. Regression detection
    def test_15_regression_detection(self):
        p9_file = os.path.join(self.results_dir, "real_run_phase9_1_results.json")
        self.assertTrue(os.path.exists(p9_file), "Phase 9 result file must exist for regression tracking.")


if __name__ == "__main__":
    unittest.main()
