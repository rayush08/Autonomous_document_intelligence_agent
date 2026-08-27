import os
import unittest
import json
import pypdf
from src.ingestion import clean_html_text

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "data", "government_schemes", "documents")


class TestIngestion(unittest.TestCase):
    def test_clean_html_text(self):
        sample_html = "<html><head><title>Test</title><style>p {color:red;}</style></head><body><h1>Scheme Title</h1><script>alert(1);</script><p>Eligibility details here.</p></body></html>"
        extracted = clean_html_text(sample_html)
        self.assertIn("Scheme Title", extracted)
        self.assertIn("Eligibility details here.", extracted)
        self.assertNotIn("alert(1)", extracted)
        self.assertNotIn("color:red", extracted)

    def test_pdf_ingested_file_and_pages(self):
        pdf_path = os.path.join(DOCS_DIR, "GOV-M-03.pdf")
        self.assertTrue(os.path.exists(pdf_path), "GOV-M-03.pdf must exist in documents dir")
        
        with open(pdf_path, 'rb') as f:
            magic = f.read(10)
            self.assertTrue(magic.startswith(b'%PDF-'), "GOV-M-03.pdf must begin with %PDF- magic bytes")

        pages_json_path = os.path.join(DOCS_DIR, "GOV-M-03_pages.json")
        self.assertTrue(os.path.exists(pages_json_path), "GOV-M-03_pages.json must exist")
        
        with open(pages_json_path, 'r', encoding='utf-8') as jf:
            data = json.load(jf)
            self.assertEqual(data['document_id'], "GOV-M-03")
            self.assertEqual(data['total_pages'], 29)
            self.assertTrue(len(data['pages']) == 29)

    def test_all_7_documents_non_empty_content(self):
        doc_ids = ['GOV-E-01', 'GOV-E-02', 'GOV-E-03', 'GOV-E-04', 'GOV-M-01', 'GOV-M-02', 'GOV-M-03']
        for doc_id in doc_ids:
            extracted_path = os.path.join(DOCS_DIR, f"{doc_id}_extracted.json")
            self.assertTrue(os.path.exists(extracted_path), f"Extracted JSON for {doc_id} must exist")
            with open(extracted_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            content = data.get('content', '')
            self.assertTrue(content and len(content.strip()) > 100, f"Content for {doc_id} must be non-empty and substantial (>100 chars)")

    def test_myscheme_not_shell_html(self):
        myscheme_ids = ['GOV-E-01', 'GOV-E-03', 'GOV-M-02']
        for doc_id in myscheme_ids:
            extracted_path = os.path.join(DOCS_DIR, f"{doc_id}_extracted.json")
            with open(extracted_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.assertEqual(data.get('retrieval_method'), 'official_api', f"{doc_id} must be retrieved via official_api")
            self.assertTrue(data.get('api_slug'), f"{doc_id} must have a non-empty api_slug")
            self.assertTrue(data.get('scheme_id'), f"{doc_id} must have a non-empty scheme_id")
            content = data.get('content', '')
            self.assertGreater(len(content), 2000, f"{doc_id} content must be comprehensive (>2000 chars), not a 644-char HTML shell")

    def test_myscheme_semantic_keywords(self):
        # GOV-E-01 semantic checks
        gov_e01_path = os.path.join(DOCS_DIR, "GOV-E-01_extracted.json")
        with open(gov_e01_path, 'r', encoding='utf-8') as f:
            e01_c = json.load(f).get('content', '').lower()
        self.assertTrue(any(kw in e01_c for kw in ['sc', 'scheduled caste']), "GOV-E-01 must contain SC/Scheduled Caste terms")
        self.assertTrue(any(kw in e01_c for kw in ['post-matric', 'scholarship']), "GOV-E-01 must contain post-matric/scholarship terms")
        self.assertTrue(any(kw in e01_c for kw in ['benefit', 'maintenance', 'financial']), "GOV-E-01 must contain benefit/maintenance terms")
        self.assertTrue(any(kw in e01_c for kw in ['eligibility', 'income']), "GOV-E-01 must contain eligibility/income terms")

        # GOV-E-03 semantic checks
        gov_e03_path = os.path.join(DOCS_DIR, "GOV-E-03_extracted.json")
        with open(gov_e03_path, 'r', encoding='utf-8') as f:
            e03_c = json.load(f).get('content', '').lower()
        self.assertIn("pragati", e03_c, "GOV-E-03 must contain 'pragati'")
        self.assertTrue(any(kw in e03_c for kw in ['girl', 'female', 'women']), "GOV-E-03 must contain girl/female terms")
        self.assertTrue(any(kw in e03_c for kw in ['technical', 'degree']), "GOV-E-03 must contain technical/degree terms")
        self.assertTrue(any(kw in e03_c for kw in ['scholarship', 'benefit']), "GOV-E-03 must contain scholarship/benefit terms")

        # GOV-M-02 semantic checks
        gov_m02_path = os.path.join(DOCS_DIR, "GOV-M-02_extracted.json")
        with open(gov_m02_path, 'r', encoding='utf-8') as f:
            m02_c = json.load(f).get('content', '').lower()
        self.assertTrue(any(kw in m02_c for kw in ['obc', 'ebc', 'dnt']), "GOV-M-02 must contain OBC/EBC/DNT terms")
        self.assertTrue(any(kw in m02_c for kw in ['income', '2,50,000', '2.5']), "GOV-M-02 must contain income limit terms")
        self.assertTrue(any(kw in m02_c for kw in ['tuition', 'college', 'institution']), "GOV-M-02 must contain tuition/college terms")
        self.assertTrue(any(kw in m02_c for kw in ['computer', 'laptop', 'stationery', 'living', 'books']), "GOV-M-02 must contain benefit component terms")


if __name__ == '__main__':
    unittest.main()

