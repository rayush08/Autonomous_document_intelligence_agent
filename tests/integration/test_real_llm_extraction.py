import os
import json
import unittest
from datetime import datetime
from src.extraction import extract_document, validate_extracted_record, load_ingested_artifact
from src.llm.gemini_client import GeminiLLMClient
from src.llm.llm_extractor import LLMExtractor
from src.llm.evidence_verifier import verify_evidence_against_document
from src.llm.segmentation import segment_document

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VAL_RUNS_DIR = os.path.join(BASE_DIR, "data", "government_schemes", "validation_runs")


class TestRealLLMExtractionIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api_key = os.environ.get("GEMINI_API_KEY")
        cls.run_real = os.environ.get("RUN_REAL_LLM_TESTS") == "1"
        
        if not cls.api_key or not cls.run_real:
            raise unittest.SkipTest(
                "Skipping real LLM integration tests: GEMINI_API_KEY environment variable or RUN_REAL_LLM_TESTS=1 is not set."
            )
            
        # Use dynamic model discovery and smoke testing rather than hardcoded defaults
        cls.client = GeminiLLMClient.create_auto_discovered_client(api_key=cls.api_key, verbose=True)
        cls.extractor = LLMExtractor(llm_client=cls.client)
        os.makedirs(VAL_RUNS_DIR, exist_ok=True)

    def save_validation_run_artifact(self, doc_id: str, rec: dict, is_valid: bool, audit_results: dict):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_file = os.path.join(VAL_RUNS_DIR, f"{timestamp}_{doc_id}_gemini_run.json")
        run_data = {
            "document_id": doc_id,
            "model_provider": self.client.model,
            "timestamp": datetime.now().isoformat(),
            "schema_valid": is_valid,
            "audit_results": audit_results,
            "extracted_record": rec
        }
        with open(run_file, 'w', encoding='utf-8') as f:
            json.dump(run_data, f, indent=2, ensure_ascii=False)
        return run_file

    def test_real_gemini_extraction_gov_e01(self):
        doc_id = "GOV-E-01"
        rec = extract_document(doc_id, extractor=self.extractor)
        is_valid, errors = validate_extracted_record(rec)
        self.assertTrue(is_valid, f"GOV-E-01 real Gemini extraction schema invalid: {errors}")
        
        artifact = load_ingested_artifact(doc_id)
        chunks = segment_document(doc_id, artifact)
        
        verified_count = 0
        not_found_count = 0
        for fname, fobj in rec.items():
            if fname == 'document_metadata': continue
            status = fobj.get('verification_status')
            if status == 'verified': verified_count += 1
            elif status == 'not_found': not_found_count += 1

        audit = {"total_fields": 17, "verified_fields": verified_count, "not_found_fields": not_found_count}
        self.save_validation_run_artifact(doc_id, rec, is_valid, audit)

    def test_real_gemini_extraction_gov_m02(self):
        doc_id = "GOV-M-02"
        rec = extract_document(doc_id, extractor=self.extractor)
        is_valid, errors = validate_extracted_record(rec)
        self.assertTrue(is_valid, f"GOV-M-02 real Gemini extraction schema invalid: {errors}")
        
        b_val = rec.get("benefit_amount", {}).get("value")
        self.assertIsInstance(b_val, list, "GOV-M-02 benefit_amount must preserve multi-component list")
        self.assertGreaterEqual(len(b_val), 4, "GOV-M-02 benefit_amount must preserve 4 financial package components")

        audit = {"total_fields": 17, "benefit_components_count": len(b_val)}
        self.save_validation_run_artifact(doc_id, rec, is_valid, audit)

    def test_real_gemini_extraction_gov_m03(self):
        doc_id = "GOV-M-03"
        rec = extract_document(doc_id, extractor=self.extractor)
        is_valid, errors = validate_extracted_record(rec)
        self.assertTrue(is_valid, f"GOV-M-03 real Gemini extraction schema invalid: {errors}")

        # PDF page locators audit
        for fname, fobj in rec.items():
            if fname == 'document_metadata': continue
            for ev in fobj.get('evidence', []):
                loc = ev.get('locator', {})
                if 'page' in loc:
                    page_num = loc['page']
                    self.assertGreaterEqual(page_num, 1)
                    self.assertLessEqual(page_num, 29)

        # Missing fields audit
        for missing_f in ['education_level', 'income_criteria', 'age_criteria', 'academic_criteria']:
            self.assertEqual(rec[missing_f]['verification_status'], 'not_found')
            self.assertIsNone(rec[missing_f]['value'])

        audit = {"total_fields": 17, "pdf_page_range_valid": True}
        self.save_validation_run_artifact(doc_id, rec, is_valid, audit)


if __name__ == '__main__':
    unittest.main()

