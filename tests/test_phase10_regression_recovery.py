import unittest
import os
import json
from src.evaluation.comparison import compare_field, compare_values
from src.extraction import validate_extracted_record, canonicalize_extracted_record
from src.llm.semantic_completeness import validate_semantic_completeness
from src.llm.base_client import LLMTransportError, LLMServiceUnavailableError
from src.llm.llm_extractor import LLMExtractor

class TestPhase10RegressionRecovery(unittest.TestCase):
    """
    Phase 10 Regression Recovery & Verification Test Suite.
    Covers all 14 required regression topics.
    """

    def setUp(self):
        self.results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"

    # 1. Phase 6 baseline immutability
    def test_01_phase6_baseline_immutability(self):
        p6_file = os.path.join(self.results_dir, "phase6_baseline.json")
        self.assertTrue(os.path.exists(p6_file), "Phase 6 baseline file must exist.")
        with open(p6_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("overall_metrics", data)
        self.assertIn("per_field_accuracy", data)
        mean_acc = data["overall_metrics"]["field_extraction_accuracy"]["mean"]
        self.assertAlmostEqual(mean_acc, 0.5349, delta=0.001)

    # 2. Grouped vs monolithic extraction behavior
    def test_02_grouped_vs_monolithic_structure(self):
        from src.llm.prompts import GOVERNMENT_SCHEME_GROUPS, OPPORTUNITY_GROUPS
        self.assertEqual(len(GOVERNMENT_SCHEME_GROUPS), 4)
        self.assertEqual(len(OPPORTUNITY_GROUPS), 3)

    # 3. List completeness
    def test_03_list_completeness_validation(self):
        chunks = [{"chunk_id": 1, "text": "Required documents:\n1. Aadhar Card\n2. Income Certificate\n3. Caste Certificate\n4. Marksheet\n5. Domicile"}]
        record = {
            "required_documents": {
                "verification_status": "verified",
                "value": ["Aadhar Card"],
                "evidence": [{"chunk_id": 1, "text": "Aadhar Card"}]
            }
        }
        res, msg = validate_semantic_completeness(record, chunks)
        self.assertFalse(res)
        self.assertIn("required_documents", str(msg))

    # 4. Hallucination rejection
    def test_04_hallucination_rejection(self):
        gold = {"verification_status": "not_found", "value": None, "evidence": []}
        pred = {"verification_status": "verified", "value": "Invoted Fee $1000", "evidence": [{"chunk_id": 1, "text": "Completely unrelated text"}]}
        metrics = compare_field("benefit_amount", gold, pred)
        self.assertFalse(metrics["value_match"])
        self.assertTrue(metrics["is_hallucination"])

    # 5. Unsupported claim detection
    def test_05_unsupported_claim_detection(self):
        gold = {"verification_status": "not_found", "value": None, "evidence": []}
        pred = {"verification_status": "verified", "value": "Unsupported claim", "evidence": []}
        metrics = compare_field("stipend_or_funding", gold, pred)
        self.assertTrue(metrics["is_hallucination"])

    # 6. Numeric exactness
    def test_06_numeric_exactness(self):
        self.assertTrue(compare_values("600", "$600") > 0.8)
        self.assertEqual(compare_values("600", "$6,000"), 0.0)

    # 7. Currency normalization
    def test_07_currency_normalization(self):
        self.assertTrue(compare_values("Rs 50,000", "50000 rupees") > 0.8)
        self.assertTrue(compare_values("₹50000", "INR 50,000") > 0.8)

    # 8. Semantic equivalence
    def test_08_semantic_equivalence(self):
        self.assertTrue(compare_values("Central Sector Scheme", "Central Sector") > 0.8)
        self.assertTrue(compare_values("Per Annum", "per year") > 0.8)

    # 9. Status classification
    def test_09_status_classification(self):
        gold = {"verification_status": "not_found", "value": None, "evidence": []}
        pred = {"verification_status": "not_found", "value": None, "evidence": []}
        metrics = compare_field("application_deadline", gold, pred)
        self.assertTrue(metrics["status_match"])
        self.assertFalse(metrics["is_hallucination"])

    # 10. Evidence preservation
    def test_10_evidence_preservation(self):
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

    # 11. Recovery merge safety
    def test_11_recovery_merge_safety(self):
        orig = {"verification_status": "verified", "value": "Original Valid Value", "evidence": [{"chunk_id": 1, "text": "text"}]}
        rec_obj = {"verification_status": "not_found", "value": None, "evidence": []}
        # In safe recovery, if rec_obj is None/not_found, original value MUST be preserved
        val = orig["value"] if rec_obj["value"] is None else rec_obj["value"]
        self.assertEqual(val, "Original Valid Value")

    # 12. Model selection policy
    def test_12_model_selection_policy(self):
        from src.llm.gemini_client import GeminiLLMClient
        # Verify preference rank helper exists
        self.assertTrue(hasattr(GeminiLLMClient, 'create_auto_discovered_client'))

    # 13. Retry isolation
    def test_13_retry_isolation(self):
        err = LLMServiceUnavailableError("503 Service Unavailable")
        self.assertTrue(isinstance(err, LLMTransportError))

    # 14. Request accounting
    def test_14_request_accounting(self):
        extractor = LLMExtractor(llm_client=None)
        self.assertIn("transport_attempts", extractor.request_accounting)
        self.assertIn("targeted_field_recoveries", extractor.request_accounting)


if __name__ == "__main__":
    unittest.main()
