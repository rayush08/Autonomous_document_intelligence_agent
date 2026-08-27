import os
import unittest
from unittest.mock import patch, MagicMock
import urllib.error
from src.llm.gemini_client import GeminiLLMClient, sanitize_error_message
from src.llm.base_client import UnrecoverableLLMError


class TestGeminiLLMClient(unittest.TestCase):

    def test_endpoint_construction_default(self):
        client = GeminiLLMClient(api_key="test_secret_key_123", model="gemini-3.6-flash")
        self.assertEqual(client.get_model_path(), "models/gemini-3.6-flash")
        url = client.build_generate_url()
        self.assertIn("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent", url)
        self.assertIn("key=test_secret_key_123", url)

    def test_endpoint_construction_with_models_prefix(self):
        client = GeminiLLMClient(api_key="test_secret_key_123", model="models/gemini-3.6-flash")
        # Must NOT duplicate models/models/
        self.assertEqual(client.get_model_path(), "models/gemini-3.6-flash")
        url = client.build_generate_url()
        self.assertNotIn("models/models/", url)
        self.assertIn("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent", url)

    def test_model_name_configuration(self):
        client = GeminiLLMClient(api_key="test_key", model="gemini-3.6-flash")
        self.assertEqual(client.model, "gemini-3.6-flash")
        self.assertEqual(client.get_model_path(), "models/gemini-3.6-flash")

    def test_api_key_redaction_in_errors(self):
        raw_error_text = "HTTP 404: Model not found at https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=secret_api_key_xyz987"
        clean_text = sanitize_error_message(raw_error_text, "secret_api_key_xyz987")
        self.assertNotIn("secret_api_key_xyz987", clean_text)
        self.assertIn("[REDACTED]", clean_text)

    @patch('urllib.request.urlopen')
    def test_http_error_parsing(self, mock_urlopen):
        err_body = b'{"error": {"code": 404, "message": "Model not found at key=secret_key_abc123"}}'
        mock_err = urllib.error.HTTPError(
            url="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=secret_key_abc123",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=MagicMock(read=MagicMock(return_value=err_body))
        )
        mock_urlopen.side_effect = mock_err

        client = GeminiLLMClient(api_key="secret_key_abc123", model="gemini-2.0-flash")
        with self.assertRaises(UnrecoverableLLMError) as ctx:
            client.generate_structured_output("test prompt", {})

        err_msg = str(ctx.exception)
        self.assertIn("HTTP Error 404", err_msg)
        self.assertIn("Model not found", err_msg)
        self.assertNotIn("secret_key_abc123", err_msg)
        self.assertIn("[REDACTED]", err_msg)

    @patch('src.llm.gemini_client.GeminiLLMClient.list_available_models')
    @patch('src.llm.gemini_client.GeminiLLMClient.run_smoke_test')
    def test_auto_discovery_model_propagation(self, mock_smoke, mock_list):
        mock_list.return_value = [
            {"name": "models/gemini-3.6-flash", "supportedGenerationMethods": ["generateContent"]},
            {"name": "models/gemini-1.5-old", "supportedGenerationMethods": ["generateContent"]}
        ]
        # Candidate 0 (gemini-3.6-flash) fails smoke test, Candidate 1 (gemini-1.5-old) passes
        mock_smoke.side_effect = [False, True]

        client = GeminiLLMClient.create_auto_discovered_client(api_key="secret_key_123", verbose=False)
        self.assertEqual(client.model, "gemini-1.5-old", "Candidate smoke test failure must cause discovery to select the next working candidate")
        self.assertEqual(client.get_model_path(), "models/gemini-1.5-old")

    @patch('src.llm.gemini_client.GeminiLLMClient.list_available_models')
    @patch('src.llm.gemini_client.GeminiLLMClient.run_smoke_test')
    def test_auto_discovery_all_failed_raises_error(self, mock_smoke, mock_list):
        mock_list.return_value = [
            {"name": "models/gemini-1.5-old", "supportedGenerationMethods": ["generateContent"]}
        ]
        mock_smoke.return_value = False

        with self.assertRaises(UnrecoverableLLMError) as ctx:
            GeminiLLMClient.create_auto_discovered_client(api_key="secret_key_123", verbose=False)
        self.assertIn("failed smoke test verification", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()

