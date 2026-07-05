import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.constants import REQUIRED_SIGHTSEEING_COLUMNS, SIGHTSEEING_PATH
from lib.loaders import read_csv_rows
from lib.validators import load_and_validate_sightseeing, validate_sightseeing_rows


class ValidateDataTests(unittest.TestCase):
    def test_sample_sightseeing_csv_is_valid(self):
        rows = load_and_validate_sightseeing(SIGHTSEEING_PATH)
        self.assertEqual(len(rows), 20)

    def test_invalid_priority_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "invalid.csv"
            csv_path.write_text(
                ",".join(REQUIRED_SIGHTSEEING_COLUMNS)
                + "\n"
                + "X001,Test,Area,観光,Z,Tokyo,,,Day1,30,4,中,可,メモ,,Test Search\n",
                encoding="utf-8",
            )
            fieldnames, rows = read_csv_rows(csv_path)
            errors = validate_sightseeing_rows(fieldnames, rows)
            self.assertTrue(any("priority must be one of" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
