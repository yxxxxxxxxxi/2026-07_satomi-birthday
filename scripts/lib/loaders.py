import csv
from pathlib import Path
from typing import Dict, List, Tuple


def parse_simple_yaml(text: str) -> Dict[str, object]:
    data: Dict[str, object] = {}
    current_list_key = None

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if line.startswith("  - "):
            if current_list_key is None:
                raise ValueError(
                    "List item found without a parent key on line {0}".format(line_number)
                )
            current_list = data.setdefault(current_list_key, [])
            if not isinstance(current_list, list):
                raise ValueError(
                    "Key {0} is not a list on line {1}".format(current_list_key, line_number)
                )
            current_list.append(line[4:].strip())
            continue

        if line.startswith(" "):
            raise ValueError(
                "Only top-level keys and one-level lists are supported in trip.yaml "
                "at line {0}".format(line_number)
            )

        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError("Invalid YAML line {0}: {1}".format(line_number, line))

        key = key.strip()
        value = value.strip()

        if not value:
            data[key] = []
            current_list_key = key
        else:
            data[key] = value
            current_list_key = None

    return data


def load_trip_config(path: Path) -> Dict[str, object]:
    return parse_simple_yaml(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        raw_fieldnames = reader.fieldnames or []
        fieldnames = [(field or "").strip() for field in raw_fieldnames]
        rows: List[Dict[str, str]] = []

        for raw_row in reader:
            normalized: Dict[str, str] = {}
            for original_name, normalized_name in zip(raw_fieldnames, fieldnames):
                normalized[normalized_name] = (raw_row.get(original_name) or "").strip()
            rows.append(normalized)

    return fieldnames, rows


def write_csv_rows(path: Path, fieldnames: List[str], rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()

