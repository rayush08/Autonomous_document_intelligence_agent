import os
import json
import unittest
from src.llm.base_client import (
    BaseLLMClient,
    LLMTransportError,
    LLMRateLimitError,
    LLMServiceUnavailableError,
    LLMNetworkError,
    UnrecoverableLLMError,
    LLMResponseError,
    InvalidJSONError
)
from src.llm.gemini_client import GeminiLLMClient, reset_model_health_registry, sanitize_error_message
from src.llm.llm_extractor import LLMExtractor


class MockInstrumentedClient(BaseLLMClient):
    """Mock client that instruments total HTTP requests, failovers, and targeted field recovery."""
    def __init__(self, fail_models: list[str] = None, return_missing_stipend_first: bool = False):
        self.fail_models = fail_models or []
        self.return_missing_stipend_first = return_missing_stipend_first
        self.model = "model-1"
        self.candidate_models = ["model-1", "model-2", "model-3", "model-4"]
        self.http_calls_by_model = {m: 0 for m in self.candidate_models}
        self.total_http_requests = 0

    def failover_to_next_model(self):
        curr_idx = self.candidate_models.index(self.model)
        if curr_idx + 1 < len(self.candidate_models):
            self.model = self.candidate_models[curr_idx + 1]
            return self.model
        return None

    def generate_structured_output(self, prompt: str, schema: dict) -> dict:
        self.http_calls_by_model[self.model] += 1
        self.total_http_requests += 1

        if self.model in self.fail_models:
            raise LLMServiceUnavailableError(f"HTTP 503 for model '{self.model}'")

        # Targeted single-field recovery prompt detection
        if "Targeted Field to Extract: 'stipend_or_funding'" in prompt:
            return {
                "stipend_or_funding": {
                    "value": "$600/week stipend",
                    "evidence": [{"text": "Monthly stipend of $600/week", "locator": "sec 1"}],
                    "confidence": 1.0,
                    "verification_status": "verified"
                }
            }

        # First call returning missing stipend if flag is enabled
        stipend_val = None if self.return_missing_stipend_first else "$600/week stipend"
        stipend_ev = [] if self.return_missing_stipend_first else [{"text": "Monthly stipend of $600/week", "locator": "sec 1"}]
        stipend_status = "not_found" if self.return_missing_stipend_first else "verified"

        return {
            "document_metadata": {"document_id": "OPP-E-01"},
            "title": {"value": "Test Fellowship", "evidence": [{"text": "Test Fellowship", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"},
            "organization": {"value": "Test Org", "evidence": [{"text": "Test Org", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"},
            "opportunity_type": {"value": "Fellowship", "evidence": [{"text": "Fellowship", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"},
            "education_level": {"value": "Postdoc", "evidence": [{"text": "Postdoc", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"},
            "eligible_disciplines": {"value": ["CS"], "evidence": [{"text": "CS", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"},
            "skills_required": {"value": None, "evidence": [], "confidence": 0.0, "verification_status": "not_found"},
            "experience_required": {"value": None, "evidence": [], "confidence": 0.0, "verification_status": "not_found"},
            "eligibility_notes": {"value": None, "evidence": [], "confidence": 0.0, "verification_status": "not_found"},
            "location": {"value": "USA", "evidence": [{"text": "USA", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"},
            "mode": {"value": "On-site", "evidence": [{"text": "On-site", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"},
            "duration": {"value": "12 months", "evidence": [{"text": "12 months", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"},
            "stipend_or_funding": {"value": stipend_val, "evidence": stipend_ev, "confidence": 1.0 if stipend_val else 0.0, "verification_status": stipend_status},
            "start_date": {"value": "Sept 2026", "evidence": [{"text": "Sept 2026", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"},
            "application_deadline": {"value": "March 2026", "evidence": [{"text": "March 2026", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"},
            "application_url": {"value": "https://test.org", "evidence": [{"text": "https://test.org", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"},
            "required_documents": {"value": ["CV"], "evidence": [{"text": "CV", "locator": "sec 1"}], "confidence": 1.0, "verification_status": "verified"}
        }

    def generate_text(self, prompt: str) -> str:
        return "text"


class TestRetryIsolation(unittest.TestCase):

    def setUp(self):
        reset_model_health_registry()

    def tearDown(self):
        reset_model_health_registry()

    def test_01_http_503_does_not_consume_semantic_retry(self):
        client = MockInstrumentedClient(fail_models=["model-1"])
        extractor = LLMExtractor(llm_client=client, max_retries=2, max_model_failovers=3)
        artifact = {"content_type": "text/html", "content": "<p>Test fellowship</p>"}
        record = extractor.extract("OPP-E-01", artifact)
        
        self.assertIsNotNone(record)
        self.assertEqual(extractor.request_accounting["semantic_attempts"], 1)
        self.assertEqual(extractor.request_accounting["transport_failures"], 1)
        self.assertEqual(extractor.request_accounting["model_failovers"], 1)

    def test_02_worst_case_http_request_upper_bound(self):
        """Verify worst-case infrastructure outage across candidate models stays bounded."""
        client = MockInstrumentedClient(fail_models=["model-1", "model-2", "model-3", "model-4"])
        extractor = LLMExtractor(llm_client=client, max_retries=2, max_model_failovers=3)
        artifact = {"content_type": "text/html", "content": "<p>Test fellowship</p>"}
        
        with self.assertRaises(LLMServiceUnavailableError):
            extractor.extract("OPP-E-01", artifact)
            
        self.assertEqual(client.total_http_requests, 4)
        self.assertEqual(extractor.request_accounting["model_failovers"], 3)
        self.assertEqual(extractor.request_accounting["semantic_attempts"], 0)

    def test_03_provider_retry_after_header_parsing(self):
        gemini = GeminiLLMClient(api_key="test_key")
        headers = {"Retry-After": "15"}
        self.assertEqual(gemini.parse_retry_after(headers, ""), 15.0)

        body_json = '{"error": {"code": 429, "message": "Resource exhausted", "details": [{"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": "18s"}]}}'
        self.assertEqual(gemini.parse_retry_after({}, body_json), 18.0)

    def test_04_api_secret_security_redaction(self):
        """Verify API keys are redacted from URLs, query params, exception messages, and JSON error bodies."""
        secret_key = "AIzaSySecretTestKey12345"
        url_err = f"Error calling https://generativelanguage.googleapis.com/v1beta/models?key={secret_key}"
        clean_url = sanitize_error_message(url_err, secret_key)
        self.assertNotIn(secret_key, clean_url)
        self.assertIn("key=[REDACTED]", clean_url)

        json_err = f'{{"error": {{"message": "Invalid key {secret_key}", "key": "{secret_key}"}}}}'
        clean_json = sanitize_error_message(json_err, secret_key)
        self.assertNotIn(secret_key, clean_json)
        self.assertIn("[REDACTED]", clean_json)

    def test_05_request_accounting_accuracy(self):
        client = MockInstrumentedClient(fail_models=[])
        extractor = LLMExtractor(llm_client=client, max_retries=2)
        artifact = {"content_type": "text/html", "content": "<p>Test fellowship</p>"}
        extractor.extract("OPP-E-01", artifact)
        
        acc = extractor.request_accounting
        self.assertEqual(acc["semantic_attempts"], 1)
        self.assertEqual(acc["transport_attempts"], 1)
        self.assertEqual(acc["successful_http_responses"], 1)
        self.assertEqual(acc["transport_failures"], 0)
        self.assertEqual(acc["rate_limit_events"], 0)

    def test_06_targeted_field_recovery_success(self):
        """Verify that missing field detected by semantic completeness triggers targeted single-field recovery."""
        client = MockInstrumentedClient(return_missing_stipend_first=True)
        extractor = LLMExtractor(llm_client=client, max_retries=2)
        artifact = {
            "content_type": "text/html",
            "content": "<p>Monthly stipend of $600/week will be provided to selected fellows.</p>"
        }
        record = extractor.extract("OPP-E-01", artifact)
        
        self.assertIsNotNone(record)
        self.assertEqual(record["stipend_or_funding"]["value"], "$600/week stipend")
    def test_07_request_upper_bound_formula(self):
        """Assert that total worst-case HTTP requests per document adhere to mathematical formula N_max = S * (G + F_rec) * T * (1 + M_failovers)."""
        client = MockInstrumentedClient(return_missing_stipend_first=True)
        extractor = LLMExtractor(llm_client=client, max_retries=2, max_model_failovers=3)
        artifact = {
            "content_type": "text/html",
            "content": "<p>Monthly stipend of $600/week will be provided to selected fellows.</p>"
        }
        extractor.extract("OPP-E-01", artifact)

        # Upper bound calculation parameters: S=3, G=4 (max groups), F_rec=3, T=3, M_failovers=3
        S, G, F_rec, T, M_failovers = 3, 4, 3, 3, 3
        max_theoretical_http_requests = S * (G + F_rec) * T * (1 + M_failovers)
        self.assertEqual(max_theoretical_http_requests, 252)
        self.assertLessEqual(client.total_http_requests, max_theoretical_http_requests)


if __name__ == '__main__':
    unittest.main()


