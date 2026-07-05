import sys
from pathlib import Path
from typing import Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from lib.constants import MYMAPS_OUTPUT_PATH, SIGHTSEEING_PATH
from lib.loaders import write_csv_rows
from lib.validators import load_and_validate_sightseeing


MYMAPS_FIELDS = [
    "Name",
    "Address",
    "Latitude",
    "Longitude",
    "Category",
    "Priority",
    "Day",
    "Memo",
    "Area",
    "StayMinutes",
    "BirthdayScore",
    "HeatRisk",
    "RainOK",
    "SourceURL",
]


def build_memo(row: Dict[str, str]) -> str:
    return "\n".join(
        [
            "優先度: {0}".format(row["priority"]),
            "エリア: {0}".format(row["area"]),
            "カテゴリ: {0}".format(row["category"]),
            "滞在目安: {0}分".format(row["stay_minutes"] or "未設定"),
            "誕生日向き: {0}/5".format(row["birthday_score"]),
            "暑さリスク: {0}".format(row["heat_risk"]),
            "雨天対応: {0}".format(row["rain_ok"]),
            "メモ: {0}".format(row["memo"] or "なし"),
        ]
    )


def transform_rows(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    exported_rows: List[Dict[str, str]] = []
    for row in rows:
        exported_rows.append(
            {
                "Name": row["name"],
                "Address": row["address"],
                "Latitude": row["latitude"],
                "Longitude": row["longitude"],
                "Category": row["category"],
                "Priority": row["priority"],
                "Day": row["day_candidate"],
                "Memo": build_memo(row),
                "Area": row["area"],
                "StayMinutes": row["stay_minutes"],
                "BirthdayScore": row["birthday_score"],
                "HeatRisk": row["heat_risk"],
                "RainOK": row["rain_ok"],
                "SourceURL": row["source_url"],
            }
        )
    return exported_rows


def export_mymaps_csv(input_path=SIGHTSEEING_PATH, output_path=MYMAPS_OUTPUT_PATH) -> Path:
    rows = load_and_validate_sightseeing(input_path)
    exported_rows = transform_rows(rows)
    write_csv_rows(output_path, MYMAPS_FIELDS, exported_rows)
    return output_path


def main() -> int:
    output_path = export_mymaps_csv()
    print("Generated My Maps CSV: {0}".format(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

