import os
import unittest
from src.medium_integrity import run_medium_integrity_check


class TestMediumDifficultyIntegrity(unittest.TestCase):
    def test_medium_difficulty_integrity(self):
        results = run_medium_integrity_check()
        self.assertTrue(results['GOV-M-01']['integrity_passed'], "GOV-M-01 must pass medium integrity check")
        self.assertTrue(results['GOV-M-02']['integrity_passed'], "GOV-M-02 must pass medium integrity check")
        self.assertTrue(results['GOV-M-03']['integrity_passed'], "GOV-M-03 must pass medium integrity check")


if __name__ == '__main__':
    unittest.main()

