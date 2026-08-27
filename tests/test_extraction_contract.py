import os
import json
import unittest
from src.extraction import (
    BaseExtractor,
    FixtureExtractor,
    extract_document,
    validate_extracted_record,
    load_ingested_artifact,
    ALLOWED_VERIFICATION_STATUSES,
    SCHEMA_FIELDS
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES_DIR = os.path.join(BASE_DIR, "tests", "fixtures", "extractions")


class TestExtractionContract(unittest.TestCase):
    def setUp(self):
        self.extractor = FixtureExtractor()

    # 1. Extraction result structure
    def test_extraction_result_structure(self):
        rec = extract_document("GOV-E-01", extractor=self.extractor)
        self.assertIn("document_metadata", rec)
        for field in SCHEMA_FIELDS:
            self.assertIn(field, rec, f"Missing field '{field}' in extracted record")
            f_obj = rec[field]
            self.assertIn("value", f_obj)
            self.assertIn("evidence", f_obj)
            self.assertIn("confidence", f_obj)
            self.assertIn("verification_status", f_obj)

    # 2. Allowed verification statuses
    def test_allowed_verification_statuses(self):
        rec = extract_document("GOV-M-02", extractor=self.extractor)
        for field in SCHEMA_FIELDS:
            status = rec[field]["verification_status"]
            self.assertIn(status, ALLOWED_VERIFICATION_STATUSES, f"Field '{field}' has invalid status '{status}'")

    # 3. Verified field requirements
    def test_verified_field_requirements(self):
        rec = extract_document("GOV-E-01", extractor=self.extractor)
        verified_field = rec["scheme_name"]
        self.assertEqual(verified_field["verification_status"], "verified")
        self.assertIsNotNone(verified_field["value"])
        self.assertGreaterEqual(len(verified_field["evidence"]), 1)
        self.assertIn("text", verified_field["evidence"][0])
        self.assertIn("locator", verified_field["evidence"][0])

    # 4. Not_found field requirements
    def test_not_found_field_requirements(self):
        rec = extract_document("GOV-E-01", extractor=self.extractor)
        not_found_field = rec["age_criteria"]
        self.assertEqual(not_found_field["verification_status"], "not_found")
        self.assertIsNone(not_found_field["value"])
        self.assertEqual(len(not_found_field["evidence"]), 0)

    # 5. Uncertain field handling
    def test_uncertain_field_handling(self):
        # Create a candidate record with an uncertain field
        rec = extract_document("GOV-E-01", extractor=self.extractor)
        rec["income_criteria"] = {
            "value": "Unclear income limit mentioned",
            "evidence": [{"text": "income details ambiguous", "locator": {"section": "Eligibility"}}],
            "confidence": 0.5,
            "verification_status": "uncertain"
        }
        is_valid, errors = validate_extracted_record(rec)
        self.assertTrue(is_valid, f"Uncertain field record should be valid: {errors}")

    # 6. Invalid field handling
    def test_invalid_field_handling(self):
        rec = extract_document("GOV-E-01", extractor=self.extractor)
        # Violate rule: status verified but value is None
        rec["scheme_name"] = {
            "value": None,
            "evidence": [],
            "confidence": 1.0,
            "verification_status": "verified"
        }
        is_valid, errors = validate_extracted_record(rec)
        self.assertFalse(is_valid, "Record with status 'verified' and value=None must fail validation")

    # 7. Schema validation success
    def test_schema_validation_success(self):
        for doc_id in ['GOV-E-01', 'GOV-M-02', 'GOV-M-03']:
            rec = extract_document(doc_id, extractor=self.extractor)
            is_valid, errors = validate_extracted_record(rec)
            self.assertTrue(is_valid, f"Validation failed for [{doc_id}]: {errors}")

    # 8. Schema validation failure
    def test_schema_validation_failure(self):
        rec = extract_document("GOV-E-01", extractor=self.extractor)
        # Invalid confidence score out of bounds (> 1.0)
        rec["scheme_name"]["confidence"] = 1.5
        is_valid, errors = validate_extracted_record(rec)
        self.assertFalse(is_valid, "Record with confidence > 1.0 must fail schema validation")

    # 9. HTML/API fixture extraction
    def test_html_api_fixture_extraction(self):
        rec_e01 = extract_document("GOV-E-01", extractor=self.extractor)
        self.assertEqual(rec_e01["document_metadata"]["document_id"], "GOV-E-01")
        self.assertEqual(rec_e01["document_metadata"]["source_type"], "HTML")
        
        rec_m02 = extract_document("GOV-M-02", extractor=self.extractor)
        self.assertEqual(rec_m02["document_metadata"]["document_id"], "GOV-M-02")
        self.assertEqual(rec_m02["document_metadata"]["source_type"], "HTML")

    # 10. PDF fixture extraction
    def test_pdf_fixture_extraction(self):
        rec_m03 = extract_document("GOV-M-03", extractor=self.extractor)
        self.assertEqual(rec_m03["document_metadata"]["document_id"], "GOV-M-03")
        self.assertEqual(rec_m03["document_metadata"]["source_type"], "PDF")
        
        # Verify page-level locators are present in PDF evidence
        name_ev = rec_m03["scheme_name"]["evidence"][0]
        self.assertIn("page", name_ev["locator"])
        self.assertEqual(name_ev["locator"]["page"], 1)

    # 11. Evidence locator preservation
    def test_evidence_locator_preservation(self):
        rec_m03 = extract_document("GOV-M-03", extractor=self.extractor)
        b_ev = rec_m03["benefit_amount"]["evidence"]
        pages_found = [item["locator"].get("page") for item in b_ev if "page" in item["locator"]]
        self.assertIn(2, pages_found, "PDF evidence must preserve page 2 locator")
        self.assertIn(3, pages_found, "PDF evidence must preserve page 3 locator")

    # 12. Multi-component benefit preservation
    def test_multicomponent_benefit_preservation(self):
        rec_m02 = extract_document("GOV-M-02", extractor=self.extractor)
        b_val = rec_m02["benefit_amount"]["value"]
        self.assertIsInstance(b_val, list, "Multi-component benefit_amount value must be preserved as a list")
        self.assertEqual(len(b_val), 4, "GOV-M-02 must contain 4 financial package components")


if __name__ == '__main__':
    unittest.main()

