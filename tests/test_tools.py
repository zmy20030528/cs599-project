import unittest

from src.tools import DemoStockTools, validate_request


class ToolTests(unittest.TestCase):
    def test_validate_request(self):
        validate_request("600519", "20260101", "20260622")

    def test_rejects_bad_code(self):
        with self.assertRaises(ValueError):
            validate_request("abc", "20260101", "20260622")

    def test_demo_data_is_labeled(self):
        result = DemoStockTools().get_market_data("600519", "20260101", "20260622")
        self.assertEqual(result["data_source"], "demo_fixture")


if __name__ == "__main__":
    unittest.main()

