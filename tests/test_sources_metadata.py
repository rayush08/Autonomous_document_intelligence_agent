import os
import csv
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES_CSV = os.path.join(BASE_DIR, "data", "government_schemes", "sources.csv")


class TestSourcesMetadata(unittest.TestCase):
    def _load_sources(self):
        with open(SOURCES_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return reader.fieldnames, list(reader)

    def test_sources_csv_exists(self):
        self.assertTrue(os.path.exists(SOURCES_CSV), "sources.csv does not exist")

    def test_sources_csv_structure_and_ids(self):
        fieldnames, rows = self._load_sources()
        expected_headers = ['document_id', 'title', 'source_url', 'source_type', 'format', 'domain', 'expected_difficulty', 'notes']
        self.assertEqual(fieldnames, expected_headers, "CSV headers do not match expected specification")
        self.assertEqual(len(rows), 7, "Expected exactly 7 records in sources.csv")

        expected_ids = ['GOV-E-01', 'GOV-E-02', 'GOV-E-03', 'GOV-E-04', 'GOV-M-01', 'GOV-M-02', 'GOV-M-03']
        actual_ids = [r['document_id'] for r in rows]
        self.assertEqual(actual_ids, expected_ids, "Document IDs or ordering in sources.csv do not match specification")

    def test_required_fields_not_empty(self):
        _, rows = self._load_sources()
        required_fields = ['document_id', 'title', 'source_url', 'source_type', 'format', 'domain', 'expected_difficulty']
        for r in rows:
            doc_id = r.get('document_id', 'UNKNOWN')
            for field in required_fields:
                val = r.get(field)
                self.assertTrue(
                    val is not None and str(val).strip() != "",
                    f"Required field '{field}' is empty for document_id '{doc_id}'"
                )

    def test_difficulty_distribution(self):
        _, rows = self._load_sources()
        difficulties = [r['expected_difficulty'].strip() for r in rows]
        
        easy_count = difficulties.count('easy')
        medium_count = difficulties.count('medium')
        
        self.assertEqual(easy_count, 4, f"Expected 4 'easy' difficulty records, got {easy_count}")
        self.assertEqual(medium_count, 3, f"Expected 3 'medium' difficulty records, got {medium_count}")
        self.assertEqual(len(difficulties), 7, "Total difficulty records must equal 7")
        self.assertTrue(all(d in ['easy', 'medium'] for d in difficulties), "All difficulties must be either 'easy' or 'medium'")

    def test_source_url_validation(self):
        _, rows = self._load_sources()
        for r in rows:
            doc_id = r.get('document_id', 'UNKNOWN')
            url = r.get('source_url', '')
            self.assertTrue(url and url.strip() != "", f"source_url is empty for document_id '{doc_id}'")
            self.assertTrue(url.startswith('https://'), f"source_url '{url}' must start with 'https://' for document_id '{doc_id}'")

    def test_format_validation(self):
        _, rows = self._load_sources()
        formats = [r['format'].strip() for r in rows]
        
        for r in rows:
            doc_id = r.get('document_id', 'UNKNOWN')
            fmt = r.get('format', '')
            self.assertIn(fmt, ['HTML', 'PDF'], f"Format '{fmt}' must be 'HTML' or 'PDF' for document_id '{doc_id}'")
            
        self.assertEqual(formats.count('HTML'), 6, f"Expected 6 HTML sources, got {formats.count('HTML')}")
        self.assertEqual(formats.count('PDF'), 1, f"Expected 1 PDF source, got {formats.count('PDF')}")

    def test_domain_consistency(self):
        _, rows = self._load_sources()
        for r in rows:
            doc_id = r.get('document_id', 'UNKNOWN')
            domain = r.get('domain', '').strip()
            self.assertEqual(domain, 'government_schemes', f"Domain for document_id '{doc_id}' must be 'government_schemes', got '{domain}'")


if __name__ == '__main__':
    unittest.main()

