"""Shared parsing and normalization helpers for MC-03."""

from datetime import date, datetime
from typing import Any

import pandas as pd

from .config import ALL_PROVINCES_TOKEN, DEFAULT_PROVINCE, DEFAULT_TARGET_COVERAGE, MONTH_LABELS


def parse_date(value: Any) -> date | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    parsed = pd.to_datetime(value, errors="coerce")
    return parsed.date() if not pd.isna(parsed) else None


def to_date(value: Any) -> date | None:
    return parse_date(value)


def clean_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def to_number(value: Any) -> float | None:
    parsed = pd.to_numeric(value, errors="coerce")
    return None if pd.isna(parsed) else float(parsed)


def to_int(value: Any) -> int | None:
    parsed = to_number(value)
    return None if parsed is None else int(parsed)


def format_date(value: date | None) -> str:
    return value.strftime("%d/%m/%Y") if value else "-"


def has_value(value: Any) -> bool:
    return value is not None and not pd.isna(value) and str(value).strip() != ""


def month_key(year: int, month: int) -> str:
    return f"{year}_{month}"


def parse_month_key(value: Any) -> tuple[int | None, int | None, str | None]:
    text = clean_text(value)
    if "_" not in text:
        return None, None, None

    year_text, month_text = text.split("_", 1)
    try:
        year = int(year_text)
        month = int(month_text)
    except ValueError:
        return None, None, None

    return year, month, MONTH_LABELS.get(month)


def safe_row_value(row: pd.Series, column: str) -> Any:
    return row[column] if column in row.index else None


def normalize_filter(value: str | None, default_province: str = DEFAULT_PROVINCE) -> str | None:
    if value is None:
        return default_province

    normalized = value.strip().upper()
    if normalized in {"", "ALL", "TODOS", ALL_PROVINCES_TOKEN}:
        return None
    return normalized


def normalize_target(value: float | None, default_target: float = DEFAULT_TARGET_COVERAGE) -> float:
    if value is None:
        return float(default_target)

    return max(0.0, min(100.0, float(value)))


def coverage_semaphore(coverage: float, target: float) -> str:
    return "green" if coverage >= target else "red"
