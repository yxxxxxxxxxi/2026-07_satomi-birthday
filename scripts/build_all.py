import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_dashboard import build_dashboard
from export_mymaps_csv import export_mymaps_csv
from validate_data import validate_project_data


def main() -> int:
    validate_project_data()
    mymaps_path = export_mymaps_csv()
    dashboard_path = build_dashboard()
    print("Build complete.")
    print("- My Maps CSV: {0}".format(mymaps_path))
    print("- Dashboard HTML: {0}".format(dashboard_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

