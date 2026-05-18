"""Shared helpers for SI-02 parsing and reporting."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd

try:
    from ...core.dates import clean_text
except ImportError:
    from core.dates import clean_text


MONTH_LABELS = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "setiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}


def clean_value(value: Any) -> str:
    return clean_text(value)


def has_value(value: Any) -> bool:
    return bool(clean_value(value))


def to_date(value: Any) -> date | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    parsed = pd.to_datetime(value, errors="coerce")
    return parsed.date() if not pd.isna(parsed) else None


def to_number(value: Any) -> float | None:
    parsed = pd.to_numeric(value, errors="coerce")
    return None if pd.isna(parsed) else float(parsed)


def to_int(value: Any) -> int | None:
    number = to_number(value)
    return None if number is None else int(number)


def normalize_code(value: Any) -> str:
    text = clean_value(value).upper().replace(" ", "")
    if not text:
        return ""
    number = to_number(text)
    if number is not None:
        if number.is_integer():
            return str(int(number))
        return f"{number:.2f}".rstrip("0").rstrip(".")
    return text


def normalize_lab(value: Any) -> str:
    return clean_value(value).upper().replace(" ", "")


def flag_is_true(value: Any) -> bool:
    text = clean_value(value).lower()
    if text in {"1", "cumple", "si", "true", "evaluado"}:
        return True
    number = to_number(value)
    return number == 1


def age_from_birth(row: pd.Series, date_column: str) -> int | None:
    birth = to_date(row.get("FEC_NAC"))
    event_date = to_date(row.get(date_column))
    if birth is None or event_date is None:
        return None
    return (event_date - birth).days


def days_between(row: pd.Series, start_column: str, end_column: str) -> int | None:
    start = to_date(row.get(start_column))
    end = to_date(row.get(end_column))
    if start is None or end is None:
        return None
    return (end - start).days


def parse_month_key(value: Any) -> tuple[int, int, str] | None:
    text = clean_value(value)
    if not text or "_" not in text:
        return None
    year_text, month_text = text.split("_", 1)
    try:
        year = int(float(year_text))
        month = int(float(month_text))
    except ValueError:
        return None
    return year, month, MONTH_LABELS.get(month, text)


def value_in_window(value: int | None, min_value: int, max_value: int) -> bool:
    return value is not None and min_value <= value <= max_value
