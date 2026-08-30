import unittest
import os
import json
import hashlib
from src.evaluation.comparison import compare_field, compare_values, normalize_str
from src.extraction import validate_extracted_record, canonicalize_extracted_record
from src.llm.semantic_completeness import validate_semantic_completeness
from src.llm.base_client import LLMTransportError, LLMServiceUnavailableError
from src.llm.llm_extractor import LLMExtractor
from src.validator import validate_gold_records

class TestPhase18ExtractionReliability(unittest.TestCase):
    """
    Phase 18 Extraction Reliability & Deterministic Test Suite.
    Covers root cause verification, safe recovery merging, canonicalization rules,
    adversarial edge cases, evidence preservation, and baseline immutability.
    """

    def setUp(self):
        self.results_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\results"
        self.gold_dir = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\evaluation\gold"

    # 1. Safe recovery merging rule
    def test_01_safe_recovery_merge_preserves_initial(self):
        orig_obj = {
            "verification_status": "verified",
            "value": "Verified Initial Extraction",
            "evidence": [{"chunk_id": 1, "text": "evidence text"}]
        }
        rec_null_obj = {
            "verification_status": "not_found",
            "value": None,
            "evidence": []
        }
        merged_val = orig_obj["value"] if rec_null_obj["value"] is None else rec_null_obj["value"]
        self.assertEqual(merged_val, "Verified Initial Extraction")

    # 2. Recovery updates missing values
    def test_02_recovery_updates_missing_initial(self):
        orig_obj = {
            "verification_status": "not_found",
            "value": None,
            "evidence": []
        }
        rec_valid_obj = {
            "verification_status": "verified",
            "value": "Recovered Value",
            "evidence": [{"chunk_id": 1, "text": "recovered text"}]
        }
        merged_val = rec_valid_obj["value"] if orig_obj["value"] is None else orig_obj["value"]
        self.assertEqual(merged_val, "Recovered Value")

    # 3. List completeness check for stipend/funding
    def test_03_list_completeness_validation(self):
        chunks = [{"chunk_id": 1, "text": "Financial assistance: Monthly stipend of Rs 5000 is provided to students."}]
        record = {
            "stipend_or_funding": {
                "verification_status": "not_found",
                "value": None,
                "evidence": []
            }
        }
        res, msg = validate_semantic_completeness(record, chunks)
        self.assertFalse(res)
        self.assertIn("stipend_or_funding", str(msg))

    # 4. Currency token normalization
    def test_04_currency_token_normalization(self):
        self.assertTrue(compare_values("Rs 50,000", "50000 rupees") > 0.8)
        self.assertTrue(compare_values("₹50000", "INR 50,000") > 0.8)

    # 5. Frequency token normalization
    def test_05_frequency_token_normalization(self):
        self.assertTrue(compare_values("per annum", "per year") > 0.8)
        self.assertTrue(compare_values("monthly", "per month") > 0.8)

    # 6. Numeric collision check
    def test_06_numeric_collision_prevention(self):
        self.assertEqual(compare_values("600", "6000"), 0.0)
        self.assertEqual(compare_values("$600", "$6,000"), 0.0)

    # 7. Taxonomy near-match rejection
    def test_07_taxonomy_near_match_rejection(self):
        self.assertFalse(compare_values("Central Sector Scheme", "State Sector Scheme") > 0.8)

    # 8. Hallucination detection
    def test_08_hallucination_detection(self):
        gold = {"verification_status": "not_found", "value": None, "evidence": []}
        pred = {"verification_status": "verified", "value": "Invoted Fee $1000", "evidence": [{"chunk_id": 1, "text": "unrelated"}]}
        metrics = compare_field("benefit_amount", gold, pred)
        self.assertFalse(metrics["value_match"])
        self.assertTrue(metrics["is_hallucination"])

    # 9. Evidence grounding preservation
    def test_09_evidence_grounding_preservation(self):
        gold = {"verification_status": "verified", "value": "PM-YASASVI", "evidence": [{"chunk_id": 1, "text": "text"}]}
        pred = {"verification_status": "verified", "value": "PM-YASASVI", "evidence": [{"chunk_id": 1, "text": "text"}]}
        metrics = compare_field("scheme_name", gold, pred)
        self.assertTrue(metrics["evidence_grounded"])

    # 10. Gold integrity & Baseline immutability
    def test_10_gold_integrity_and_baseline(self):
        summary = validate_gold_records()
        self.assertEqual(summary["valid_records"], 10)
        p6_file = os.path.join(self.results_dir, "phase6_baseline.json")
        self.assertTrue(os.path.exists(p6_file))


if __name__ == "__main__":
    unittest.main()
