import os
import json
import unittest
from unittest.mock import patch, MagicMock
import urllib.error
import socket
from src.extraction import (
    normalize_verification_statuses,
    validate_extracted_record,
    canonicalize_extracted_record,
    canonicalize_evidence_locator,
    canonicalize_benefit_amount,
    SCHEMA_FIELDS
)
from src.llm.gemini_client import GeminiLLMClient, clean_and_parse_json, sanitize_error_message
from src.llm.base_client import BaseLLMClient, UnrecoverableLLMError
from src.llm.llm_extractor import LLMExtractor
from src.llm.semantic_completeness import validate_semantic_completeness


class TestRobustnessUpgrades(unittest.TestCase):

    # 1. Missing value + no evidence -> canonical not_found
    def test_missing_value_no_evidence_canonical_not_found(self):
        partial_record = {
            "document_metadata": {"document_id": "TEST-01"},
            "age_criteria": {
                "value": None,
                "evidence": [],
                "confidence": 1.0,
                "verification_status": "unverified"
            }
        }
        canonical = canonicalize_extracted_record(partial_record, "TEST-01")
        self.assertEqual(canonical["age_criteria"]["verification_status"], "not_found")
        self.assertIsNone(canonical["age_criteria"]["value"])
        self.assertEqual(canonical["age_criteria"]["evidence"], [])

    # 2. Non-null value + no evidence -> must NOT be silently converted to not_found
    def test_non_null_value_no_evidence_not_converted_to_not_found(self):
        unsupported_claim_record = {
            "document_metadata": {"document_id": "TEST-01"},
            "scheme_name": {
                "value": "Unsupported Claim Scheme",
                "evidence": [],
                "confidence": 0.9,
                "verification_status": "verified"
            }
        }
        canonical = canonicalize_extracted_record(unsupported_claim_record, "TEST-01")
        self.assertEqual(canonical["scheme_name"]["value"], "Unsupported Claim Scheme")
        self.assertEqual(canonical["scheme_name"]["verification_status"], "verified")
        
        is_valid, errors = validate_extracted_record(canonical)
        self.assertFalse(is_valid)
        self.assertTrue(any("must contain at least 1 evidence item" in err for err in errors))

    # 3. Non-null value + evidence -> preserve normally
    def test_non_null_value_with_evidence_preserved(self):
        valid_record = {
            "document_metadata": {"document_id": "TEST-01"},
            "scheme_name": {
                "value": "Valid Grounded Scheme",
                "evidence": [{"text": "Valid Grounded Scheme", "locator": "sec 1"}],
                "confidence": 1.0,
                "verification_status": "verified"
            }
        }
        canonical = canonicalize_extracted_record(valid_record, "TEST-01")
        self.assertEqual(canonical["scheme_name"]["value"], "Valid Grounded Scheme")
        self.assertEqual(canonical["scheme_name"]["verification_status"], "verified")

    # 4. String locator is normalized into the exact schema-compatible locator object
    def test_string_locator_normalized_to_object(self):
        str_loc = "GOV-E-01-sec1"
        norm = canonicalize_evidence_locator(str_loc)
        self.assertIsInstance(norm, dict)
        self.assertEqual(norm.get("section"), "GOV-E-01-sec1")

    # 5. Already-valid locator objects remain unchanged
    def test_valid_locator_object_unchanged(self):
        dict_loc = {"page": 2, "section": "Table 1"}
        norm = canonicalize_evidence_locator(dict_loc)
        self.assertEqual(norm, dict_loc)

    # 6. Multi-component benefit_amount strings are conservatively converted into lists
    def test_multi_component_benefit_string_to_list(self):
        multi_str = "Tuition Fee Support; Maintenance Allowance Rs 10000; Laptop Grant Rs 45000"
        res = canonicalize_benefit_amount(multi_str)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 3)

    # 7. Normal single-value strings are not incorrectly split
    def test_single_value_benefit_string_not_split(self):
        single_str = "Rs. 2.50 lakh per annum"
        res = canonicalize_benefit_amount(single_str)
        self.assertEqual(res, single_str)

    # 8. Benefit genuinely absent -> not_found remains valid
    def test_semantic_completeness_benefit_absent_valid(self):
        chunks = [{"text": "This document describes general portal guidelines with no financial terms."}]
        record = {"benefit_amount": {"value": None, "evidence": [], "confidence": 0.0, "verification_status": "not_found"}}
        is_complete, errors = validate_semantic_completeness(record, chunks)
        self.assertTrue(is_complete)
        self.assertEqual(len(errors), 0)

    # 9. Benefit present in chunks but output is not_found -> semantic completeness error
    def test_semantic_completeness_benefit_present_triggers_error(self):
        chunks = [{"text": "The scheme provides tuition fee waiver and maintenance allowance of Rs 10000 per year."}]
        record = {"benefit_amount": {"value": None, "evidence": [], "confidence": 0.0, "verification_status": "not_found"}}
        is_complete, errors = validate_semantic_completeness(record, chunks)
        self.assertFalse(is_complete)
        self.assertTrue(any("SemanticCompletenessError" in err for err in errors))

    # 10. Retry feedback appended correctly for semantic completeness error
    def test_semantic_completeness_retry_feedback_appended(self):
        attempt_prompts = []

        class CompletenessMockClient(BaseLLMClient):
            def generate_structured_output(self, prompt, schema):
                attempt_prompts.append(prompt)
                if len(attempt_prompts) == 1:
                    # Attempt 1 returns benefit_amount as not_found
                    rec = {f: {"value": "V", "evidence": [{"text": "V", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"} for f in SCHEMA_FIELDS}
                    rec["benefit_amount"] = {"value": None, "evidence": [], "confidence": 0.0, "verification_status": "not_found"}
                    return rec
                
                # Attempt 2 returns multi-component benefit list
                rec = {f: {"value": "V", "evidence": [{"text": "V", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"} for f in SCHEMA_FIELDS}
                rec["benefit_amount"] = {
                    "value": ["Tuition fee waiver", "Maintenance allowance Rs 10000"],
                    "evidence": [
                        {"text": "tuition fee waiver", "locator": {"section": "Benefits"}},
                        {"text": "maintenance allowance", "locator": {"section": "Benefits"}}
                    ],
                    "confidence": 1.0,
                    "verification_status": "verified"
                }
                return rec

            def generate_text(self, prompt):
                return ""

        extractor = LLMExtractor(llm_client=CompletenessMockClient(), max_retries=2)
        # Pass document artifact containing tuition fee & maintenance allowance keywords in chunks
        fake_artifact = {
            "content_type": "HTML",
            "source_url": "http://test",
            "sections": [{"title": "Benefits", "content": "The scheme provides tuition fee waiver and maintenance allowance of Rs 10000."}]
        }
        with patch('src.llm.llm_extractor.segment_document') as mock_seg:
            mock_seg.return_value = [{"text": "tuition fee waiver and maintenance allowance of Rs 10000", "metadata": {"section": "Benefits"}}]
            rec = extractor.extract("GENERIC-DOC-99", fake_artifact)

        self.assertEqual(len(attempt_prompts), 2)
        self.assertIn("[PREVIOUS ATTEMPT FAILED SEMANTIC COMPLETENESS VALIDATION]", attempt_prompts[1])
        self.assertIsInstance(rec["benefit_amount"]["value"], list)
        self.assertEqual(len(rec["benefit_amount"]["value"]), 2)

    # Test A: Transport Timeout Retry (Isolated Client-level Test)
    @patch('time.sleep')
    @patch('urllib.request.urlopen')
    def test_transport_timeout_retry(self, mock_urlopen, mock_sleep):
        mock_urlopen.side_effect = socket.timeout("The read operation timed out")
        client = GeminiLLMClient(api_key="secret_test_key_xyz987", model="gemini-1.5-flash", timeout=10)

        with self.assertRaises(ValueError) as ctx:
            client.generate_structured_output("test prompt", {})

        err_msg = str(ctx.exception)
        self.assertIn("timed out", err_msg)
        self.assertEqual(mock_urlopen.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)
        self.assertNotIn("secret_test_key_xyz987", err_msg)

    # Test B: Semantic / Malformed Output Retry (Isolated Extractor-level Test)
    def test_semantic_malformed_output_retry(self):
        attempt_prompts = []

        class MalformedMockClient(BaseLLMClient):
            def generate_structured_output(self, prompt, schema):
                attempt_prompts.append(prompt)
                return {"invalid_key": "bad_data"}

            def generate_text(self, prompt):
                return ""

        extractor = LLMExtractor(llm_client=MalformedMockClient(), max_retries=2)
        
        with self.assertRaises(ValueError) as ctx:
            extractor.extract("GOV-E-01", {"content_type": "HTML", "source_url": "http://test"})

        self.assertIn("failed for [GOV-E-01] after 3 attempts", str(ctx.exception))
        self.assertEqual(len(attempt_prompts), 3)
        self.assertGreater(len(attempt_prompts[1]), len(attempt_prompts[0]))
        self.assertIn("[PREVIOUS ATTEMPT FAILED VALIDATION]", attempt_prompts[1])
        self.assertIn("[PREVIOUS ATTEMPT FAILED VALIDATION]", attempt_prompts[2])


if __name__ == '__main__':
    unittest.main()

