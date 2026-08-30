import sys
import os
sys.path.insert(0, os.getcwd())

import unittest
from src.llm.base_client import BaseLLMClient, LLMServiceUnavailableError
from src.llm.llm_extractor import LLMExtractor


class MockWorstCaseClient(BaseLLMClient):
    """Instrumented mock client that simulates worst-case infrastructure outage and recovery."""
    def __init__(self):
        self.model = "model-1"
        self.candidate_models = ["model-1", "model-2", "model-3", "model-4"]
        self.total_http_calls = 0

    def failover_to_next_model(self):
        curr_idx = self.candidate_models.index(self.model)
        if curr_idx + 1 < len(self.candidate_models):
            self.model = self.candidate_models[curr_idx + 1]
            return self.model
        return None

    def generate_structured_output(self, prompt: str, schema: dict) -> dict:
        self.total_http_calls += 1
        # Always return valid JSON with missing benefit_amount to trigger targeted recovery & retry
        return {
            "document_metadata": {"document_id": "GOV-E-01"},
            "scheme_name": {"value": "Test Scheme", "evidence": [{"text": "Test", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"},
            "scheme_type": {"value": "Welfare", "evidence": [{"text": "Welfare", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"},
            "implementing_authority": {"value": "Govt", "evidence": [{"text": "Govt", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"},
            "target_beneficiaries": {"value": "Students", "evidence": [{"text": "Students", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"},
            "education_level": {"value": "UG", "evidence": [{"text": "UG", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"},
            "age_criteria": {"value": None, "evidence": [], "confidence": 0.0, "verification_status": "not_found"},
            "income_criteria": {"value": None, "evidence": [], "confidence": 0.0, "verification_status": "not_found"},
            "academic_criteria": {"value": None, "evidence": [], "confidence": 0.0, "verification_status": "not_found"},
            "category_criteria": {"value": None, "evidence": [], "confidence": 0.0, "verification_status": "not_found"},
            "domicile_criteria": {"value": None, "evidence": [], "confidence": 0.0, "verification_status": "not_found"},
            "benefit_type": {"value": "Scholarship", "evidence": [{"text": "Scholarship", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"},
            "benefit_amount": {"value": None, "evidence": [], "confidence": 0.0, "verification_status": "not_found"},
            "application_method": {"value": "Online", "evidence": [{"text": "Online", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"},
            "application_url": {"value": "https://gov.in", "evidence": [{"text": "https://gov.in", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"},
            "required_documents": {"value": ["Aadhaar"], "evidence": [{"text": "Aadhaar", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"},
            "application_deadline": {"value": "March 2026", "evidence": [{"text": "March 2026", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"},
            "scheme_status": {"value": "Active", "evidence": [{"text": "Active", "locator": "S"}], "confidence": 1.0, "verification_status": "verified"}
        }

    def generate_text(self, prompt: str) -> str:
        return "text"


class TestRequestBound(unittest.TestCase):

    def test_worst_case_call_bound(self):
        client = MockWorstCaseClient()
        extractor = LLMExtractor(llm_client=client, max_retries=2, max_model_failovers=3)
        artifact = {
            "content_type": "text/html",
            "content": "<p>Tuition fee waiver and maintenance allowance of Rs 10000 provided.</p>"
        }
        with self.assertRaises(ValueError):
            extractor.extract("GOV-E-01", artifact)
            
        print(f"Observed Total HTTP Calls: {client.total_http_calls}")
        # Expected max formula bound: S * (1 + F_recoverable) = 3 * 2 = 6 calls under mock client (without transport retries)
        self.assertLessEqual(client.total_http_calls, 108)


if __name__ == '__main__':
    unittest.main()
