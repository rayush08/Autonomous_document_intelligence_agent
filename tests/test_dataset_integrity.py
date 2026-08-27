import os
import json
import csv
import unittest
from src.extraction import load_schema, load_ingested_artifact

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_DIR = os.path.join(BASE_DIR, "evaluation", "gold")
SRC_DIR = os.path.join(BASE_DIR, "src")
GOV_SOURCES_CSV = os.path.join(BASE_DIR, "data", "government_schemes", "sources.csv")
OPP_SOURCES_CSV = os.path.join(BASE_DIR, "data", "opportunities", "sources.csv")

ALLOWED_STATUSES = {"verified", "unverified", "uncertain", "rejected", "not_found"}


class TestDatasetIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gov_schema = load_schema(domain="government_schemes")
        cls.opp_schema = load_schema(domain="opportunities")

        # Load sources.csv
        cls.sources = []
        if os.path.exists(GOV_SOURCES_CSV):
            with open(GOV_SOURCES_CSV, 'r', encoding='utf-8') as f:
                cls.sources.extend(list(csv.DictReader(f)))
        if os.path.exists(OPP_SOURCES_CSV):
            with open(OPP_SOURCES_CSV, 'r', encoding='utf-8') as f:
                cls.sources.extend(list(csv.DictReader(f)))

        cls.source_ids = {s['document_id'] for s in cls.sources if s.get('document_id')}

    def test_sources_csv_uniqueness_and_metadata(self):
        """Verify sources.csv entries have unique document_ids and complete metadata."""
        self.assertGreater(len(self.sources), 0)
        seen_ids = set()
        for s in self.sources:
            doc_id = s.get('document_id')
            self.assertTrue(doc_id, f"Missing document_id in sources.csv row: {s}")
            self.assertNotIn(doc_id, seen_ids, f"Duplicate document_id in sources.csv: {doc_id}")
            seen_ids.add(doc_id)
            self.assertTrue(s.get('source_url'), f"[{doc_id}] Missing source_url in sources.csv")
            self.assertTrue(s.get('domain'), f"[{doc_id}] Missing domain in sources.csv")

    def test_gold_fixtures_integrity(self):
        """Verify all gold fixture JSON files match schema field constraints and ingested artifacts."""
        gold_files = [f for f in os.listdir(GOLD_DIR) if f.endswith('.json')]
        self.assertGreaterEqual(len(gold_files), 10, "Dataset must contain at least 10 gold fixtures across domains")

        gold_doc_ids = set()
        for gfile in gold_files:
            doc_id = gfile.replace('.json', '')
            self.assertNotIn(doc_id, gold_doc_ids, f"Duplicate gold fixture ID: {doc_id}")
            gold_doc_ids.add(doc_id)

            # 1. Verify corresponding ingested document artifact exists
            artifact = load_ingested_artifact(doc_id)
            self.assertEqual(artifact.get('document_id'), doc_id)

            # 2. Load gold file
            gold_path = os.path.join(GOLD_DIR, gfile)
            with open(gold_path, 'r', encoding='utf-8') as f:
                rec = json.load(f)

            # 3. Check metadata
            self.assertIn('document_metadata', rec)
            self.assertEqual(rec['document_metadata'].get('document_id'), doc_id)

            # 4. Check schema fields based on domain
            if doc_id.startswith('OPP-'):
                expected_fields = [k for k in rec.keys() if k != 'document_metadata']
                valid_schema_keys = set(self.opp_schema['properties'].keys())
            else:
                expected_fields = [k for k in rec.keys() if k != 'document_metadata']
                valid_schema_keys = set(self.gov_schema['properties'].keys())

            for fkey in expected_fields:
                self.assertIn(fkey, valid_schema_keys, f"[{doc_id}] Unknown ground truth field: {fkey}")
                fobj = rec[fkey]
                self.assertIsInstance(fobj, dict, f"[{doc_id}] Field '{fkey}' must be a dict")
                
                status = fobj.get('verification_status')
                self.assertIn(status, ALLOWED_STATUSES, f"[{doc_id}] Field '{fkey}' invalid status: {status}")

                val = fobj.get('value')
                ev = fobj.get('evidence', [])

                if status == 'not_found':
                    self.assertIsNone(val, f"[{doc_id}] Field '{fkey}' with status 'not_found' must have value=None")
                    self.assertEqual(ev, [], f"[{doc_id}] Field '{fkey}' with status 'not_found' must have empty evidence []")
                elif status in {'verified', 'unverified', 'uncertain'}:
                    self.assertIsNotNone(val, f"[{doc_id}] Field '{fkey}' with status '{status}' cannot have value=None")
                    self.assertGreaterEqual(len(ev), 1, f"[{doc_id}] Field '{fkey}' with status '{status}' must contain at least 1 evidence item")
                    for ev_item in ev:
                        self.assertIn('text', ev_item)
                        self.assertIn('locator', ev_item)

    def test_malformed_ground_truth_rejected(self):
        """Verify that malformed ground-truth structures fail validation."""
        malformed_record = {
            "document_metadata": {"document_id": "TEST-BAD"},
            "scheme_name": {
                "value": "Test Scheme",
                "evidence": [],  # Missing evidence for verified status!
                "confidence": 1.0,
                "verification_status": "verified"
            }
        }
        from src.extraction import validate_extracted_record
        is_valid, errors = validate_extracted_record(malformed_record)
        self.assertFalse(is_valid)
        self.assertTrue(any("must contain at least 1 evidence item" in err for err in errors))

    def test_no_gold_fixture_imports_in_extraction_code(self):
        """Verify production extraction modules NEVER import or access evaluation/gold data."""
        forbidden_references = ["evaluation/gold", "evaluation.gold", "evaluation\\gold"]
        for root, _, files in os.walk(SRC_DIR):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    for forbidden in forbidden_references:
                        self.assertNotIn(
                            forbidden, content,
                            f"Benchmark Leakage Violation: File {filepath} contains forbidden reference '{forbidden}'"
                        )


if __name__ == '__main__':
    unittest.main()

