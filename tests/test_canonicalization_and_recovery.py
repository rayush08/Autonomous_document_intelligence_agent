import unittest
from src.extraction import canonicalize_benefit_amount


class TestCanonicalizationAndRecovery(unittest.TestCase):

    def test_01_preserve_thousands_separated_inr(self):
        """₹50,000/- per annum must NOT be split into a list."""
        val = "₹50,000/- per annum"
        res = canonicalize_benefit_amount(val)
        self.assertEqual(res, "₹50,000/- per annum")
        self.assertIsInstance(res, str)

    def test_02_preserve_thousands_separated_usd(self):
        """$5,400 for the full 9-week program must NOT be split into a list."""
        val = "Weekly stipend of $600 per week ($5,400 for the full 9-week program)"
        res = canonicalize_benefit_amount(val)
        self.assertEqual(res, "Weekly stipend of $600 per week ($5,400 for the full 9-week program)")
        self.assertIsInstance(res, str)

    def test_03_preserve_thousands_separated_chf(self):
        """approx. 2,700 CHF per month must NOT be split into a list."""
        val = "Subsistence allowance of approx. 2,700 CHF per month"
        res = canonicalize_benefit_amount(val)
        self.assertEqual(res, "Subsistence allowance of approx. 2,700 CHF per month")
        self.assertIsInstance(res, str)

    def test_04_preserve_indian_numbering_format(self):
        """1,25,000 per annum must NOT be split into a list."""
        val = "Rs. 1,25,000 per annum"
        res = canonicalize_benefit_amount(val)
        self.assertEqual(res, "Rs. 1,25,000 per annum")
        self.assertIsInstance(res, str)

    def test_05_semicolon_separated_benefits_split(self):
        """Multi-clause benefits separated by semicolons are split into a list."""
        val = "₹37,000 per month; ₹20,000 annual grant; ₹42,000 thereafter"
        res = canonicalize_benefit_amount(val)
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0], "₹37,000 per month")
        self.assertEqual(res[1], "₹20,000 annual grant")
        self.assertEqual(res[2], "₹42,000 thereafter")


if __name__ == '__main__':
    unittest.main()

