"""CRED control evaluation rules for MC-03."""

from datetime import date
from typing import Any

import pandas as pd

from .config import CODIGOS_ESTANDAR, REGLAS_NEGOCIO
from .messages import attention_detail
from .utils import clean_text, has_value, safe_row_value, to_date, to_int, to_number


def valid_cred(row: pd.Series, number: int) -> bool:
    age = to_number(safe_row_value(row, f"Edad_Atencion_{number}"))
    code = clean_text(safe_row_value(row, f"Codigo_HIS_{number}"))
    window_key = ["1ER_CRED", "2DO_CRED", "3ER_CRED"][number - 1]
    window = REGLAS_NEGOCIO["CRED_VENTANAS"][window_key]

    if not (has_value(safe_row_value(row, f"Fecha_Atencion_{number}")) and code == CODIGOS_ESTANDAR["CRED"]):
        return False
    if age is None or not (window["inicio"] <= age <= window["fin"]):
        return False

    if number > 1:
        interval = to_number(safe_row_value(row, f"Intervalo_{number}"))
        if interval is not None and interval < REGLAS_NEGOCIO["INTERVALO_MIN_CRED"]:
            return False

    return True


def cred_detail(row: pd.Series, number: int, reference_date: date) -> dict[str, Any]:
    window_key = ["1ER_CRED", "2DO_CRED", "3ER_CRED"][number - 1]
    window = REGLAS_NEGOCIO["CRED_VENTANAS"][window_key]
    age = to_int(safe_row_value(row, f"Edad_Atencion_{number}"))
    code = clean_text(safe_row_value(row, f"Codigo_HIS_{number}"))
    interval = to_int(safe_row_value(row, f"Intervalo_{number}"))
    interval_valid = number == 1 or interval is None or interval >= REGLAS_NEGOCIO["INTERVALO_MIN_CRED"]

    return attention_detail(
        label=f"CRED {number}",
        has_attention=has_value(safe_row_value(row, f"Fecha_Atencion_{number}")),
        valid_code=code == CODIGOS_ESTANDAR["CRED"],
        valid_age=age is not None and window["inicio"] <= age <= window["fin"],
        birth_date=to_date(safe_row_value(row, "fec_Nac")),
        start_day=window["inicio"],
        end_day=window["fin"],
        reference_date=reference_date,
        expected_code=CODIGOS_ESTANDAR["CRED"],
        actual_code=code,
        actual_age=age,
        interval_valid=interval_valid,
        interval=interval,
    )
