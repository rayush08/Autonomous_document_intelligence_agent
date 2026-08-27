import os
import json
from src.llm.base_client import BaseLLMClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GOLD_DIR = os.path.join(BASE_DIR, "evaluation", "gold")


class MockLLMClient(BaseLLMClient):
    """
    Deterministic Mock LLM Client for testing without network calls or paid LLM usage.
    """

    def __init__(self, custom_responses: dict = None):
        """
        Args:
            custom_responses (dict): Optional dictionary mapping document_id or prompt keys 
                                    to custom mock JSON responses.
        """
        self.custom_responses = custom_responses or {}

    def generate_structured_output(self, prompt: str, schema: dict) -> dict:
        # Check if custom response is provided
        for key, resp in self.custom_responses.items():
            if key in prompt:
                if isinstance(resp, Exception):
                    raise resp
                if isinstance(resp, str):
                    return json.loads(resp)
                return resp

        # Extract document ID from prompt if present
        doc_id = None
        for candidate in ['GOV-E-01', 'GOV-E-02', 'GOV-E-03', 'GOV-E-04', 'GOV-M-01', 'GOV-M-02', 'GOV-M-03']:
            if candidate in prompt:
                doc_id = candidate
                break

        if doc_id:
            gold_file = os.path.join(GOLD_DIR, f"{doc_id}.json")
            if os.path.exists(gold_file):
                with open(gold_file, 'r', encoding='utf-8') as gf:
                    return json.load(gf)

        # Fallback empty record
        return {
            "document_metadata": {
                "document_id": doc_id or "UNKNOWN",
                "source_type": "HTML",
                "source_identifier": "mock://source",
                "extraction_timestamp": "2026-08-25T23:35:00Z"
            }
        }

    def generate_text(self, prompt: str) -> str:
        res_dict = self.generate_structured_output(prompt, {})
        return json.dumps(res_dict, ensure_ascii=False)

