import os
import json
import csv
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "data", "government_schemes", "documents")
SOURCES_CSV = os.path.join(BASE_DIR, "data", "government_schemes", "sources.csv")


def load_extracted_json(doc_id):
    path = os.path.join(DOCS_DIR, f"{doc_id}_extracted.json")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


class TestExtractionQualityAndProvenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SOURCES_CSV, 'r', encoding='utf-8') as f:
            cls.sources_list = list(csv.DictReader(f))
        cls.sources_map = {s['document_id']: s for s in cls.sources_list}

    # =========================================================================
    # 1. PROVENANCE INTEGRITY TESTS
    # =========================================================================
    def test_provenance_integrity(self):
        allowed_methods = {'html_parsing', 'official_api', 'pdf_text_extractor'}
        
        for s in self.sources_list:
            doc_id = s['document_id']
            data = load_extracted_json(doc_id)
            
            # 1. document_id presence and match
            self.assertEqual(data.get('document_id'), doc_id, f"[{doc_id}] document_id mismatch")
            
            # 2. source_url exact match
            self.assertEqual(data.get('source_url'), s['source_url'], f"[{doc_id}] source_url mismatch")
            
            # 3. retrieval_method in allowed set
            ret_method = data.get('retrieval_method')
            self.assertIn(ret_method, allowed_methods, f"[{doc_id}] invalid retrieval_method: {ret_method}")
            
            # 4. official_api requirements
            if ret_method == 'official_api':
                self.assertTrue(data.get('content_source'), f"[{doc_id}] missing content_source")
                self.assertTrue(data.get('api_slug'), f"[{doc_id}] missing api_slug")
                self.assertTrue(data.get('scheme_id'), f"[{doc_id}] missing scheme_id")
                
            # 5. pdf_text_extractor requirements
            if ret_method == 'pdf_text_extractor':
                self.assertEqual(data.get('page_count'), 29, f"[{doc_id}] page_count must be 29")
                
                # Check pages.json structure
                pages_path = os.path.join(DOCS_DIR, f"{doc_id}_pages.json")
                self.assertTrue(os.path.exists(pages_path), f"[{doc_id}] _pages.json missing")
                with open(pages_path, 'r', encoding='utf-8') as pf:
                    pdata = json.load(pf)
                self.assertEqual(pdata.get('total_pages'), 29)
                self.assertEqual(len(pdata.get('pages', [])), 29)
                
                # Check raw PDF binary magic bytes
                raw_pdf_path = os.path.join(DOCS_DIR, f"{doc_id}.pdf")
                self.assertTrue(os.path.exists(raw_pdf_path), f"[{doc_id}] raw PDF missing")
                with open(raw_pdf_path, 'rb') as pdf_file:
                    magic = pdf_file.read(10)
                    self.assertTrue(magic.startswith(b'%PDF-'), f"[{doc_id}] invalid PDF magic bytes")

    # =========================================================================
    # 2. SOURCE-SPECIFIC EXTRACTION CORRECTNESS TESTS
    # =========================================================================
    def test_gov_e01_extraction_correctness(self):
        c = load_extracted_json('GOV-E-01').get('content', '').lower()
        self.assertTrue(any(k in c for k in ['scheduled caste', 'sc students']), "GOV-E-01 missing SC category terms")
        self.assertTrue(any(k in c for k in ['post-matric', 'post matric']), "GOV-E-01 missing post-matric terms")
        self.assertTrue(any(k in c for k in ['2,50,000', '2.50 lakh', '2.5 lakh']), "GOV-E-01 missing 2.50L income criterion")
        self.assertTrue(any(k in c for k in ['maintenance allowance', 'academic allowance', 'scholarship', 'compulsory non-refundable fees']), "GOV-E-01 missing benefit terms")

    def test_gov_e02_extraction_correctness(self):
        c = load_extracted_json('GOV-E-02').get('content', '').lower()
        self.assertTrue(any(k in c for k in ['csir', 'csir-ugc net']), "GOV-E-02 missing CSIR terms")
        self.assertTrue(any(k in c for k in ['jrf', 'junior research fellowship']), "GOV-E-02 missing JRF terms")
        self.assertTrue(any(k in c for k in ['m.sc', 'b.e', 'b.tech', 'mbbs', 'bs']), "GOV-E-02 missing educational qualification terms")
        self.assertTrue(any(k in c for k in ['31,000', '37,000', 'stipend', 'contingency']), "GOV-E-02 missing fellowship rate terms")

    def test_gov_e03_extraction_correctness(self):
        c = load_extracted_json('GOV-E-03').get('content', '').lower()
        self.assertIn("pragati", c, "GOV-E-03 missing 'pragati'")
        self.assertTrue(any(k in c for k in ['girl', 'female', 'women']), "GOV-E-03 missing female eligibility terms")
        self.assertTrue(any(k in c for k in ['technical degree', 'degree course']), "GOV-E-03 missing technical degree terms")
        self.assertTrue(any(k in c for k in ['8 lakh', '8,00,000']), "GOV-E-03 missing 8 lakh income ceiling")
        self.assertTrue(any(k in c for k in ['50,000', '50000']), "GOV-E-03 missing 50,000 scholarship benefit amount")

    def test_gov_e04_extraction_correctness(self):
        c = load_extracted_json('GOV-E-04').get('content', '').lower()
        self.assertTrue(any(k in c for k in ['pm-ajay', 'pradhan mantri anusuchit jaati abhyuday']), "GOV-E-04 missing scheme title terms")
        self.assertTrue(any(k in c for k in ['scheduled caste', 'sc']), "GOV-E-04 missing SC category terms")
        self.assertTrue(any(k in c for k in ['adarsh gram', 'grant-in-aid', 'hostels', 'livelihood']), "GOV-E-04 missing scheme component terms")

    def test_gov_m01_extraction_correctness(self):
        c = load_extracted_json('GOV-M-01').get('content', '').lower()
        self.assertTrue(any(k in c for k in ['st students', 'scheduled tribe', 'national tribal fellowship']), "GOV-M-01 missing ST category terms")
        self.assertTrue(any(k in c for k in ['higher education', 'ph.d', 'm.phil', 'fellowship']), "GOV-M-01 missing higher education research terms")
        self.assertTrue(any(k in c for k in ['fellowship', 'fellowship amount', 'revision of fellowship', 'stipend']), "GOV-M-01 missing fellowship rate / revision terms")

    def test_gov_m02_extraction_correctness(self):
        c = load_extracted_json('GOV-M-02').get('content', '').lower()
        self.assertTrue(any(k in c for k in ['obc', 'ebc', 'dnt']), "GOV-M-02 missing category terms (OBC/EBC/DNT)")
        self.assertTrue(any(k in c for k in ['2.5 lakh', '2.50 lakh', '2.50 lakhs', '2,50,000']), "GOV-M-02 missing 2.5 lakh income limit")
        self.assertTrue(any(k in c for k in ['tuition fee', 'notified institution', 'top class college']), "GOV-M-02 missing tuition/institution terms")
        self.assertTrue(any(k in c for k in ['living expenses', '36,000', 'books', '5,000', 'computer', 'laptop', '45,000']), "GOV-M-02 missing multi-component benefit package terms")

    def test_gov_m03_extraction_correctness(self):
        c = load_extracted_json('GOV-M-03').get('content', '').lower()
        self.assertTrue(any(k in c for k in ['national bioenergy programme', 'biomass programme']), "GOV-M-03 missing title terms")
        self.assertTrue(any(k in c for k in ['central financial assistance', 'cfa']), "GOV-M-03 missing CFA terms")
        self.assertTrue(any(k in c for k in ['pellet', 'briquette', 'cogeneration']), "GOV-M-03 missing pellet/briquette/cogeneration terms")
        self.assertTrue(any(k in c for k in ['3 lakh', '1.5 lakh', '40 lakh']), "GOV-M-03 missing multi-tier capacity financial assistance figures")
        self.assertTrue(any(k in c for k in ['biourja', 'biourja.mnre.gov.in']), "GOV-M-03 missing BioURJA portal application reference")
        self.assertTrue(any(k in c for k in ['31.03.2026', '2025-26']), "GOV-M-03 missing application deadline / scheme timeline evidence")

    # =========================================================================
    # 3. SOURCE-CONTENT CONTAMINATION SANITY CHECKS
    # =========================================================================
    def test_source_content_contamination(self):
        # GOV-M-02 must NOT contain unrelated PMMVY scheme content
        m02_c = load_extracted_json('GOV-M-02').get('content', '').lower()
        self.assertNotIn("matru vandana", m02_c, "GOV-M-02 contaminated with PMMVY content")
        
        # GOV-E-03 must NOT contain Saksham or Swanath scheme text
        e03_c = load_extracted_json('GOV-E-03').get('content', '').lower()
        self.assertNotIn("saksham", e03_c, "GOV-E-03 contaminated with Saksham scheme text")
        self.assertNotIn("swanath", e03_c, "GOV-E-03 contaminated with Swanath scheme text")

        # GOV-E-01 must NOT contain PM-YASASVI scheme title text
        e01_c = load_extracted_json('GOV-E-01').get('content', '').lower()
        self.assertNotIn("pm-yasasvi", e01_c, "GOV-E-01 contaminated with PM-YASASVI text")


if __name__ == '__main__':
    unittest.main()

