import unittest
from src.evaluation.comparison import compare_values, compare_field, normalize_str


class TestPhase6AccuracyHardening(unittest.TestCase):
    """Adversarial regression test suite for Phase 6 accuracy hardening."""

    # Test Group A — Paraphrases
    def test_group_a_equivalent_paraphrases(self):
        self.assertEqual(compare_values("Ministry of Education", "Ministry of Education, Govt of India"), 0.9)
        self.assertEqual(compare_values("Students", "Eligible Students"), 0.9)

    # Test Group B — Non-equivalent Similar Terms
    def test_group_b_non_equivalent_categories(self):
        # Central Sector Scheme vs Centrally Sponsored Scheme must NOT match as exact
        self.assertLess(compare_values("Central Sector Scheme", "Centrally Sponsored Scheme"), 1.0)
        # 600 vs 6000 must NOT match
        self.assertEqual(compare_values("$600", "$6,000"), 0.0)

    # Test Group C — Partial Lists
    def test_group_c_partial_lists(self):
        gold_list = ["Aadhaar Card", "Income Certificate", "Bank Passbook"]
        model_list = ["Aadhaar Card", "Income Certificate"]
        # Partial list (2/3 items) should give score 2/3 = 0.6667
        score = compare_values(gold_list, model_list)
        self.assertAlmostEqual(score, 2.0 / 3.0, places=2)

    # Test Group D — Numeric Values & Units
    def test_group_d_numeric_values_and_units(self):
        # Equivalent currency / unit formats
        self.assertEqual(normalize_str("₹50,000"), "50000 rupees")
        self.assertEqual(normalize_str("Rs. 50,000"), "50000 rupees")
        self.assertEqual(normalize_str("INR 50,000"), "50000 rupees")
        
        # Non-equivalent frequency units must fail
        self.assertNotEqual(normalize_str("₹1,000/month"), normalize_str("₹1,000/year"))

    # Test Group E — Unsupported Values (Hallucination Detection)
    def test_group_e_unsupported_values(self):
        exp_field = {"value": None, "verification_status": "not_found", "evidence": []}
        ext_field = {"value": "Plausible Fake Value", "verification_status": "verified", "evidence": [{"text": "text"}]}
        
        res = compare_field("scheme_name", exp_field, ext_field)
        self.assertTrue(res["is_hallucination"])

    # Test Group F — Gold Dataset Integrity
    def test_group_f_gold_dataset_integrity(self):
        from src.validator import validate_gold_records
        summary = validate_gold_records()
        self.assertEqual(summary["total_records"], 10)
        self.assertEqual(summary["invalid_records"], 0)


if __name__ == "__main__":
    unittest.main()
