import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from build_dashboard import build_dashboard


class BuildDashboardTests(unittest.TestCase):
    def test_dashboard_html_contains_required_sections(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "travel_dashboard.html"
            build_dashboard(output_path)
            html = output_path.read_text(encoding="utf-8")

            self.assertIn("2026年7月_理実誕生日旅行", html)
            self.assertIn("観光候補", html)
            self.assertIn("予約・ToDo", html)
            self.assertIn("未登録", html)
            self.assertIn("tab-button", html)
            self.assertIn("Anniversary Escape", html)
            self.assertIn("Couple itinerary", html)


if __name__ == "__main__":
    unittest.main()
