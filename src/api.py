"""
Production Public API Module for Autonomous Document Intelligence Agent.
Provides programmatic python functions for extracting structured intelligence from documents,
validating schemas, and verifying evidence grounding.
"""

import os
import json
from typing import Dict, Any, Optional

from src.ingestion import ingest_document
from src.llm.llm_extractor import LLMExtractor
from src.extraction import canonicalize_extracted_record
from src.validator import validate_against_schema
from src.security import sanitize_document_text, validate_file_safety
from src.logger import get_logger

logger = get_logger("document_intelligence.api")

def extract_document(
    file_path: str,
    domain: str = "government_scheme",
    client: Optional[Any] = None,
    use_mock: bool = True,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Programmatic entry point for structured document extraction.

    Args:
        file_path: Absolute or relative path to the document file (PDF, TXT, HTML, JSON).
        domain: Domain schema ("government_scheme" or "opportunity").
        client: Optional GeminiLLMClient instance. If None and use_mock=True, uses MockLLMClient.
        use_mock: If True, uses deterministic offline MockLLMClient.
        verbose: Print detailed extraction progress.

    Returns:
        Structured JSON dictionary containing extracted fields, verification statuses, and evidence.
    """
    if not validate_file_safety(file_path):
        raise ValueError(f"Invalid or unsafe file path: '{file_path}'")

    logger.info(f"Ingesting document from '{file_path}' (Domain: {domain})...")
    chunks = ingest_document(file_path)

    # Sanitize chunk text to neutralize potential prompt injection
    for c in chunks:
        c["text"] = sanitize_document_text(c["text"])

    if client is None and use_mock:
        from src.llm.mock_client import MockLLMClient
        client = MockLLMClient()

    doc_id = os.path.splitext(os.path.basename(file_path))[0]
    ingested_artifact = {
        "content_type": "JSON" if file_path.endswith(".json") else "PDF" if file_path.endswith(".pdf") else "HTML",
        "source_url": file_path,
        "content": chunks[0]["text"] if chunks else ""
    }

    extractor = LLMExtractor(llm_client=client)
    extracted_record = extractor.extract(doc_id, ingested_artifact)

    canonical_record = canonicalize_extracted_record(extracted_record)
    validation_status = validate_against_schema(canonical_record, domain)

    return {
        "document_path": file_path,
        "domain": domain,
        "extraction": canonical_record,
        "schema_valid": validation_status["valid"],
        "schema_errors": validation_status.get("errors", []),
        "request_accounting": extractor.request_accounting
    }
