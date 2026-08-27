import os
import sys
import json
import re
from abc import ABC, abstractmethod
from datetime import datetime
import jsonschema

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(BASE_DIR, "schemas", "government_scheme.json")
OPPORTUNITY_SCHEMA_PATH = os.path.join(BASE_DIR, "schemas", "opportunity.json")
DOCS_DIR = os.path.join(BASE_DIR, "data", "government_schemes", "documents")
OPP_DOCS_DIR = os.path.join(BASE_DIR, "data", "opportunities", "documents")
FIXTURES_DIR = os.path.join(BASE_DIR, "tests", "fixtures", "extractions")

ALLOWED_VERIFICATION_STATUSES = {
    "verified",
    "unverified",
    "uncertain",
    "rejected",
    "not_found"
}

STATUS_SYNONYM_MAP = {
    "not_verified": "unverified",
    "not verified": "unverified",
    "not-verified": "unverified",
    "unverified_status": "unverified",
    "partially_verified": "uncertain",
    "partially verified": "uncertain",
    "partially-verified": "uncertain",
    "un-certain": "uncertain",
    "notfound": "not_found",
    "not found": "not_found",
    "not-found": "not_found"
}

SCHEMA_FIELDS = [
    "scheme_name",
    "scheme_type",
    "implementing_authority",
    "target_beneficiaries",
    "education_level",
    "age_criteria",
    "income_criteria",
    "academic_criteria",
    "category_criteria",
    "domicile_criteria",
    "benefit_type",
    "benefit_amount",
    "application_method",
    "application_url",
    "required_documents",
    "application_deadline",
    "scheme_status"
]

OPPORTUNITY_SCHEMA_FIELDS = [
    "title",
    "organization",
    "opportunity_type",
    "education_level",
    "eligible_disciplines",
    "skills_required",
    "experience_required",
    "eligibility_notes",
    "location",
    "mode",
    "duration",
    "stipend_or_funding",
    "start_date",
    "application_deadline",
    "application_url",
    "required_documents"
]


def load_schema(domain: str = "government_schemes") -> dict:
    """Load JSON schema definition for specified domain."""
    if domain and any(k in str(domain).lower() for k in ["opportunity", "opportunities", "opp"]):
        schema_path = OPPORTUNITY_SCHEMA_PATH
    else:
        schema_path = SCHEMA_PATH

    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_schema_fields(record_or_domain=None) -> list[str]:
    """Get domain-aware target field names."""
    if isinstance(record_or_domain, str):
        if any(k in record_or_domain.lower() for k in ["opportunity", "opportunities", "opp"]):
            return OPPORTUNITY_SCHEMA_FIELDS
        return SCHEMA_FIELDS

    if isinstance(record_or_domain, dict):
        if "title" in record_or_domain and "organization" in record_or_domain and "scheme_name" not in record_or_domain:
            return OPPORTUNITY_SCHEMA_FIELDS
        if record_or_domain.get("document_metadata", {}).get("document_id", "").startswith("OPP-"):
            return OPPORTUNITY_SCHEMA_FIELDS

    return SCHEMA_FIELDS


get_fields_for_record = get_schema_fields



