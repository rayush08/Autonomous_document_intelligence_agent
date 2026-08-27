import os
import json
import ssl
import re
import time
import random
import urllib.request
import urllib.error
import socket
from src.llm.base_client import (
    BaseLLMClient,
    LLMError,
    LLMTransportError,
    LLMRateLimitError,
    LLMServiceUnavailableError,
    LLMNetworkError,
    UnrecoverableLLMError,
    InvalidJSONError
)

# Global circuit breaker model health registries
UNHEALTHY_MODELS = {}
PERMANENTLY_UNAVAILABLE_MODELS = set()


def reset_model_health_registry():
    """Reset global circuit breaker health registries (for test isolation)."""
    global UNHEALTHY_MODELS, PERMANENTLY_UNAVAILABLE_MODELS
    UNHEALTHY_MODELS.clear()
    PERMANENTLY_UNAVAILABLE_MODELS.clear()


def sanitize_error_message(msg: str, api_key: str = None) -> str:
    """Redact API key from error messages, URLs, JSON payloads, and HTTP headers."""
    if not msg:
        return ""
    if api_key:
        msg = msg.replace(api_key, "[REDACTED]")
    # Redact key=... query parameters
    msg = re.sub(r'key=[A-Za-z0-9_\-]+', 'key=[REDACTED]', msg)
    # Redact bearer tokens or explicit API key fields in JSON
    msg = re.sub(r'"key":\s*"[A-Za-z0-9_\-]+"', '"key": "[REDACTED]"', msg)
    return msg


def clean_and_parse_json(raw_text: str, model_name: str = "unknown") -> dict:
    """
    Safely extract and parse JSON dictionary from LLM response.
    Strips markdown code blocks, surrounding whitespace, or embedded text.
    """
    if not raw_text or not isinstance(raw_text, str):
        raise InvalidJSONError(f"Raw response from model '{model_name}' is empty or not a string.")

    cleaned = raw_text.strip()

    # 1. Strip markdown fences if present
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    # 2. Try direct JSON parsing
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    # 3. Substring extraction for embedded JSON objects { ... }
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        extracted = match.group(0)
        try:
            data = json.loads(extracted)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    # 4. If all parsing attempts fail, raise a clear structured error
    preview = (cleaned[:200] + "...") if len(cleaned) > 200 else cleaned
    raise InvalidJSONError(
        f"Malformed JSON from model '{model_name}' (response length {len(raw_text)} chars). Preview: {preview}"
    )


