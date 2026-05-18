"""Neonatal screening evaluation rules for MC-03."""

from datetime import date
from typing import Any

import pandas as pd

from .config import CODIGOS_ESTANDAR, REGLAS_NEGOCIO
from .messages import attention_detail
from .utils import clean_text, has_value, safe_row_value, to_date, to_int, to_number


def valid_tamizaje(row: pd.Series) -> bool:
    age = to_number(safe_row_value(row, "Edad_Atencion_TN"))
    code = clean_text(safe_row_value(row, "Codigo_HIS_TN")).removesuffix(".0")
    window = REGLAS_NEGOCIO["TAMIZAJE_VENTANA"]
    return (
        has_value(safe_row_value(row, "Fecha_Atencion_TN"))
        and code == CODIGOS_ESTANDAR["TAMIZAJE"]
        and age is not None
        and window["inicio_dia"] <= age <= window["fin_dia"]
    )


def tamizaje_detail(row: pd.Series, reference_date: date) -> dict[str, Any]:
    age = to_int(safe_row_value(row, "Edad_Atencion_TN"))
    code = clean_text(safe_row_value(row, "Codigo_HIS_TN")).removesuffix(".0")
    window = REGLAS_NEGOCIO["TAMIZAJE_VENTANA"]

    return attention_detail(
        label="tamizaje neonatal",
        has_attention=has_value(safe_row_value(row, "Fecha_Atencion_TN")),
        valid_code=code == CODIGOS_ESTANDAR["TAMIZAJE"],
        valid_age=age is not None and window["inicio_dia"] <= age <= window["fin_dia"],
        birth_date=to_date(safe_row_value(row, "fec_Nac")),
        start_day=window["inicio_dia"],
        end_day=window["fin_dia"],
        reference_date=reference_date,
        expected_code=CODIGOS_ESTANDAR["TAMIZAJE"],
        actual_code=code,
        actual_age=age,
    )
