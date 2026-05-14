from datetime import date, datetime
from typing import Any

import pandas as pd


def parse_excel_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    parsed = pd.to_datetime(value, errors="coerce")
    return parsed.date() if not pd.isna(parsed) else None


def clean_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    text = str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        return text[:-2]
    return "" if text.lower() == "nan" else text
