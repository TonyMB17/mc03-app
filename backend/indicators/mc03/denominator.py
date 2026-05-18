"""Denominator rules for MC-03."""

import pandas as pd

from .config import REGLAS_NEGOCIO
from .utils import clean_text, month_key, safe_row_value


def is_in_denominator(row: pd.Series, year: int, month: int) -> bool:
    if clean_text(safe_row_value(row, "Mes_eva")) != month_key(year, month):
        return False

    if clean_text(safe_row_value(row, "Obs_Eval")).upper() != "EVALUADO":
        return False

    insurance = clean_text(safe_row_value(row, "Esta_pac")).upper()
    if insurance not in REGLAS_NEGOCIO["SEGUROS_INCLUIDOS"]:
        return False

    return True
