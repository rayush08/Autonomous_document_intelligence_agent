import unittest
from src.evaluation.comparison import compare_values, compare_field, normalize_str
from src.evaluation.metrics import compute_metrics


class TestEvaluatorAndMetrics(unittest.TestCase):

    # CASE 1: Identical values
    def test_case_1_identical_records(self):
        self.assertEqual(compare_values("Test Scheme", "Test Scheme"), 1.0)
        self.assertEqual(compare_values(None, None), 1.0)
        self.assertEqual(compare_values(["Item 1", "Item 2"], ["Item 1", "Item 2"]), 1.0)

    # CASE 2: One incorrect field ratio in metrics
    def test_case_2_one_incorrect_field_ratio(self):
        eval_results = [
            {
                "document_id": "TEST-01",
                "domain": "government_schemes",
                "schema_valid": True,
                "latency_seconds": 0.5,
                "extraction_attempts": 1,
                "field_comparisons": [
                    {"field_name": "f1", "status_match": True, "value_score": 1.0, "value_match": True, "is_genuinely_missing": False, "missing_info_correct": False, "is_hallucination": False, "evidence_grounded": True, "expected_status": "verified", "extracted_status": "verified"},
                    {"field_name": "f2", "status_match": True, "value_score": 1.0, "value_match": True, "is_genuinely_missing": False, "missing_info_correct": False, "is_hallucination": False, "evidence_grounded": True, "expected_status": "verified", "extracted_status": "verified"},
                    {"field_name": "f3", "status_match": False, "value_score": 0.0, "value_match": False, "is_genuinely_missing": False, "missing_info_correct": False, "is_hallucination": False, "evidence_grounded": True, "expected_status": "verified", "extracted_status": "not_found"},
                    {"field_name": "f4", "status_match": True, "value_score": 1.0, "value_match": True, "is_genuinely_missing": False, "missing_info_correct": False, "is_hallucination": False, "evidence_grounded": True, "expected_status": "verified", "extracted_status": "verified"},
                ]
            }
        ]
        metrics = compute_metrics(eval_results)
        overall = metrics.get("overall", {})
        self.assertEqual(overall["total_documents_evaluated"], 1)
        self.assertEqual(overall["field_extraction_accuracy"], 0.75)  # 3 out of 4 correct = 75%

    # CASE 3: Equivalent normalized monetary & period formats
    def test_case_3_equivalent_monetary_formats(self):
        self.assertGreaterEqual(compare_values("Rs. 50,000 per year", "₹50,000/- per annum"), 0.9)
        self.assertGreaterEqual(compare_values("₹50,000", "INR 50,000"), 0.9)
        self.assertGreaterEqual(compare_values("annually", "per year"), 0.9)

    # CASE 4: Multi-component lists in different order
    def test_case_4_multi_component_lists_different_order(self):
        val1 = ["Tuition Fee Waiver", "Monthly Stipend €600", "Mobility Grant €1000"]
        val2 = ["Mobility Grant €1000", "Tuition Fee Waiver", "Monthly Stipend €600"]
        score = compare_values(val1, val2)
        self.assertEqual(score, 1.0, f"Order-independent list comparison should match: score={score}")

    # CASE 5: Different numeric values remain mismatches
    def test_case_5_different_numeric_values_mismatch(self):
        self.assertLess(compare_values("₹50,000 per annum", "₹90,000 per annum"), 0.7)
        self.assertLess(compare_values("$600/week", "$600/month"), 0.7)
        self.assertLess(compare_values("2025", "2026"), 0.7)
        self.assertLess(compare_values("$600", "$6,000"), 0.7)


if __name__ == '__main__':
    unittest.main()

