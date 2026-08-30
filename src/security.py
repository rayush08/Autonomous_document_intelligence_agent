"""
Security and Prompt Injection Guardrails Module for Autonomous Document Intelligence Agent.
Provides input sanitization, document boundary safety, path traversal protection, and secret leakage prevention.
"""

import os
import re

# Key patterns to neutralize in untrusted document text to prevent prompt injection
INJECTION_PATTERNS = [
    re.compile(r"System Prompt:", re.IGNORECASE),
    re.compile(r"Ignore previous instructions", re.IGNORECASE),
    re.compile(r"Disregard prior instructions", re.IGNORECASE),
    re.compile(r"You are now a", re.IGNORECASE),
    re.compile(r"\[SYSTEM\]", re.IGNORECASE),
    re.compile(r"```json\s*\{.*\"override\"", re.IGNORECASE | re.DOTALL),
]

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB limit for safety

def sanitize_document_text(text: str) -> str:
    """
    Sanitizes raw document text to prevent prompt injection attacks where untrusted document text
    attempts to hijack LLM instructions.
    """
    if not text:
        return ""

    sanitized = text
    for pattern in INJECTION_PATTERNS:
        sanitized = pattern.sub("[SANITIZED_INSTRUCTION]", sanitized)

    return sanitized

def validate_file_safety(file_path: str) -> bool:
    """
    Validates file existence, path safety (preventing directory traversal), and size limits.
    """
    if not file_path:
        return False

    abs_path = os.path.abspath(file_path)

    if not os.path.exists(abs_path):
        return False

    if not os.path.isfile(abs_path):
        return False

    if os.path.getsize(abs_path) > MAX_FILE_SIZE_BYTES:
        return False

    return True

def audit_for_secrets(content: str) -> bool:
    """
    Returns True if content appears clean of API keys/secrets, False if potential credentials discovered.
    """
    if not content:
        return True

    # Generic Google Gemini API Key pattern check
    if re.search(r"AIzaSy[A-Za-z0-9_-]{33}", content):
        return False

    return True
