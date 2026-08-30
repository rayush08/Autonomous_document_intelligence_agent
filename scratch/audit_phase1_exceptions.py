import sys
import os
sys.path.insert(0, os.getcwd())

import unittest
from src.llm.base_client import (
    LLMError,
    LLMTransportError,
    LLMRateLimitError,
    LLMServiceUnavailableError,
    LLMNetworkError,
    UnrecoverableLLMError,
    LLMResponseError,
    InvalidJSONError,
    SchemaValidationError,
    EvidenceValidationError,
    SemanticCompletenessError
)
from src.llm.gemini_client import GeminiLLMClient


class TestPhase1ExceptionAudit(unittest.TestCase):

    def test_01_exception_hierarchy_inheritance(self):
        self.assertTrue(issubclass(LLMTransportError, LLMError))
        self.assertTrue(issubclass(LLMResponseError, LLMError))
        self.assertTrue(issubclass(LLMRateLimitError, LLMTransportError))
        self.assertTrue(issubclass(LLMServiceUnavailableError, LLMTransportError))
        self.assertTrue(issubclass(LLMNetworkError, LLMTransportError))
        self.assertTrue(issubclass(UnrecoverableLLMError, LLMTransportError))
        
        self.assertTrue(issubclass(InvalidJSONError, LLMResponseError))
        self.assertTrue(issubclass(SchemaValidationError, LLMResponseError))
        self.assertTrue(issubclass(EvidenceValidationError, LLMResponseError))
        self.assertTrue(issubclass(SemanticCompletenessError, LLMResponseError))

    def test_02_retry_after_parsing_all_cases(self):
        client = GeminiLLMClient(api_key="test_key")

        # 1. Integer Retry-After
        self.assertEqual(client.parse_retry_after({"Retry-After": "15"}, ""), 15.0)

        # 2. JSON retryDelay
        json_body = '{"error": {"details": [{"retryDelay": "18s"}]}}'
        self.assertEqual(client.parse_retry_after({}, json_body), 18.0)

        # 3. Malformed header
        self.assertEqual(client.parse_retry_after({"Retry-After": "invalid"}, ""), 0.0)

        # 4. Missing header
        self.assertEqual(client.parse_retry_after({}, ""), 0.0)


if __name__ == '__main__':
    unittest.main()
