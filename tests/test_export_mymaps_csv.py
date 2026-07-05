import csv
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from export_mymaps_csv import export_mymaps_csv
from lib.constants import SIGHTSEEING_PATH


class ExportMyMapsCsvTests(unittest.TestCase):
    def test_export_creates_expected_columns_and_memo(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "mymaps_import.csv"
            export_mymaps_csv(SIGHTSEEING_PATH, output_path)

            with output_path.open("r", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)

            self.assertEqual(len(rows), 20)
            self.assertEqual(reader.fieldnames[0:4], ["Name", "Address", "Latitude", "Longitude"])
            self.assertIn("優先度:", rows[0]["Memo"])
            self.assertIn("誕生日向き:", rows[0]["Memo"])


if __name__ == "__main__":
    unittest.main()

