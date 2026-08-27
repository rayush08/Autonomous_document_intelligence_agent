import os
import sys
import json
import jsonschema

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(BASE_DIR, "schemas", "government_scheme.json")
GOLD_DIR = os.path.join(BASE_DIR, "evaluation", "gold")


def load_schema():
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as sf:
        return json.load(sf)


def validate_gold_records():
    schema = load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    
    gold_files = [f for f in os.listdir(GOLD_DIR) if f.endswith('.json')]
    gold_files.sort()
    
    validation_summary = {
        "total_records": len(gold_files),
        "valid_records": 0,
        "invalid_records": 0,
        "details": []
    }

    print(f"Validating {len(gold_files)} gold records against {SCHEMA_PATH}...\n")

    for gf in gold_files:
        file_path = os.path.join(GOLD_DIR, gf)
        with open(file_path, 'r', encoding='utf-8') as f:
            record_data = json.load(f)

        errors = list(validator.iter_errors(record_data))
        is_valid = (len(errors) == 0)
        
        detail = {
            "file_name": gf,
            "document_id": record_data.get("document_metadata", {}).get("document_id"),
            "is_valid": is_valid,
            "error_count": len(errors),
            "errors": [err.message for err in errors]
        }

        if is_valid:
            validation_summary["valid_records"] += 1
            print(f"✅ [{gf}] SCHEMA VALIDATION PASSED")
        else:
            validation_summary["invalid_records"] += 1
            print(f"❌ [{gf}] SCHEMA VALIDATION FAILED ({len(errors)} errors)")
            for err in errors:
                print(f"   -> Error: {err.message} at {list(err.path)}")

        validation_summary["details"].append(detail)

    print(f"\nSchema Validation Summary: {validation_summary['valid_records']}/{validation_summary['total_records']} records valid.")
    return validation_summary


if __name__ == "__main__":
    validate_gold_records()

