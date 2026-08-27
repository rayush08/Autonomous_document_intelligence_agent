from abc import ABC, abstractmethod


class UnrecoverableLLMError(ValueError):
    """
    Raised when an unrecoverable LLM API error occurs 
    (e.g., 404 Model Not Found, 401 Unauthorized, 403 Forbidden, 400 Bad Request).
    These errors must fail immediately without consuming extraction retry attempts.
    """
    pass


class BaseLLMClient(ABC):
    """Abstract Base Class for LLM Client implementations."""

    @abstractmethod
    def generate_structured_output(self, prompt: str, schema: dict) -> dict:
        """
        Generate structured JSON output conforming to the provided JSON schema.
        
        Args:
            prompt (str): Detailed prompt string.
            schema (dict): Target JSON schema definition or field schema.
            
        Returns:
            dict: Structured JSON dictionary response.
        """
        pass

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """
        Generate raw text response given a prompt.
        
        Args:
            prompt (str): Input prompt string.
            
        Returns:
            str: Generated text response.
        """
        pass

