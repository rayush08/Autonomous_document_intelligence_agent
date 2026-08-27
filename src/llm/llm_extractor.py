import os
import json
import time
from datetime import datetime
from src.extraction import BaseExtractor, get_fields_for_record, validate_extracted_record, canonicalize_extracted_record
from src.llm.base_client import (
    BaseLLMClient,
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
from src.llm.mock_client import MockLLMClient
from src.llm.segmentation import segment_document
from src.llm.evidence_verifier import verify_evidence_against_document
from src.llm.semantic_completeness import validate_semantic_completeness, FIELD_SEMANTIC_HINTS, is_affirmative_indicator
from src.llm.prompts import (
    build_document_extraction_prompt,
    build_group_extraction_prompt,
    GOVERNMENT_SCHEME_GROUPS,
    OPPORTUNITY_GROUPS,
    SYSTEM_EXTRACTION_PROMPT
)



class LLMExtractor(BaseExtractor):
    """
    Real LLM/Agent-Based Extractor supporting provider abstraction, 
    document segmentation, evidence verification, semantic completeness validation,
    targeted single-field recovery, strict transport vs. semantic retry isolation, model failover,
    and request accounting.

    True Bounded Request Math:
    - Semantic Extraction Attempts (max_retries = 2 -> 3 primary extraction attempts: S = 3)
    - Targeted Single-Field Recoveries (up to F_recoverable = 2 per attempt)
    - Transport Retries per HTTP Call (max_transient_retries = 2 -> 3 HTTP calls: T = 3)
    - Candidate Model Failovers (max_model_failovers = 3 -> up to 4 models: M_failovers = 3)
    - Corrected Maximum HTTP Request Upper Bound:
      N_max = S * (1 + F_recoverable) * T * (1 + M_failovers)
      N_max = 3 * (1 + 2) * 3 * 4 = 108 maximum HTTP requests per document.
    """


    def __init__(self, llm_client: BaseLLMClient = None, max_retries: int = 2, max_model_failovers: int = 3):
        self.llm_client = llm_client or MockLLMClient()
        self.max_retries = max_retries
        self.max_model_failovers = max_model_failovers
        self.request_accounting = {
            "semantic_attempts": 0,
            "transport_attempts": 0,
            "successful_http_responses": 0,
            "transport_failures": 0,
            "rate_limit_events": 0,
            "model_failovers": 0,
            "targeted_field_recoveries": 0
        }

    def recover_target_field(self, field_name: str, hint_cfg: dict, record: dict, chunks: list[dict], document_id: str) -> bool:
        """
        Targeted recovery mechanism: Extract ONLY the specified missed field using affirmative text excerpts.
        Eliminates full-document prompt clutter and focuses LLM context directly on missing evidence.
        """
        # Find affirmative matching chunks
        matching_chunks = []
        for c in chunks:
            text = c.get("text", "")
            if any(kw in text.lower() for kw in hint_cfg["keywords"]) and any(is_affirmative_indicator(text, kw) for kw in hint_cfg["keywords"]):
                matching_chunks.append(c)

        if not matching_chunks:
            return False

        excerpts_str = "\n---\n".join([f"[{c.get('locator', 'chunk')}] {c.get('text', '').strip()}" for c in matching_chunks[:4]])

        recovery_prompt = f"""You are an expert document intelligence extraction agent.
Target Document: '{document_id}'
Target Field to Extract: '{field_name}'

Source Document Excerpts:
{excerpts_str}

Task:
Extract ONLY the field '{field_name}' from the excerpts above.
Extract all relevant financial / stipend / funding / eligibility details into a JSON object conforming to:
{{
  "{field_name}": {{
    "value": "<extracted string or list of component strings>",
    "evidence": [
      {{"text": "<verbatim excerpt from source text>", "locator": "<page or section locator>"}}
    ],
    "confidence": 1.0,
    "verification_status": "verified"
  }}
}}

CRITICAL INSTRUCTION FOR MONETARY VALUES:
- Preserve monetary numbers containing commas (e.g. ₹50,000, $5,400, 2,700 CHF, 1,25,000) COMPLETELY INTACT as a single value string.
- Do NOT split a single number containing a thousands-separator comma into multiple list items.
- Return a JSON list ONLY if there are multiple distinct, independent financial benefit components (e.g. stipend AND housing AND travel grant).

Constraint: Return ONLY valid raw JSON without markdown formatting outside the JSON object."""


        print(f"🎯 [TARGETED RECOVERY START] Attempting single-field recovery for '{field_name}' across {len(matching_chunks)} excerpts...")
        try:
            self.request_accounting["transport_attempts"] += 1
            rec_res = self.llm_client.generate_structured_output(recovery_prompt, {})
            self.request_accounting["successful_http_responses"] += 1

            if isinstance(rec_res, dict) and field_name in rec_res and isinstance(rec_res[field_name], dict):
                field_obj = rec_res[field_name]
                # Canonicalize evidence locators and values
                temp_rec = {field_name: field_obj}
                temp_rec = canonicalize_extracted_record(temp_rec, document_id)
                recovered_field_obj = temp_rec[field_name]

                # Verify evidence against document chunks
                verified_obj, _ = verify_evidence_against_document(field_name, recovered_field_obj, chunks)

                status = verified_obj.get("verification_status")
                val = verified_obj.get("value")
                ev = verified_obj.get("evidence", [])

                if status in {"verified", "unverified", "uncertain"} and val is not None and len(ev) >= 1:
                    record[field_name] = verified_obj
                    self.request_accounting["targeted_field_recoveries"] += 1
                    print(f"✅ 🎯 [TARGETED RECOVERY SUCCESS] Field '{field_name}' recovered! Value: {val}")
                    return True
        except Exception as e:
            print(f"⚠️ [Targeted Recovery Notice] Recovery attempt for '{field_name}' failed: {e}")

        return False

    def extract_grouped_fields(self, document_id: str, source_type: str, chunks: list[dict]) -> dict:
        """Extract fields using domain group prompts and merge into a unified record."""
        is_opp = document_id.upper().startswith("OPP-") if document_id else False
        groups = OPPORTUNITY_GROUPS if is_opp else GOVERNMENT_SCHEME_GROUPS

        merged_record = {
            "document_metadata": {
                "document_id": document_id,
                "domain": "opportunity" if is_opp else "government_scheme"
            }
        }

        print(f"   -> 🎯 [GROUPED EXTRACTION START] Executing {len(groups)} domain field group prompts...")

        for group_name, target_fields in groups.items():
            prompt = build_group_extraction_prompt(document_id, source_type, group_name, target_fields, chunks)
            self.request_accounting["transport_attempts"] += 1
            self.request_accounting["grouped_extraction_calls"] += 1
            group_out = self.llm_client.generate_structured_output(prompt, {})
            self.request_accounting["successful_http_responses"] += 1

            if isinstance(group_out, dict):
                for fname in target_fields:
                    if fname in group_out and isinstance(group_out[fname], dict):
                        merged_record[fname] = group_out[fname]
                    else:
                        merged_record[fname] = {
                            "value": None,
                            "evidence": [],
                            "confidence": 0.0,
                            "verification_status": "not_found"
                        }

        return merged_record

    def extract(self, document_id: str, ingested_artifact: dict) -> dict:

        """Extract structured record using LLM with evidence verification and retry loop."""
        self.request_accounting = {
            "semantic_attempts": 0,
            "transport_attempts": 0,
            "successful_http_responses": 0,
            "transport_failures": 0,
            "rate_limit_events": 0,
            "model_failovers": 0,
            "targeted_field_recoveries": 0,
            "grouped_extraction_calls": 0
        }

        chunks = segment_document(document_id, ingested_artifact)
        source_type = ingested_artifact.get('content_type', 'HTML')
        source_url = ingested_artifact.get('source_url', '')

        base_prompt = build_document_extraction_prompt(document_id, source_type, chunks)
        chunk_count = len(chunks)

        record = None
        attempt = 0
        last_error = ""
        failovers_executed = 0

        while attempt <= self.max_retries:
            selected_model = getattr(self.llm_client, 'model', 'unknown_model')
            print(f"\n🔍 [EXTRACTION START] Document: '{document_id}' | Semantic Attempt: {attempt+1}/{self.max_retries+1}")
            print(f"   -> Active Model: {selected_model} | Chunks: {chunk_count}")

            start_time = time.time()
            try:
                if attempt == 0:
                    raw_record = self.extract_grouped_fields(document_id, source_type, chunks)
                else:
                    curr_prompt = base_prompt
                    if last_error:
                        if "JSON" in last_error or "Malformed" in last_error:
                            feedback_str = f"\n\n[PREVIOUS ATTEMPT FAILED JSON PARSING]\nError feedback: {last_error}\nReturn ONLY a valid raw JSON object."
                        elif "SemanticCompletenessError" in last_error:
                            feedback_str = f"\n\n[PREVIOUS ATTEMPT FAILED SEMANTIC COMPLETENESS VALIDATION]\nCorrect issues:\n- {last_error}\nRe-examine text carefully."
                        else:
                            feedback_str = f"\n\n[PREVIOUS ATTEMPT FAILED VALIDATION]\nCorrect issues:\n- {last_error}\nReturn COMPLETE corrected JSON."
                        curr_prompt += feedback_str

                    self.request_accounting["transport_attempts"] += 1
                    raw_record = self.llm_client.generate_structured_output(curr_prompt, {})
                    self.request_accounting["successful_http_responses"] += 1

                elapsed = time.time() - start_time
                print(f"   -> LLM Response Received in {elapsed:.2f}s")
                
                if not isinstance(raw_record, dict):
                    raise InvalidJSONError("LLM response is not a valid JSON dictionary")

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

                # 4. Schema validation
                is_valid, errors = validate_extracted_record(raw_record)
                if not is_valid:
                    last_error = "; ".join(errors)
                    print(f"❌ Attempt {attempt+1} Schema Validation Failed: {last_error}")
                    self.request_accounting["semantic_attempts"] += 1
                    attempt += 1
                    continue

                # 5. Verify evidence snippets against document chunks
                target_fields = get_fields_for_record(raw_record)
                for field_name in target_fields:
                    field_obj = raw_record[field_name]
                    verified_obj, _ = verify_evidence_against_document(field_name, field_obj, chunks)
                    raw_record[field_name] = verified_obj

                # 6. Check generic semantic completeness against document text
                is_complete, completeness_errors = validate_semantic_completeness(raw_record, chunks)
                if not is_complete:
                    print(f"⚠️ Attempt {attempt+1} Semantic Completeness Triggered: {'; '.join(completeness_errors)}")
                    
                    # Attempt Targeted Field Recovery before resorting to full prompt retry!
                    recovered_any = False
                    for field_name, hint_cfg in FIELD_SEMANTIC_HINTS.items():
                        if field_name in raw_record:
                            f_val = raw_record[field_name].get("value")
                            f_stat = raw_record[field_name].get("verification_status")
                            if f_val is None or f_stat == "not_found":
                                rec_ok = self.recover_target_field(field_name, hint_cfg, raw_record, chunks, document_id)
                                if rec_ok:
                                    recovered_any = True

                    # Re-verify completeness after targeted recovery
                    if recovered_any:
                        is_complete, completeness_errors = validate_semantic_completeness(raw_record, chunks)

                    if not is_complete:
                        last_error = "; ".join(completeness_errors)
                        print(f"❌ Attempt {attempt+1} Semantic Completeness Validation Failed after recovery: {last_error}")
                        self.request_accounting["semantic_attempts"] += 1
                        attempt += 1
                        continue

                # 7. Re-canonicalize & Re-validate after evidence verification & semantic completeness
                raw_record = canonicalize_extracted_record(raw_record, document_id)
                is_valid, errors = validate_extracted_record(raw_record)
                if is_valid:
                    record = raw_record
                    self.request_accounting["semantic_attempts"] += 1
                    print(f"✅ [{document_id}] Extraction & Validation PASSED on Attempt {attempt+1} ({time.time()-start_time:.2f}s total)")
                    break
                else:
                    last_error = "; ".join(errors)
                    print(f"❌ Attempt {attempt+1} Evidence Re-validation Failed: {last_error}")
                    self.request_accounting["semantic_attempts"] += 1
                    attempt += 1

            except UnrecoverableLLMError as e:
                print(f"⛔ Unrecoverable API Error for [{document_id}]: {str(e)}")
                raise e

            except LLMTransportError as e:
                elapsed = time.time() - start_time
                self.request_accounting["transport_failures"] += 1
                if isinstance(e, LLMRateLimitError):
                    self.request_accounting["rate_limit_events"] += 1

                print(f"⚠️ [Transport Failure] Model '{selected_model}' experienced {e.__class__.__name__} in {elapsed:.2f}s: {str(e)}")

                if failovers_executed < self.max_model_failovers and hasattr(self.llm_client, "failover_to_next_model"):
                    new_model = self.llm_client.failover_to_next_model()
                    if new_model and new_model != selected_model:
                        failovers_executed += 1
                        self.request_accounting["model_failovers"] += 1
                        print(f"🔄 [Model Failover #{failovers_executed}] Retrying request with candidate model '{new_model}' (semantic attempt {attempt+1} preserved)")
                        continue

                raise e

            except (LLMResponseError, ValueError) as e:
                elapsed = time.time() - start_time
                last_error = str(e)
                self.request_accounting["semantic_attempts"] += 1
                print(f"❌ Attempt {attempt+1} Semantic Validation Failed in {elapsed:.2f}s: {last_error}")
                attempt += 1

        if record is None:
            raise ValueError(f"LLMExtractor failed for [{document_id}] after {self.max_retries+1} semantic attempts. Last error: {last_error}")

        return record

