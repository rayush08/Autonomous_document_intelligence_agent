import os
import json
import unittest
from src.extraction import BaseExtractor, extract_document, load_ingested_artifact
from src.llm.base_client import BaseLLMClient
from src.llm.mock_client import MockLLMClient
from src.llm.llm_extractor import LLMExtractor
from src.llm.evidence_verifier import verify_evidence_against_document
from src.llm.segmentation import segment_document

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "data", "government_schemes", "documents")


class TestLLMExtraction(unittest.TestCase):
    def setUp(self):
        self.mock_client = MockLLMClient()
        self.extractor = LLMExtractor(llm_client=self.mock_client)

    # 1. LLMExtractor implements BaseExtractor
    def test_llm_extractor_implements_base_extractor(self):
        self.assertIsInstance(self.extractor, BaseExtractor)

    # 2. Extraction returns a schema-valid record
    def test_extraction_returns_schema_valid_record(self):
        rec = extract_document("GOV-E-01", extractor=self.extractor)
        self.assertEqual(rec["document_metadata"]["document_id"], "GOV-E-01")
        self.assertIsNotNone(rec.get("scheme_name", {}).get("value"))

    # 3. Evidence snippets are verified against source content
    def test_evidence_snippets_verified_against_source(self):
        artifact = load_ingested_artifact("GOV-E-01")
        chunks = segment_document("GOV-E-01", artifact)
        
        valid_field = {
            "value": "Post-Matric Scholarship for SC Students",
            "evidence": [{"text": "Post-Matric Scholarship for SC Students", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc"}}],
            "confidence": 1.0,
            "verification_status": "verified"
        }
        res, is_grounded = verify_evidence_against_document("scheme_name", valid_field, chunks)
        self.assertTrue(is_grounded)
        self.assertEqual(res["verification_status"], "verified")

    # 4. Invalid / hallucinated evidence snippets are detected
    def test_invalid_evidence_snippets_detected(self):
        artifact = load_ingested_artifact("GOV-E-01")
        chunks = segment_document("GOV-E-01", artifact)
        
        hallucinated_field = {
            "value": "Hallucinated Scholarship Claim",
            "evidence": [{"text": "This text does not exist anywhere in the source document chunk 12345", "locator": {"url": "https://myscheme.gov.in/schemes/pm-pms-sc"}}],
            "confidence": 1.0,
            "verification_status": "verified"
        }
        res, is_grounded = verify_evidence_against_document("scheme_name", hallucinated_field, chunks)
        self.assertFalse(is_grounded)
        self.assertEqual(res["verification_status"], "not_found", "Hallucinated evidence snippet with zero grounded items must be converted to not_found")
        self.assertIsNone(res["value"], "Value must be set to null for ungrounded claim")

    # 5. PDF page locators are preserved
    def test_pdf_page_locators_preserved(self):
        rec = extract_document("GOV-M-03", extractor=self.extractor)
        ev_item = rec["scheme_name"]["evidence"][0]
        self.assertIn("page", ev_item["locator"])
        self.assertEqual(ev_item["locator"]["page"], 1)

    # 6. GOV-M-02 preserves all 4 financial benefit components
    def test_gov_m02_preserves_four_financial_components(self):
        rec = extract_document("GOV-M-02", extractor=self.extractor)
        b_val = rec["benefit_amount"]["value"]
        self.assertIsInstance(b_val, list)
        self.assertEqual(len(b_val), 4, "GOV-M-02 must preserve all 4 financial package components")

    # 7. GOV-M-03 preserves multiple capacity-based CFA amounts
    def test_gov_m03_preserves_capacity_cfa_amounts(self):
        rec = extract_document("GOV-M-03", extractor=self.extractor)
        b_val = rec["benefit_amount"]["value"]
        self.assertIsInstance(b_val, list)
        self.assertGreaterEqual(len(b_val), 3)

    # 8. not_found fields have null values and empty evidence
    def test_not_found_fields_have_null_values(self):
        rec = extract_document("GOV-E-01", extractor=self.extractor)
        age_field = rec["age_criteria"]
        self.assertEqual(age_field["verification_status"], "not_found")
        self.assertIsNone(age_field["value"])
        self.assertEqual(len(age_field["evidence"]), 0)

    # 9. Mock provider operates offline without network access
    def test_mock_provider_operates_offline(self):
        # Verify MockLLMClient requires no API key or network initialization
        client = MockLLMClient()
        output = client.generate_structured_output("GOV-E-01 test prompt", {})
        self.assertIsInstance(output, dict)

    # 10. Invalid LLM output triggers controlled retry
    def test_invalid_llm_output_triggers_retry(self):
        attempt_counter = {"count": 0}
        
        class RetryMockClient(BaseLLMClient):
            def generate_structured_output(self, prompt, schema):
                attempt_counter["count"] += 1
                if attempt_counter["count"] == 1:
                    return {"invalid_key": "bad_data"}
                gold_path = os.path.join(BASE_DIR, "evaluation", "gold", "GOV-E-01.json")
                with open(gold_path, 'r', encoding='utf-8') as f:
                    return json.load(f)

            def generate_text(self, prompt):
                return ""

        retry_extractor = LLMExtractor(llm_client=RetryMockClient(), max_retries=2)
        rec = extract_document("GOV-E-01", extractor=retry_extractor)
        self.assertEqual(attempt_counter["count"], 2, "Extractor must retry after first invalid LLM output")
        self.assertIsNotNone(rec.get("scheme_name", {}).get("value"))

    # 11. Retry limit is enforced
    def test_retry_limit_enforced(self):
        class AlwaysFailingMockClient(BaseLLMClient):
            def generate_structured_output(self, prompt, schema):
                return {"invalid_key": "bad_data"}
            def generate_text(self, prompt):
                return ""

        failing_extractor = LLMExtractor(llm_client=AlwaysFailingMockClient(), max_retries=2)
        with self.assertRaises(ValueError) as ctx:
            extract_document("GOV-E-01", extractor=failing_extractor)
        self.assertIn("failed for [GOV-E-01] after 3 attempts", str(ctx.exception))

    # 12. Source contamination prevention
    def test_source_contamination_prevention(self):
        artifact = load_ingested_artifact("GOV-M-02")
        chunks = segment_document("GOV-M-02", artifact)
        
        contaminated_field = {
            "value": "Pradhan Mantri Matru Vandana Yojana benefit of Rs 5000",
            "evidence": [{"text": "Pradhan Mantri Matru Vandana Yojana text snippet", "locator": {"url": "https://www.myscheme.gov.in/schemes/pmy-tcc"}}],
            "confidence": 1.0,
            "verification_status": "verified"
        }
        res, is_grounded = verify_evidence_against_document("benefit_amount", contaminated_field, chunks)
        self.assertFalse(is_grounded, "Contaminated/out-of-context claim snippet must be converted to not_found")
        self.assertEqual(res["verification_status"], "not_found")
        self.assertIsNone(res["value"])


if __name__ == '__main__':
    unittest.main()

