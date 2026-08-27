import os
import json
import time
from datetime import datetime
from src.extraction import BaseExtractor, SCHEMA_FIELDS, validate_extracted_record, canonicalize_extracted_record
from src.llm.base_client import BaseLLMClient, UnrecoverableLLMError
from src.llm.mock_client import MockLLMClient
from src.llm.segmentation import segment_document
from src.llm.evidence_verifier import verify_evidence_against_document
from src.llm.semantic_completeness import validate_semantic_completeness
from src.llm.prompts import build_document_extraction_prompt, SYSTEM_EXTRACTION_PROMPT


class LLMExtractor(BaseExtractor):
    """
    Real LLM/Agent-Based Extractor supporting provider abstraction, 
    document segmentation, evidence verification, semantic completeness validation,
    diagnostic logging, and controlled retries.
    
    Retry Architecture Math:
    - Extractor Layer (Semantic Retries): max_retries = 2 (1 initial attempt + 2 retries = 3 extraction attempts)
    - Client Layer (Transport/HTTP Retries): max_transient_retries = 2 (1 initial HTTP call + 2 network retries = 3 HTTP attempts)
    - True Maximum HTTP Requests Per Document: 3 extraction attempts * 3 HTTP attempts = 9 maximum HTTP requests.
    """

    def __init__(self, llm_client: BaseLLMClient = None, max_retries: int = 2):
        self.llm_client = llm_client or MockLLMClient()
        self.max_retries = max_retries

    def extract(self, document_id: str, ingested_artifact: dict) -> dict:
        """
        Perform document understanding and extraction from ingested document artifact.
        
        Args:
            document_id (str): Identifier of target scheme document.
            ingested_artifact (dict): Ingested artifact dictionary.
            
        Returns:
            dict: Schema-compliant extracted scheme record.
        """
        # 1. Segment document into metadata-tagged chunks
        chunks = segment_document(document_id, ingested_artifact)
        source_type = ingested_artifact.get('content_type', 'HTML')
        source_url = ingested_artifact.get('source_url', '')

        # 2. Build extraction prompt
        base_prompt = build_document_extraction_prompt(document_id, source_type, chunks)
        chunk_count = len(chunks)
        selected_model = getattr(self.llm_client, 'model', 'unknown_model')

        # 3. Attempt extraction with retry loop
        record = None
        attempt = 0
        last_error = ""

        while attempt <= self.max_retries:
            curr_prompt = base_prompt
            feedback_chars = 0

            if attempt > 0 and last_error:
                if "JSON parsing" in last_error or "Malformed JSON" in last_error:
                    feedback_str = f"\n\n[PREVIOUS ATTEMPT FAILED JSON PARSING]\nError feedback: {last_error}\nReturn ONLY a valid raw JSON object. Do NOT include markdown code blocks, explanation, or text outside the JSON."
                elif "SemanticCompletenessError" in last_error:
                    feedback_str = f"\n\n[PREVIOUS ATTEMPT FAILED SEMANTIC COMPLETENESS VALIDATION]\nCorrect the following issues:\n- {last_error}\nRe-examine the source text carefully and extract ALL benefit components into a JSON list."
                else:
                    feedback_str = f"\n\n[PREVIOUS ATTEMPT FAILED VALIDATION]\nCorrect the following issues:\n- {last_error}\nReturn the COMPLETE corrected JSON record containing ALL 17 required fields."
                
                curr_prompt += feedback_str
                feedback_chars = len(feedback_str)

            prompt_char_count = len(curr_prompt)
            approx_request_size_bytes = len(curr_prompt.encode('utf-8'))

            print(f"\n🔍 [EXTRACTION START] Document: '{document_id}' | Attempt: {attempt+1}/{self.max_retries+1}")
            print(f"   -> Model: {selected_model} | Chunks: {chunk_count}")
            print(f"   -> Prompt Length: {prompt_char_count} chars | Feedback Chars: {feedback_chars} | Approx Size: {approx_request_size_bytes} bytes")

            start_time = time.time()
            try:
                raw_record = self.llm_client.generate_structured_output(curr_prompt, {})
                elapsed = time.time() - start_time
                print(f"   -> LLM Response Received in {elapsed:.2f}s")
                
                if not isinstance(raw_record, dict):
                    raise ValueError("LLM response is not a valid JSON dictionary")

                # Canonicalize output record BEFORE schema validation
                raw_record = canonicalize_extracted_record(raw_record, document_id)

                # Ensure document_metadata
                if 'document_metadata' not in raw_record or not isinstance(raw_record['document_metadata'], dict):
                    raw_record['document_metadata'] = {}
                    
                raw_record['document_metadata']['document_id'] = document_id
                raw_record['document_metadata']['source_type'] = 'PDF' if source_type == 'application/pdf' or 'pdf' in str(source_type).lower() else 'HTML'
                raw_record['document_metadata']['source_identifier'] = source_url
                if 'extraction_timestamp' not in raw_record['document_metadata']:
                    raw_record['document_metadata']['extraction_timestamp'] = datetime.now().isoformat()

                # 4. First check schema & fields validation
                is_valid, errors = validate_extracted_record(raw_record)
                if not is_valid:
                    last_error = "; ".join(errors)
                    print(f"❌ Attempt {attempt+1} Schema Validation Failed: {last_error}")
                    attempt += 1
                    continue

                # 5. Verify evidence snippets against document chunks
                for field_name in SCHEMA_FIELDS:
                    field_obj = raw_record[field_name]
                    verified_obj, _ = verify_evidence_against_document(field_name, field_obj, chunks)
                    raw_record[field_name] = verified_obj

                # 6. Check generic semantic completeness against document text
                is_complete, completeness_errors = validate_semantic_completeness(raw_record, chunks)
                if not is_complete:
                    last_error = "; ".join(completeness_errors)
                    print(f"❌ Attempt {attempt+1} Semantic Completeness Validation Failed: {last_error}")
                    attempt += 1
                    continue

                # 7. Re-canonicalize & Re-validate after evidence verification & semantic completeness
                raw_record = canonicalize_extracted_record(raw_record, document_id)
                is_valid, errors = validate_extracted_record(raw_record)
                if is_valid:
                    record = raw_record
                    print(f"✅ [{document_id}] Extraction & Validation PASSED on Attempt {attempt+1} ({time.time()-start_time:.2f}s total)")
                    break
                else:
                    last_error = "; ".join(errors)
                    print(f"❌ Attempt {attempt+1} Evidence Re-validation Failed: {last_error}")
                    attempt += 1

            except UnrecoverableLLMError as e:
                # Unrecoverable API error (404, 401, 403, 400) -> Fail immediately without retrying!
                print(f"⛔ Unrecoverable API Error for [{document_id}]: {str(e)}")
                raise e
            except Exception as e:
                elapsed = time.time() - start_time
                last_error = str(e)
                print(f"⚠️ Attempt {attempt+1} Failed in {elapsed:.2f}s: {last_error}")
                attempt += 1

        if record is None:
            raise ValueError(f"LLMExtractor failed for [{document_id}] after {self.max_retries+1} attempts. Last error: {last_error}")

        return record

