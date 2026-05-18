"""BCG and HvB evaluation rules for MC-03."""

from datetime import date
from typing import Any

import pandas as pd

from .messages import attention_detail
from .utils import clean_text, has_value, safe_row_value, to_date, to_int, to_number


def valid_vaccine(row: pd.Series, date_col: str, result_col: str, age_col: str) -> bool:
    age = to_number(safe_row_value(row, age_col))
    result = clean_text(safe_row_value(row, result_col)).upper()
    return (
        has_value(safe_row_value(row, date_col))
        and result != "PENDIENTE"
        and age is not None
        and age <= 1
    )


def vaccine_detail(
    row: pd.Series,
    label: str,
    date_col: str,
    result_col: str,
    age_col: str,
    reference_date: date,
) -> dict[str, Any]:
    age = to_int(safe_row_value(row, age_col))
    has_attention = has_value(safe_row_value(row, date_col))
    result = clean_text(safe_row_value(row, result_col)).upper()
    birth_date = to_date(safe_row_value(row, "fec_Nac"))
    detail = attention_detail(
        label=label,
        has_attention=has_attention,
        valid_code=True,
        valid_age=age is not None and age <= 1,
        birth_date=birth_date,
        start_day=0,
        end_day=1,
        reference_date=reference_date,
        actual_age=age,
    )

    if has_attention and result == "PENDIENTE":
        detail["cumple"] = False
        detail["estado"] = "incumplimiento"
        detail["mensaje"] = f"{label} figura como pendiente en el registro."

    return detail