class GeminiLLMClient(BaseLLMClient):
    """
    Production Gemini LLM Client using Google Gemini REST API v1beta
    supporting dynamic model discovery, deterministic ranking prioritizing stable Flash models,
    exponential backoff retries with Retry-After parsing, model failover, circuit breaker health tracking,
    and robust JSON parsing.
    """

    def __init__(self, api_key: str = None, model: str = None, timeout: int = 120, auto_discover: bool = False, candidate_models: list[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.timeout = timeout
        self.candidate_models = candidate_models or []
        self.current_model_index = 0

        if auto_discover or model == "auto":
            temp_client = self.create_auto_discovered_client(api_key=self.api_key, verbose=False)
            self.model = temp_client.model
            self.candidate_models = temp_client.candidate_models
        else:
            self.model = model or "gemini-1.5-flash"
            if self.model not in self.candidate_models:
                self.candidate_models.insert(0, self.model)

        self.ssl_ctx = ssl.create_default_context()
        self.ssl_ctx.check_hostname = False
        self.ssl_ctx.verify_mode = ssl.CERT_NONE

    def get_model_path(self) -> str:
        """Ensure model name is correctly formatted as models/{model_name} without duplicating models/."""
        if not self.model:
            return "models/gemini-1.5-flash"
        if self.model.startswith("models/"):
            return self.model
        return f"models/{self.model}"

    def build_generate_url(self) -> str:
        """Construct full API endpoint URL for generateContent."""
        model_path = self.get_model_path()
        return f"https://generativelanguage.googleapis.com/v1beta/{model_path}:generateContent?key={self.api_key}"

    def build_list_models_url(self) -> str:
        """Construct API endpoint URL for listing models."""
        return f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"

    def mark_current_model_unhealthy(self, cooldown_seconds: int = 300, is_permanent: bool = False):
        """Mark current model as unhealthy in global circuit breaker for cooldown duration or permanently."""
        m_name = self.model.replace("models/", "")
        if is_permanent:
            PERMANENTLY_UNAVAILABLE_MODELS.add(m_name)
            print(f"⛔ [Circuit Breaker] Model '{m_name}' marked PERMANENTLY unavailable.")
        else:
            UNHEALTHY_MODELS[m_name] = time.time() + cooldown_seconds
            print(f"⚠️ [Circuit Breaker] Model '{m_name}' marked unhealthy for {cooldown_seconds}s cooldown.")

    def failover_to_next_model(self, is_permanent: bool = False) -> str:
        """Failover to next eligible candidate model if current model experiences transport errors."""
        self.mark_current_model_unhealthy(is_permanent=is_permanent)
        now = time.time()

        for idx, cand in enumerate(self.candidate_models):
            cand_clean = cand.replace("models/", "")
            if cand_clean in PERMANENTLY_UNAVAILABLE_MODELS:
                continue
            cooldown_until = UNHEALTHY_MODELS.get(cand_clean, 0)
            if cooldown_until < now and cand_clean != self.model.replace("models/", ""):
                self.model = cand_clean
                self.current_model_index = idx
                print(f"🔄 [Client Failover] Switched to candidate model: '{self.model}'")
                return self.model

        print(f"⚠️ [Client Failover] No healthy alternative candidate models available.")
        return None

    @classmethod
    def list_available_models(cls, api_key: str = None) -> list[dict]:
        """Query official Gemini API models endpoint to discover available models."""
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        try:
            req = urllib.request.Request(url)
            res = urllib.request.urlopen(req, context=ssl_ctx, timeout=15)
            data = json.loads(res.read().decode('utf-8'))
            return data.get('models', [])
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='ignore')
            clean_body = sanitize_error_message(body, key)
            if e.code in [400, 401, 403, 404]:
                raise UnrecoverableLLMError(f"Gemini Models API HTTP Error {e.code} ({e.reason}): {clean_body}")
            raise LLMTransportError(f"Gemini Models API HTTP Error {e.code} ({e.reason}): {clean_body}")
        except Exception as e:
            clean_e = sanitize_error_message(str(e), key)
            raise LLMNetworkError(f"Failed to query Gemini models endpoint: {clean_e}")

    @classmethod
    def create_auto_discovered_client(cls, api_key: str = None, verbose: bool = True) -> 'GeminiLLMClient':
        """
        Discover available models supporting generateContent, filter out specialized/non-text models,
        rank stable Flash models first, run a smoke test on candidates, and return a GeminiLLMClient.
        """
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")

        models = cls.list_available_models(key)
        
        # Filter: must support generateContent AND exclude non-text/specialized models
        excluded_keywords = ["tts", "imagen", "embed", "bison", "robotics", "computer-use", "transcription", "deep-research", "audio"]
        
        filtered_models = []
        for m in models:
            m_name = m.get('name', '').lower()
            methods = m.get('supportedGenerationMethods', [])
            if 'generateContent' not in methods:
                continue
            if any(ex in m_name for ex in excluded_keywords):
                continue
            filtered_models.append(m)

        if not filtered_models:
            raise UnrecoverableLLMError("No suitable Gemini text generation models supporting 'generateContent' were found.")

        # Candidate ranking strategy:
        # Tier 0: Stable Flash models (gemini-1.5-flash, gemini-2.0-flash)
        # Tier 1: Stable Pro models (gemini-1.5-pro)
        # Tier 2: Stable lightweight Flash models (gemini-flash-lite, gemini-1.5-flash-8b)
        # Tier 3: Stable aliases (gemini-flash-latest)
        # Tier 4: Preview/experimental models
        def model_preference_rank(m_dict):
            name = m_dict.get('name', '').lower()
            is_preview = 'preview' in name or 'exp' in name
            
            if '1.5-flash' in name and not is_preview:
                return 0
            if '2.0-flash' in name and not is_preview:
                return 1
            if '1.5-pro' in name and not is_preview:
                return 2
            if 'flash-lite' in name or '8b' in name:
                return 3
            if 'flash-latest' in name:
                return 4
            if 'flash' in name and not is_preview:
                return 5
            if 'pro' in name and not is_preview:
                return 6
            if 'flash' in name:
                return 7
            return 8

        candidate_models_info = sorted(filtered_models, key=model_preference_rank)
        candidate_ids = [m.get('name', '').replace('models/', '') for m in candidate_models_info]

        selected_client = None
        for model_id in candidate_ids:
            client = cls(api_key=key, model=model_id, timeout=120, candidate_models=candidate_ids)
            try:
                if client.run_smoke_test():
                    if verbose:
                        print(f"\nDISCOVERED MODEL:\nmodels/{model_id}")
                        print(f"\nSELECTED MODEL:\n{model_id}")
                        print("\nSMOKE TEST:\nPASSED")
                    selected_client = client
                    break
                else:
                    if verbose:
                        print(f"\nSMOKE TEST:\nFAILED for candidate model: {model_id}")
            except Exception as e:
                if verbose:
                    clean_err = sanitize_error_message(str(e), key)
                    print(f"\nSMOKE TEST FAILED for candidate model {model_id}: {clean_err}")

        if not selected_client:
            raise UnrecoverableLLMError("All discovered Gemini text models failed smoke test verification.")

        return selected_client

    def run_smoke_test(self) -> bool:
        """Run a lightweight smoke test expecting {"status": "ok"}."""
        prompt = 'Return exactly this JSON: {"status": "ok"}'
        schema = {
            "type": "object",
            "properties": {"status": {"type": "string"}},
            "required": ["status"]
        }
        res = self.generate_structured_output(prompt, schema)
        if isinstance(res, dict) and res.get("status") == "ok":
            return True
        return False

    def parse_retry_after(self, headers, body_str: str) -> float:
        """Extract retry delay seconds from HTTP headers or provider error JSON body."""
        if headers:
            retry_header = headers.get("Retry-After") or headers.get("retry-after")
            if retry_header:
                try:
                    return float(retry_header)
                except ValueError:
                    pass

        if body_str:
            match = re.search(r'"retryDelay":\s*"(\d+(?:\.\d+)?)s"', body_str)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass
            match_plain = re.search(r'retry in (\d+)s', body_str, re.IGNORECASE)
            if match_plain:
                try:
                    return float(match_plain.group(1))
                except ValueError:
                    pass

        return 0.0


    def _execute_http_request_with_retry(self, url: str, payload_bytes: bytes, headers: dict) -> dict:
        """
        Execute HTTP request with bounded exponential backoff and Retry-After header parsing.
        Raises typed transport exceptions (LLMRateLimitError, LLMServiceUnavailableError, LLMNetworkError).
        """
        max_transient_retries = 2
        last_exception = None

        for retry in range(max_transient_retries + 1):
            start_time = time.time()
            try:
                req = urllib.request.Request(url, data=payload_bytes, headers=headers)
                res = urllib.request.urlopen(req, context=self.ssl_ctx, timeout=self.timeout)
                data = json.loads(res.read().decode('utf-8'))
                return data
            except urllib.error.HTTPError as e:
                elapsed = time.time() - start_time
                body = e.read().decode('utf-8', errors='ignore')
                clean_msg = sanitize_error_message(
                    f"Gemini API HTTP Error {e.code} ({e.reason}) for model '{self.model}'. Elapsed: {elapsed:.2f}s. Response Body: {body}",
                    self.api_key
                )

                # Unrecoverable errors (400, 401, 403, 404) -> Fail immediately
                if e.code in [400, 401, 403, 404]:
                    self.mark_current_model_unhealthy(is_permanent=True)
                    raise UnrecoverableLLMError(clean_msg)

                # Parse provider Retry-After delay
                retry_delay = self.parse_retry_after(e.headers, body)

                if e.code == 429:
                    last_exception = LLMRateLimitError(clean_msg, retry_after=retry_delay)
                elif e.code in [500, 502, 503, 504]:
                    last_exception = LLMServiceUnavailableError(clean_msg)
                else:
                    last_exception = LLMTransportError(clean_msg)

                if retry < max_transient_retries:
                    delay = retry_delay if retry_delay is not None else min(30.0, (2 ** retry) + random.uniform(0.5, 1.5))
                    print(f"⚠️ [Transport HTTP {e.code}] Model '{self.model}' attempt {retry+1}/{max_transient_retries+1} failed. Retrying in {delay:.2f}s...")
                    time.sleep(delay)

            except (socket.timeout, TimeoutError, urllib.error.URLError) as e:
                elapsed = time.time() - start_time
                clean_msg = sanitize_error_message(f"Gemini API network timeout/connection error for model '{self.model}': {str(e)}. Elapsed: {elapsed:.2f}s", self.api_key)
                last_exception = LLMNetworkError(clean_msg)
                if retry < max_transient_retries:
                    delay = min(30.0, (2 ** retry) + random.uniform(0.5, 1.5))
                    print(f"⚠️ [Network Timeout/Error] Model '{self.model}' attempt {retry+1}/{max_transient_retries+1} failed. Retrying in {delay:.2f}s...")
                    time.sleep(delay)

        raise last_exception if last_exception else LLMTransportError(f"API request failed for model '{self.model}' after retries.")

    def generate_structured_output(self, prompt: str, schema: dict) -> dict:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")

        url = self.build_generate_url()
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }
        payload_bytes = json.dumps(payload).encode('utf-8')

        data = self._execute_http_request_with_retry(url, payload_bytes, headers)

        try:
            raw_text = data['candidates'][0]['content']['parts'][0]['text']
            return clean_and_parse_json(raw_text, model_name=self.model)
        except (LLMTransportError, UnrecoverableLLMError, InvalidJSONError) as e:
            raise e
        except Exception as e:
            clean_msg = sanitize_error_message(f"Gemini API response parsing failed: {e}", self.api_key)
            raise InvalidJSONError(clean_msg)

    def generate_text(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")

        url = self.build_generate_url()
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        payload_bytes = json.dumps(payload).encode('utf-8')

        data = self._execute_http_request_with_retry(url, payload_bytes, headers)

        try:
            return data['candidates'][0]['content']['parts'][0]['text']
        except LLMTransportError as e:
            raise e
        except Exception as e:
            clean_msg = sanitize_error_message(f"Gemini API text parsing failed: {e}", self.api_key)
            raise LLMTransportError(clean_msg)

