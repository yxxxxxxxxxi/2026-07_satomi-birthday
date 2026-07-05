import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from lib.constants import SIGHTSEEING_PATH
from lib.validators import load_and_validate_sightseeing


def main() -> int:
    rows = load_and_validate_sightseeing(SIGHTSEEING_PATH)
    pending_rows = [
        row for row in rows if not row.get("latitude") or not row.get("longitude")
    ]

    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        print("GOOGLE_MAPS_API_KEY is not set. No API call will be made.")
        print("Candidates that still need coordinates:")
        for row in pending_rows:
            print("- {0}: {1}".format(row["name"], row["google_maps_search"]))
        return 0

    print("API key detected, but automatic geocoding is intentionally disabled in this MVP.")
    print("Use this script as a queue inspector before adding a compliant geocoding client.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

