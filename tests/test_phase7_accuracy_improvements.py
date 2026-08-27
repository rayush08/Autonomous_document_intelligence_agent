import unittest
from src.evaluation.comparison import compare_values, normalize_str


class TestPhase7AccuracyImprovements(unittest.TestCase):
    """Phase 7 required unit and regression test suite."""

    # Test Group A — List Completeness
    def test_group_a_list_completeness(self):
        gold = ["Aadhaar Card", "Income Certificate", "Bank Passbook"]
        
        # Complete list
        self.assertEqual(compare_values(gold, ["Aadhaar Card", "Income Certificate", "Bank Passbook"]), 1.0)
        
        # Reordered equivalent list
        self.assertEqual(compare_values(gold, ["Bank Passbook", "Aadhaar Card", "Income Certificate"]), 1.0)
        
        # Partial list (2/3 items)
        self.assertAlmostEqual(compare_values(gold, ["Aadhaar Card", "Income Certificate"]), 2.0 / 3.0, places=2)
        
        # Duplicate items in extracted list
        self.assertAlmostEqual(compare_values(gold, ["Aadhaar Card", "Aadhaar Card", "Income Certificate"]), 2.0 / 3.0, places=2)

    # Test Group B — Numeric Normalization
    def test_group_b_numeric_normalization(self):
        # Currency equivalences
        self.assertEqual(normalize_str("₹50,000"), "50000 rupees")
        self.assertEqual(normalize_str("50000 rupees"), "50000 rupees")
        self.assertEqual(normalize_str("Rs. 50,000"), "50000 rupees")
        self.assertEqual(normalize_str("₹50000"), "50000 rupees")
        
        # Unequal numbers MUST fail (600 vs 6000)
        self.assertEqual(compare_values("600", "6000"), 0.0)
        self.assertEqual(compare_values("$600", "$6,000"), 0.0)
        
        # Monthly vs Yearly MUST fail
        self.assertNotEqual(normalize_str("₹1,000/month"), normalize_str("₹1,000/year"))
        self.assertEqual(compare_values("Rs 1,000 per month", "Rs 1,000 per year"), 0.0)

    # Test Group C — Unit Normalization
    def test_group_c_unit_normalization(self):
        # Equivalent frequency terms
        self.assertEqual(normalize_str("Rs 10,000 per annum"), normalize_str("Rs 10,000 per year"))
        self.assertEqual(compare_values("Rs 10,000 per annum", "Rs 10,000 per year"), 1.0)
        
        # Non-equivalent period terms MUST fail
        self.assertEqual(compare_values("10 months", "10 years"), 0.0)

    # Test Group D — Taxonomy Normalization
    def test_group_d_taxonomy_normalization(self):
        # Approved equivalent terms or near-synonyms
        self.assertLess(compare_values("Central Sector Scheme", "Centrally Sponsored Scheme"), 1.0)
        self.assertEqual(compare_values("Internship", "Internship Program"), 0.9)
        
        # Genuinely incorrect category MUST fail
        self.assertEqual(compare_values("Government Scheme", "Private Job"), 0.0)

    # Test Group E — Paraphrase Handling
    def test_group_e_paraphrase_handling(self):
        # Semantically equivalent text
        self.assertEqual(compare_values("Ministry of Education", "Ministry of Education, Govt of India"), 0.9)
        
        # Materially different text MUST fail or score low
        self.assertEqual(compare_values("Department of Agriculture", "Ministry of Defense"), 0.0)

    # Test Group F — Regression Protection
    def test_group_f_regression_protection(self):
        from src.validator import validate_gold_records
        summary = validate_gold_records()
        self.assertEqual(summary["total_records"], 10)
        self.assertEqual(summary["invalid_records"], 0)


if __name__ == "__main__":
    unittest.main()
