import os
import unittest
from src.validator import validate_gold_records


class TestSchemaValidation(unittest.TestCase):
    def test_all_gold_records_schema_validation(self):
        summary = validate_gold_records()
        self.assertEqual(summary['total_records'], 10)
        self.assertEqual(summary['valid_records'], 10, "All 10 gold standard JSON records must pass schema validation")
        self.assertEqual(summary['invalid_records'], 0)



if __name__ == '__main__':
    unittest.main()

