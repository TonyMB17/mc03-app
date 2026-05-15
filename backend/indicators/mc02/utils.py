"""Shared MC-02 parsing helpers.

The indicator depends on Excel values that can arrive as dates, datetimes,
numbers, strings or empty cells. These helpers standardize date formatting,
month labels, numeric conversion, text cleaning and operative Excel flags so
the business-rule modules can stay focused on MC-02 criteria.
"""

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

MONTH_ABBR = {
    1: "ene",
    2: "feb",
    3: "mar",
    4: "abr",
    5: "may",
    6: "jun",
    7: "jul",
    8: "ago",
    9: "set",
    10: "oct",
    11: "nov",
    12: "dic",
}


def clean_value(value: Any) -> str:
    return clean_text(value)


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


def has_value(value: Any) -> bool:
    return bool(clean_value(value))


def flag_is_true(value: Any) -> bool:
    if value is None or pd.isna(value):
        return False
    if isinstance(value, str):
        clean = value.strip().lower()
        return clean in {"1", "cumple", "si", "true", "evaluado"}
    return to_number(value) == 1


def format_short_date(value: date | None) -> str:
    if value is None:
        return ""
    return f"{value.day:02d} {MONTH_ABBR[value.month]} {value.year}"


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