def load_ingested_artifact(document_id: str) -> dict:
    """Load ingested document artifact from government_schemes or opportunities directory."""
    if str(document_id).startswith("OPP-"):
        path = os.path.join(OPP_DOCS_DIR, f"{document_id}_extracted.json")
    else:
        path = os.path.join(DOCS_DIR, f"{document_id}_extracted.json")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Ingested artifact not found for document_id: '{document_id}' at {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def normalize_verification_statuses(record: dict) -> dict:
    """
    Normalize equivalent verification status terms before schema validation.
    Only maps known equivalent terms (e.g. 'not_verified' -> 'unverified').
    Leaves unknown terms unchanged so strict validation catches invalid statuses.
    """
    if not isinstance(record, dict):
        return record

    target_fields = get_schema_fields(record)
    for field_name in target_fields:
        if field_name in record and isinstance(record[field_name], dict):
            field_obj = record[field_name]
            raw_status = field_obj.get('verification_status')
            if isinstance(raw_status, str):
                norm_key = raw_status.strip().lower()
                if norm_key in STATUS_SYNONYM_MAP:
                    field_obj['verification_status'] = STATUS_SYNONYM_MAP[norm_key]

    return record


def canonicalize_evidence_locator(locator):
    """Normalize string or malformed evidence locators into a valid Locator object."""
    if locator is None:
        return None
    if isinstance(locator, dict):
        if "page" in locator and isinstance(locator["page"], str):
            try:
                locator["page"] = int(locator["page"])
            except ValueError:
                pass
        return locator
    if isinstance(locator, str):
        loc_str = locator.strip()
        if not loc_str:
            return None
        if loc_str.startswith("http://") or loc_str.startswith("https://"):
            return {"url": loc_str}
        page_match = re.search(r'(?:page|pg)\.?\s*(\d+)', loc_str, re.IGNORECASE)
        if page_match:
            try:
                return {"page": int(page_match.group(1)), "section": loc_str}
            except ValueError:
                pass
        return {"section": loc_str}
    return {"section": str(locator)}


def canonicalize_benefit_amount(val):
    """
    Conservatively canonicalize multi-component benefit/stipend strings into a list.
    Preserves numeric thousands-separated numbers (₹50,000, $5,400, 2,700 CHF, 1,25,000)
    and parenthetical expressions completely intact.
    """
    if val is None or isinstance(val, list):
        return val
    if not isinstance(val, str):
        return val
        
    val_str = val.strip()
    if not val_str:
        return None

    # 1. Split by semicolons if present
    if ';' in val_str:
        parts = [p.strip() for p in val_str.split(';') if p.strip()]
        if len(parts) > 1:
            return parts
            
    # 2. Split by newline bullet points or numbered lines
    if '\n' in val_str:
        lines = [re.sub(r'^[\s*\-•\d+.\)]+', '', p).strip() for p in val_str.split('\n') if p.strip()]
        lines = [p for p in lines if len(p) > 2]
        if len(lines) > 1:
            return lines

    # 3. Numbered patterns e.g. 1) ... 2) ... or (i) ... (ii) ...
    numbered_parts = re.split(r'(?:\d+[\.\)]|\([i|v|x]+\))\s*', val_str)
    numbered_parts = [p.strip() for p in numbered_parts if p.strip() and len(p.strip()) > 3]
    if len(numbered_parts) > 1:
        return numbered_parts

    # 4. Independent benefit clauses separated by explicit conjunctions e.g. "..., and ..., plus ..."
    conj_split = re.split(r',\s*(?:and|plus|as well as)\s+', val_str, flags=re.IGNORECASE)
    conj_parts = [p.strip() for p in conj_split if p.strip()]
    if len(conj_parts) >= 2:
        fin_words = ["fee", "stipend", "allowance", "grant", "housing", "travel", "reimbursement", "laptop", "subsistence", "waiver", "cfa"]
        if sum(1 for p in conj_parts if any(w in p.lower() for w in fin_words)) >= 2:
            return conj_parts

    return val_str



def canonicalize_extracted_record(record: dict, document_id: str = None) -> dict:
    """
    Canonicalize raw LLM output record before schema validation.
    - Normalizes status synonyms, locators, benefit_amount/stipend lists.
    - Only injects missing schema fields if record is a valid scheme extraction attempt.
    - Case A (Genuine missing info): value is None/missing and evidence is empty/missing -> canonicalize to not_found.
    - Case B (Claim exists but evidence missing): value is NON-NULL and evidence is empty/missing -> DO NOT convert to not_found! Preserve claim & status so validation rejects it and triggers retry feedback.
    """
    if not isinstance(record, dict):
        return record

    if "document_metadata" not in record or not isinstance(record["document_metadata"], dict):
        record["document_metadata"] = {}

    if document_id and not record["document_metadata"].get("document_id"):
        record["document_metadata"]["document_id"] = document_id
    elif not document_id:
        document_id = record["document_metadata"].get("document_id", "")

    # 1. Normalize status synonyms
    record = normalize_verification_statuses(record)
    target_fields = get_schema_fields(record)

    # Count valid existing schema field dicts
    existing_schema_field_count = sum(
        1 for f in target_fields if f in record and isinstance(record[f], dict)
    )

    # If the LLM returned garbage output (e.g. {"invalid_key": "bad"}), do NOT synthesize schema fields
    is_valid_extraction_attempt = existing_schema_field_count >= 2 or "scheme_name" in record or "title" in record

    # 2. Process schema fields
    for field_name in target_fields:
        if field_name not in record or not isinstance(record[field_name], dict):
            if is_valid_extraction_attempt:
                record[field_name] = {
                    "value": None,
                    "evidence": [],
                    "confidence": 0.0,
                    "verification_status": "not_found"
                }
            continue

        field_obj = record[field_name]

        # Canonicalize benefit_amount / stipend_or_funding
        if field_name in {"benefit_amount", "stipend_or_funding", "required_documents", "category_criteria", "eligible_disciplines"}:
            field_obj["value"] = canonicalize_benefit_amount(field_obj.get("value"))

        status = field_obj.get("verification_status", "not_found")
        val = field_obj.get("value")
        ev_list = field_obj.get("evidence", [])

        # Canonicalize evidence locators
        if isinstance(ev_list, list):
            valid_ev = []
            for ev_item in ev_list:
                if isinstance(ev_item, dict):
                    loc = ev_item.get("locator")
                    ev_item["locator"] = canonicalize_evidence_locator(loc)
                    valid_ev.append(ev_item)
            field_obj["evidence"] = valid_ev

        # Case A: Genuine missing info (value is None or missing AND evidence is empty or missing)
        if status == "not_found" or (val is None and (not field_obj.get("evidence") or len(ev_list) == 0)):
            field_obj["value"] = None
            field_obj["evidence"] = []
            field_obj["confidence"] = 0.0
            field_obj["verification_status"] = "not_found"
            
        # Case B: Claim exists (val is non-null) but evidence is missing (len(ev_list) == 0)
        # DO NOT convert to not_found! Preserve val & status so validate_extracted_record can catch it!

    return record


def validate_extracted_record(record: dict) -> tuple[bool, list[str]]:
    """Validate extracted record against JSON Schema and domain verification constraints."""
    # 0. Normalize status synonyms
    normalize_verification_statuses(record)
    target_fields = get_schema_fields(record)
    domain_name = "opportunities" if target_fields == OPPORTUNITY_SCHEMA_FIELDS else "government_schemes"
    
    errors = []
    
    # 1. JSON Schema validation
    schema = load_schema(domain=domain_name)
    validator = jsonschema.Draft202012Validator(schema)
    for err in validator.iter_errors(record):
        errors.append(f"JSONSchemaError at {list(err.path)}: {err.message}")

    # 2. Verification status and evidence constraints check
    for field_name in target_fields:
        if field_name not in record:
            errors.append(f"MissingField: Expected field '{field_name}' in extracted record")
            continue
            
        field_obj = record[field_name]
        if not isinstance(field_obj, dict):
            errors.append(f"InvalidStructure: Field '{field_name}' must be an object")
            continue
            
        status = field_obj.get('verification_status')
        if status not in ALLOWED_VERIFICATION_STATUSES:
            errors.append(f"InvalidStatus: Field '{field_name}' has unsupported status '{status}'")
            continue
            
        val = field_obj.get('value')
        ev = field_obj.get('evidence', [])
        
        # Rule: verified / unverified / uncertain -> value must be non-null and evidence >= 1 item
        if status in {"verified", "unverified", "uncertain"}:
            if val is None:
                errors.append(f"StatusConstraint: Field '{field_name}' with status '{status}' cannot have value=null")
            if not isinstance(ev, list) or len(ev) < 1:
                errors.append(f"StatusConstraint: Field '{field_name}' with status '{status}' must contain at least 1 evidence item")
            else:
                for idx, item in enumerate(ev):
                    if not isinstance(item, dict) or 'text' not in item or 'locator' not in item:
                        errors.append(f"EvidenceStructure: Field '{field_name}' evidence #{idx+1} missing 'text' or 'locator'")
                        
        # Rule: not_found -> value MUST be null
        elif status == "not_found":
            if val is not None:
                errors.append(f"StatusConstraint: Field '{field_name}' with status 'not_found' MUST have value=null")

    is_valid = (len(errors) == 0)
    return is_valid, errors


class BaseExtractor(ABC):
    """Abstract Base Class for extraction engines."""
    
    @abstractmethod
    def extract(self, document_id: str, ingested_artifact: dict) -> dict:
        """Extract schema-compliant structured record from an ingested artifact."""
        pass


class FixtureExtractor(BaseExtractor):
    """Deterministic extractor that loads pre-computed extraction test fixtures."""
    
    def __init__(self, fixtures_dir: str = FIXTURES_DIR):
        self.fixtures_dir = fixtures_dir

    def extract(self, document_id: str, ingested_artifact: dict) -> dict:
        fixture_path = os.path.join(self.fixtures_dir, f"{document_id}.json")
        if os.path.exists(fixture_path):
            with open(fixture_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        # Default fallback: generate schema-compliant empty record with not_found status
        now_iso = datetime.now().isoformat()
        target_fields = get_schema_fields("opportunity" if str(document_id).startswith("OPP-") else "government")
        record = {
            "document_metadata": {
                "document_id": document_id,
                "source_type": ingested_artifact.get('content_type', 'HTML'),
                "source_identifier": ingested_artifact.get('source_url', ''),
                "extraction_timestamp": now_iso
            }
        }
        for field in target_fields:
            record[field] = {
                "value": None,
                "evidence": [],
                "confidence": 1.0,
                "verification_status": "not_found"
            }
        return record


def extract_document(document_id: str, extractor: BaseExtractor = None) -> dict:
    """Core entry point to extract and validate a government scheme or opportunity record."""
    ingested_artifact = load_ingested_artifact(document_id)
    if extractor is None:
        extractor = FixtureExtractor()
        
    record = extractor.extract(document_id, ingested_artifact)
    is_valid, errors = validate_extracted_record(record)
    
    if not is_valid:
        error_msg = f"Extraction validation failed for [{document_id}]: " + "; ".join(errors)
        raise ValueError(error_msg)
        
    return record


# Lazy import LLMExtractor for export
def get_llm_extractor(*args, **kwargs):
    from src.llm.llm_extractor import LLMExtractor
    return LLMExtractor(*args, **kwargs)


if __name__ == "__main__":
    for doc_id in ['GOV-E-01', 'GOV-M-02', 'GOV-M-03', 'OPP-E-01']:
        res = extract_document(doc_id)
        print(f"✅ [{doc_id}] Extraction & Validation Passed! Document Metadata:", res['document_metadata'])

