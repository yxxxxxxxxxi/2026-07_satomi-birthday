from typing import Dict, List, Optional

from lib.constants import (
    ALLOWED_DAY_CANDIDATES,
    ALLOWED_HEAT_RISK,
    ALLOWED_PRIORITIES,
    ALLOWED_RAIN_OK,
    REQUIRED_SIGHTSEEING_COLUMNS,
    SIGHTSEEING_PATH,
)
from lib.loaders import read_csv_rows


class ValidationFailure(Exception):
    def __init__(self, errors: List[str]):
        super().__init__("\n".join(errors))
        self.errors = errors


def _parse_int(value: str) -> Optional[int]:
    if not value:
        return None
    return int(value)


def _parse_float(value: str) -> Optional[float]:
    if not value:
        return None
    return float(value)


def validate_sightseeing_rows(fieldnames: List[str], rows: List[Dict[str, str]]) -> List[str]:
    errors: List[str] = []
    missing_columns = [
        column for column in REQUIRED_SIGHTSEEING_COLUMNS if column not in fieldnames
    ]
    if missing_columns:
        errors.append("Missing required columns: {0}".format(", ".join(missing_columns)))
        return errors

    for index, row in enumerate(rows, start=2):
        prefix = "Row {0}".format(index)

        if not row.get("id"):
            errors.append("{0}: id is required".format(prefix))
        if not row.get("name"):
            errors.append("{0}: name is required".format(prefix))
        if not row.get("google_maps_search"):
            errors.append("{0}: google_maps_search is required".format(prefix))

        priority = row.get("priority", "")
        if priority not in ALLOWED_PRIORITIES:
            errors.append(
                "{0}: priority must be one of {1}".format(
                    prefix, ", ".join(sorted(ALLOWED_PRIORITIES))
                )
            )

        day_candidate = row.get("day_candidate", "")
        if day_candidate not in ALLOWED_DAY_CANDIDATES:
            errors.append(
                "{0}: day_candidate must be one of {1}".format(
                    prefix, ", ".join(sorted(ALLOWED_DAY_CANDIDATES))
                )
            )

        heat_risk = row.get("heat_risk", "")
        if heat_risk not in ALLOWED_HEAT_RISK:
            errors.append(
                "{0}: heat_risk must be one of {1}".format(
                    prefix, ", ".join(sorted(ALLOWED_HEAT_RISK))
                )
            )

        rain_ok = row.get("rain_ok", "")
        if rain_ok not in ALLOWED_RAIN_OK:
            errors.append(
                "{0}: rain_ok must be one of {1}".format(
                    prefix, ", ".join(sorted(ALLOWED_RAIN_OK))
                )
            )

        try:
            stay_minutes = _parse_int(row.get("stay_minutes", ""))
            if stay_minutes is not None and stay_minutes < 0:
                errors.append("{0}: stay_minutes must be zero or positive".format(prefix))
        except ValueError:
            errors.append("{0}: stay_minutes must be numeric".format(prefix))

        try:
            birthday_score = _parse_int(row.get("birthday_score", ""))
            if birthday_score is None or not 1 <= birthday_score <= 5:
                errors.append("{0}: birthday_score must be in the range 1-5".format(prefix))
        except ValueError:
            errors.append("{0}: birthday_score must be numeric".format(prefix))

        try:
            latitude = _parse_float(row.get("latitude", ""))
            if latitude is not None and not -90 <= latitude <= 90:
                errors.append("{0}: latitude must be between -90 and 90".format(prefix))
        except ValueError:
            errors.append("{0}: latitude must be numeric when present".format(prefix))

        try:
            longitude = _parse_float(row.get("longitude", ""))
            if longitude is not None and not -180 <= longitude <= 180:
                errors.append("{0}: longitude must be between -180 and 180".format(prefix))
        except ValueError:
            errors.append("{0}: longitude must be numeric when present".format(prefix))

    return errors


def load_and_validate_sightseeing(path=SIGHTSEEING_PATH) -> List[Dict[str, str]]:
    fieldnames, rows = read_csv_rows(path)
    errors = validate_sightseeing_rows(fieldnames, rows)
    if errors:
        raise ValidationFailure(errors)
    return rows

