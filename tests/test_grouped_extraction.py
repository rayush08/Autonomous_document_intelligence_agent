import os
import unittest
from src.llm.base_client import BaseLLMClient
from src.llm.llm_extractor import LLMExtractor
from src.llm.prompts import GOVERNMENT_SCHEME_GROUPS, OPPORTUNITY_GROUPS


class MockGroupedClient(BaseLLMClient):
    """Mock client that tracks grouped prompt invocations."""
    def __init__(self):
        self.model = "mock-model"
        self.prompts_received = []

    def generate_structured_output(self, prompt: str, schema: dict) -> dict:
        self.prompts_received.append(prompt)
        
        # Return generic field objects for requested fields in prompt
        out = {}
        if "scheme_name" in prompt:
            out["scheme_name"] = {"value": "Test Scheme", "evidence": [{"text": "Test Scheme", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        if "scheme_type" in prompt:
            out["scheme_type"] = {"value": "Central Welfare", "evidence": [{"text": "Central Welfare", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        if "implementing_authority" in prompt:
            out["implementing_authority"] = {"value": "Ministry of Education", "evidence": [{"text": "Ministry of Education", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        if "scheme_status" in prompt:
            out["scheme_status"] = {"value": "Active", "evidence": [{"text": "Active", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        if "target_beneficiaries" in prompt:
            out["target_beneficiaries"] = {"value": "Students", "evidence": [{"text": "Students", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        if "education_level" in prompt:
            out["education_level"] = {"value": "Post-Matric", "evidence": [{"text": "Post-Matric", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        if "age_criteria" in prompt:
            out["age_criteria"] = {"value": "18-25 years", "evidence": [{"text": "18-25 years", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        if "income_criteria" in prompt:
            out["income_criteria"] = {"value": "Below Rs 2,50,000", "evidence": [{"text": "Below Rs 2,50,000", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        if "academic_criteria" in prompt:
            out["academic_criteria"] = {"value": "60% marks", "evidence": [{"text": "60% marks", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        if "category_criteria" in prompt:
            out["category_criteria"] = {"value": ["OBC", "EBC"], "evidence": [{"text": "OBC, EBC", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        if "domicile_criteria" in prompt:
            out["domicile_criteria"] = {"value": "India", "evidence": [{"text": "India", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        if "benefit_type" in prompt:
            out["benefit_type"] = {"value": "Financial Grant", "evidence": [{"text": "Financial Grant", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        if "benefit_amount" in prompt:
            out["benefit_amount"] = {"value": "Rs 10,000 per annum", "evidence": [{"text": "Rs 10,000 per annum", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        if "application_method" in prompt:
            out["application_method"] = {"value": "Online Portal", "evidence": [{"text": "Online Portal", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        if "application_url" in prompt:
            out["application_url"] = {"value": "https://scholarships.gov.in", "evidence": [{"text": "https://scholarships.gov.in", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        if "required_documents" in prompt:
            out["required_documents"] = {"value": ["Aadhaar Card", "Income Certificate"], "evidence": [{"text": "Aadhaar Card, Income Certificate", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        if "application_deadline" in prompt:
            out["application_deadline"] = {"value": "31st December", "evidence": [{"text": "31st December", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
            
        return out


class TestGroupedExtractionIntegration(unittest.TestCase):
    """Test suite for verifying that LLMExtractor executes domain-grouped extraction calls."""

    def test_government_scheme_grouped_extraction(self):
        client = MockGroupedClient()
        extractor = LLMExtractor(llm_client=client)
        artifact = {
            "content_type": "text/html",
            "content": "<p>Test Scheme text with Central Welfare and Ministry of Education</p>"
        }
        record = extractor.extract("GOV-E-01", artifact)

        self.assertIsNotNone(record)
        # Should issue 4 group calls for Government Scheme
        self.assertEqual(extractor.request_accounting["grouped_extraction_calls"], len(GOVERNMENT_SCHEME_GROUPS))
        self.assertEqual(len(client.prompts_received), 4)
        self.assertIn("FIELD GROUP: METADATA", client.prompts_received[0])
        self.assertIn("FIELD GROUP: ELIGIBILITY", client.prompts_received[1])
        self.assertIn("FIELD GROUP: BENEFITS", client.prompts_received[2])
        self.assertIn("FIELD GROUP: APPLICATION", client.prompts_received[3])

    def test_opportunity_grouped_extraction(self):
        client = MockGroupedClient()
        extractor = LLMExtractor(llm_client=client)
        artifact = {
            "content_type": "text/html",
            "content": "<p>Test Opportunity text</p>"
        }
        record = extractor.extract("OPP-E-01", artifact)

        self.assertIsNotNone(record)
        # Should issue 3 group calls for Opportunity
        self.assertEqual(extractor.request_accounting["grouped_extraction_calls"], len(OPPORTUNITY_GROUPS))
        self.assertEqual(len(client.prompts_received), 3)


if __name__ == "__main__":
    unittest.main()
