import json
import tempfile
import unittest
from pathlib import Path

from src.config import Settings
from src.service import analyze_stock


class WorkflowTests(unittest.TestCase):
    def test_end_to_end_and_memory(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = Settings(mode="demo", data_dir=Path(directory))
            first = analyze_stock("600519", "20260101", "20260622", settings, prefer_langgraph=False)
            second = analyze_stock("600519", "20260101", "20260622", settings, prefer_langgraph=False)
            self.assertIn("不构成投资建议", first["final_report"])
            self.assertTrue(second["memory_context"])
            self.assertEqual(first["errors"], [])
            traces = [json.loads(line) for line in settings.trace_path.read_text(encoding="utf-8").splitlines()]
            self.assertGreaterEqual(len(traces), 12)
            self.assertTrue(all(event["status"] == "ok" for event in traces))


if __name__ == "__main__":
    unittest.main()

