from abc import ABC, abstractmethod


class LLMError(Exception):
    """Base class for all LLM client and extraction errors."""
    pass


class LLMTransportError(LLMError):
    """Base class for infrastructure, network, HTTP, rate-limiting, or service availability errors."""
    pass


class LLMRateLimitError(LLMTransportError):
    """Raised on HTTP 429 Too Many Requests."""
    def __init__(self, message: str, retry_after: float = None):
        super().__init__(message)
        self.retry_after = retry_after


class LLMServiceUnavailableError(LLMTransportError):
    """Raised on HTTP 503 Service Unavailable, 500, 502, 504."""
    pass


class LLMNetworkError(LLMTransportError):
    """Raised on socket timeout, connection resets, DNS failures."""
    pass


class UnrecoverableLLMError(LLMTransportError):
    """Raised on HTTP 404, 401, 403, 400."""
    pass



class LLMResponseError(LLMError):
    """Base class for model response validation errors (consumes semantic extraction retries)."""
    pass


class InvalidJSONError(LLMResponseError):
    """Model response could not be parsed as valid JSON."""
    pass


class SchemaValidationError(LLMResponseError):
    """Model response failed JSON schema or field structure validation."""
    pass


class EvidenceValidationError(LLMResponseError):
    """Model response failed evidence grounding verification."""
    pass


class SemanticCompletenessError(LLMResponseError):
    """Model response omitted information present in source document text."""
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

