import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from lib.constants import HOTEL_PATH, RESTAURANT_PATH, SIGHTSEEING_PATH, TRANSPORT_PATH
from lib.loaders import read_csv_rows
from lib.validators import ValidationFailure, load_and_validate_sightseeing


def validate_project_data() -> None:
    load_and_validate_sightseeing(SIGHTSEEING_PATH)

    # Empty supporting CSVs are allowed, but the headers should still parse cleanly.
    for path in (HOTEL_PATH, RESTAURANT_PATH, TRANSPORT_PATH):
        read_csv_rows(path)


def main() -> int:
    try:
        validate_project_data()
    except ValidationFailure as exc:
        print("Data validation failed:")
        for error in exc.errors:
            print("- {0}".format(error))
        return 1

    print("Data validation passed: sightseeing and support CSV files are readable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
