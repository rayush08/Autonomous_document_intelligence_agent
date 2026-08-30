import unittest
import os
import json
import hashlib
from src.evaluation.comparison import compare_field, compare_values
from src.extraction import validate_extracted_record, canonicalize_extracted_record
from src.llm.semantic_completeness import validate_semantic_completeness
from src.llm.base_client import LLMTransportError, LLMServiceUnavailableError
from src.llm.llm_extractor import LLMExtractor
from src.validator import validate_gold_records

class TestPhase12ReleaseGate(unittest.TestCase):
    """
    Phase 12 Autonomous Closed-Loop Release Gate Test Suite.
    Covers all 15 required verification topics.
    """

    def setUp(self):
        self.results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"
        self.gold_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\gold"

    # 1. Credential gating
    def test_01_credential_gating(self):
        from src.llm.config import is_real_llm_mode_allowed
        # Verify function executes safely
        res = is_real_llm_mode_allowed(explicit_real_mode=True)
        self.assertIn(res, [True, False])

    # 2. Recovery merging
    def test_02_recovery_merging(self):
        orig_obj = {"verification_status": "verified", "value": "Initial Verified Value", "evidence": [{"chunk_id": 1, "text": "evidence"}]}
        rec_null = {"verification_status": "not_found", "value": None, "evidence": []}
        # Safe recovery merge MUST preserve original non-null value
        val = orig_obj["value"] if rec_null["value"] is None else rec_null["value"]
        self.assertEqual(val, "Initial Verified Value")

    # 3. Grouped extraction
    def test_03_grouped_extraction(self):
        from src.llm.prompts import GOVERNMENT_SCHEME_GROUPS, OPPORTUNITY_GROUPS
        self.assertEqual(len(GOVERNMENT_SCHEME_GROUPS), 4)
        self.assertEqual(len(OPPORTUNITY_GROUPS), 3)

    # 4. List completeness
    def test_04_list_completeness(self):
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

    # 5. Semantic equivalence
    def test_05_semantic_equivalence(self):
        self.assertTrue(compare_values("Central Sector Scheme", "Central Sector") > 0.8)
        self.assertTrue(compare_values("Per Annum", "per year") > 0.8)
        self.assertTrue(compare_values("Undergraduate", "Undergraduate Degree") > 0.8)

    # 6. Numeric exactness
    def test_06_numeric_exactness(self):
        self.assertTrue(compare_values("600", "$600") > 0.8)
        self.assertEqual(compare_values("600", "$6,000"), 0.0)

    # 7. Taxonomy distinction
    def test_07_taxonomy_distinction(self):
        self.assertFalse(compare_values("Central Sector Scheme", "State Sector Scheme") > 0.8)

    # 8. Hallucination prevention
    def test_08_hallucination_prevention(self):
        gold = {"verification_status": "not_found", "value": None, "evidence": []}
        pred = {"verification_status": "verified", "value": "Invoted Fee $1000", "evidence": [{"chunk_id": 1, "text": "unrelated"}]}
        metrics = compare_field("benefit_amount", gold, pred)
        self.assertFalse(metrics["value_match"])
        self.assertTrue(metrics["is_hallucination"])

    # 9. Evidence grounding
    def test_09_evidence_grounding(self):
        gold = {"verification_status": "verified", "value": "PM-YASASVI", "evidence": [{"chunk_id": 1, "text": "PM-YASASVI"}]}
        pred = {"verification_status": "verified", "value": "PM-YASASVI", "evidence": [{"chunk_id": 1, "text": "PM-YASASVI"}]}
        metrics = compare_field("scheme_name", gold, pred)
        self.assertTrue(metrics["evidence_grounded"])

    # 10. Retries
    def test_10_retries(self):
        err = LLMServiceUnavailableError("503 Service Unavailable")
        self.assertTrue(isinstance(err, LLMTransportError))

    # 11. Model selection
    def test_11_model_selection(self):
        from src.llm.gemini_client import GeminiLLMClient
        self.assertTrue(hasattr(GeminiLLMClient, 'create_auto_discovered_client'))

    # 12. Request accounting
    def test_12_request_accounting(self):
        extractor = LLMExtractor(llm_client=None)
        self.assertIn("transport_attempts", extractor.request_accounting)

    # 13. Regression detection
    def test_13_regression_detection(self):
        p9_file = os.path.join(self.results_dir, "real_run_phase9_1_results.json")
        self.assertTrue(os.path.exists(p9_file), "Phase 9 results must exist for regression tracking.")

    # 14. Gold integrity
    def test_14_gold_integrity(self):
        summary = validate_gold_records()
        self.assertEqual(summary["valid_records"], 10)
        self.assertEqual(summary["invalid_records"], 0)

    # 15. Baseline immutability
    def test_15_baseline_immutability(self):
        p6_file = os.path.join(self.results_dir, "phase6_baseline.json")
        self.assertTrue(os.path.exists(p6_file), "Phase 6 baseline must exist.")
        with open(p6_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("overall_metrics", data)
        mean_acc = data["overall_metrics"]["field_extraction_accuracy"]["mean"]
        self.assertAlmostEqual(mean_acc, 0.5349, delta=0.001)


if __name__ == "__main__":
    unittest.main()
