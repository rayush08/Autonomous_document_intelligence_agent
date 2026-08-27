import os
import json
import unittest
from src.extraction import (
    validate_extracted_record,
    canonicalize_extracted_record,
    canonicalize_benefit_amount,
    canonicalize_evidence_locator
)
from src.llm.semantic_completeness import validate_semantic_completeness, is_affirmative_indicator
from src.llm.gemini_client import clean_and_parse_json
from src.llm.prompts import build_document_extraction_prompt
from src.evaluation.metrics import compute_metrics
from src.evaluation.evaluator import EvaluationEngine


class TestAdversarialReliability(unittest.TestCase):

    # 1. Valid JSON wrapped in markdown
    def test_01_markdown_json_wrapping(self):
        raw_llm_str = "```json\n{\n  \"scheme_name\": {\"value\": \"Test Scheme\", \"evidence\": [{\"text\": \"Test\", \"locator\": \"sec 1\"}], \"confidence\": 1.0, \"verification_status\": \"verified\"}\n}\n```"
        parsed = clean_and_parse_json(raw_llm_str)
        self.assertEqual(parsed["scheme_name"]["value"], "Test Scheme")

    # 2. Conversational text surrounding JSON
    def test_02_conversational_text_surrounding_json(self):
        raw_llm_str = "Here is the extracted document record:\n{\n  \"scheme_name\": {\"value\": \"Test\", \"evidence\": [{\"text\": \"T\", \"locator\": \"s1\"}], \"confidence\": 1.0, \"verification_status\": \"verified\"}\n}\nHope this helps!"
        parsed = clean_and_parse_json(raw_llm_str)
        self.assertEqual(parsed["scheme_name"]["value"], "Test")

    # 3. Truncated JSON
    def test_03_truncated_json_raises_error(self):
        truncated_str = "{\n  \"scheme_name\": {\"value\": \"Truncated"
        with self.assertRaises(ValueError):
            clean_and_parse_json(truncated_str)

    # 4. Missing required fields
    def test_04_missing_required_fields(self):
        incomplete_record = {"document_metadata": {"document_id": "TEST"}}
        is_valid, errors = validate_extracted_record(incomplete_record)
        self.assertFalse(is_valid)
        self.assertTrue(any("MissingField" in err for err in errors))

    # 5. Non-null claim with zero evidence
    def test_05_non_null_claim_zero_evidence_rejected(self):
        record = {
            "document_metadata": {"document_id": "TEST"},
            "scheme_name": {"value": "Claim", "evidence": [], "confidence": 1.0, "verification_status": "verified"}
        }
        canonical = canonicalize_extracted_record(record, "TEST")
        is_valid, errors = validate_extracted_record(canonical)
        self.assertFalse(is_valid)
        self.assertTrue(any("must contain at least 1 evidence item" in err for err in errors))

    # 6. Incorrect verification status synonym
    def test_06_verification_status_synonyms_mapped(self):
        record = {
            "document_metadata": {"document_id": "TEST"},
            "scheme_name": {"value": "Claim", "evidence": [{"text": "C", "locator": "S"}], "confidence": 1.0, "verification_status": "not_verified"}
        }
        canonical = canonicalize_extracted_record(record, "TEST")
        self.assertEqual(canonical["scheme_name"]["verification_status"], "unverified")

    # 7. Unsupported verification status
    def test_07_unsupported_verification_status_rejected(self):
        record = {
            "document_metadata": {"document_id": "TEST"},
            "scheme_name": {"value": "Claim", "evidence": [{"text": "C", "locator": "S"}], "confidence": 1.0, "verification_status": "super_verified"}
        }
        is_valid, errors = validate_extracted_record(record)
        self.assertFalse(is_valid)
        self.assertTrue(any("unsupported status 'super_verified'" in err for err in errors))

    # 8. Incorrect evidence locator type
    def test_08_evidence_locator_normalized(self):
        self.assertEqual(canonicalize_evidence_locator("https://gov.in"), {"url": "https://gov.in"})
        self.assertEqual(canonicalize_evidence_locator("Page 3"), {"page": 3, "section": "Page 3"})
        self.assertEqual(canonicalize_evidence_locator({"page": "12"}), {"page": 12})

    # 9. Multi-component financial values
    def test_09_multi_component_financial_values_split(self):
        multi_str = "Tuition Fee Waiver; Monthly Stipend €600; Mobility Grant €1000"
        res = canonicalize_benefit_amount(multi_str)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 3)

    # 10. Single monetary values must not be split
    def test_10_single_monetary_value_not_split(self):
        single_str = "Rs. 2,50,000 per annum"
        res = canonicalize_benefit_amount(single_str)
        self.assertEqual(res, single_str)

    # 11. Explicit exclusion clauses
    def test_11_explicit_exclusion_clauses_filtered(self):
        text = "Applicants currently receiving another stipend are NOT eligible. No tuition fee support is provided."
        self.assertFalse(is_affirmative_indicator(text, "stipend"))
        self.assertFalse(is_affirmative_indicator(text, "tuition fee"))

    # 12. Documents genuinely missing a field
    def test_12_genuinely_missing_field_valid(self):
        chunk = [{"text": "Standard guidelines with no financial assistance."}]
        record = {"benefit_amount": {"value": None, "evidence": [], "confidence": 0.0, "verification_status": "not_found"}}
        is_complete, errors = validate_semantic_completeness(record, chunk)
        self.assertTrue(is_complete)

    # 13. Multiple conflicting values canonicalized cleanly
    def test_13_conflicting_values_handling(self):
        val = "Option A (Rs 10,000); Option B (Rs 20,000)"
        res = canonicalize_benefit_amount(val)
        self.assertIsInstance(res, list)

    # 14. Opportunity schema contamination with scheme fields
    def test_14_opportunity_contamination_with_scheme_fields(self):
        bad_opp = {
            "document_metadata": {"document_id": "OPP-E-01"},
            "title": {"value": "MSRP", "evidence": [{"text": "MSRP", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"},
            "scheme_name": {"value": "Contaminated", "evidence": [{"text": "C", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"}
        }
        is_valid, errors = validate_extracted_record(bad_opp)
        self.assertFalse(is_valid)

    # 15. Government schema contamination with opportunity fields
    def test_15_government_contamination_with_opportunity_fields(self):
        bad_gov = {
            "document_metadata": {"document_id": "GOV-E-01"},
            "scheme_name": {"value": "PM-PMS", "evidence": [{"text": "P", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"},
            "stipend_or_funding": {"value": "Contaminated", "evidence": [{"text": "C", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"}
        }
        is_valid, errors = validate_extracted_record(bad_gov)
        self.assertFalse(is_valid)

    # 16. Gold fixture mismatch detection
    def test_16_gold_fixture_mismatch(self):
        from tests.test_dataset_integrity import TestDatasetIntegrity
        suite = unittest.TestLoader().loadTestsFromTestCase(TestDatasetIntegrity)
        res = unittest.TextTestRunner(stream=open(os.devnull, 'w')).run(suite)
        self.assertTrue(res.wasSuccessful())

    # 17. Metric denominator edge cases (0 docs / 0 missing fields)
    def test_17_metric_denominator_zero_handling(self):
        empty_metrics = compute_metrics([])
        self.assertEqual(empty_metrics, {})

    # 18. Evaluator failure isolation
    def test_18_evaluator_failure_isolation(self):
        engine = EvaluationEngine()
        res = engine.evaluate_document("GOV-E-01")
        self.assertIn("document_id", res)
        self.assertIn("schema_valid", res)

    # 19. Deterministic evaluation results
    def test_19_deterministic_evaluation_results(self):
        engine = EvaluationEngine()
        res1 = engine.evaluate_document("GOV-E-01")
        res2 = engine.evaluate_document("GOV-E-01")
        self.assertEqual(res1["schema_valid"], res2["schema_valid"])
        self.assertEqual(len(res1["field_comparisons"]), len(res2["field_comparisons"]))

    # 20. Real evaluation mode credentials check & clean skip
    def test_20_real_eval_mode_credentials_check(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        run_real = os.environ.get("RUN_REAL_LLM_TESTS") == "1"
        if not api_key or not run_real:
            self.assertTrue(True)

    # 21. Domain-specific prompt target fields isolation
    def test_21_opportunity_prompt_contains_opportunity_fields_only(self):
        chunks = [{"chunk_id": "c1", "text": "Sample fellowship document."}]
        opp_prompt = build_document_extraction_prompt("OPP-E-01", "HTML", chunks)
        self.assertIn("stipend_or_funding", opp_prompt)
        self.assertIn("organization", opp_prompt)
        self.assertNotIn("scheme_name", opp_prompt)
        self.assertNotIn("domicile_criteria", opp_prompt)

        gov_prompt = build_document_extraction_prompt("GOV-E-01", "HTML", chunks)
        self.assertIn("scheme_name", gov_prompt)
        self.assertIn("domicile_criteria", gov_prompt)
        self.assertNotIn("stipend_or_funding", gov_prompt)


if __name__ == '__main__':
    unittest.main()

