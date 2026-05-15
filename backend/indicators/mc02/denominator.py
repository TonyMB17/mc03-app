"""Denominator rules for MC-02.

The denominator uses the birth cohort month ``Mes_Nac`` and includes records
with ``Registros = 1`` after the active province filter. Insurance is read from
``Obs_Niño`` and includes SIS plus empty/no-insurance values. Known low birth
weight (< 2500 g) or prematurity (< 37 weeks) are excluded; empty weight or
gestational age is kept in the denominator because exclusion cannot be proven.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .rules import (
    DENOMINATOR_COLUMN,
    EXCLUSION_CRITERIA,
    INCLUDED_DENOMINATOR_VALUE,
    INCLUDED_INSURANCE_TYPES,
    INSURANCE_COLUMN,
)
from .utils import clean_value, to_date, to_int, to_number


def age_at_cutoff(row: pd.Series, reference_date=None) -> int | None:
    birth_date = to_date(row.get("Fec_Nac"))
    if birth_date is not None and reference_date is not None:
        return (reference_date - birth_date).days
    return to_int(row.get("Edad_Act(dia)"))


def insurance_included(row: pd.Series) -> bool:
    insurance = clean_value(row.get(INSURANCE_COLUMN)).upper()
    return insurance in INCLUDED_INSURANCE_TYPES


def has_exclusion(row: pd.Series) -> bool:
    weight = to_number(row.get(EXCLUSION_CRITERIA["COLUMNA_PESO"]))
    gestational_age = to_number(row.get(EXCLUSION_CRITERIA["COLUMNA_GESTACION"]))

    low_weight = weight is not None and weight < EXCLUSION_CRITERIA["PESO_MIN"]
    premature = gestational_age is not None and gestational_age < EXCLUSION_CRITERIA["GESTACION_MIN"]
    return low_weight or premature


def age_included(row: pd.Series, reference_date=None) -> bool:
    age = age_at_cutoff(row, reference_date)
    return age is not None and 0 <= age <= 364


def is_in_denominator(row: pd.Series, reference_date=None) -> bool:
    return (
        to_number(row.get(DENOMINATOR_COLUMN)) == INCLUDED_DENOMINATOR_VALUE
        and age_included(row, reference_date)
        and insurance_included(row)
        and not has_exclusion(row)
    )


def denominator_counts(df: pd.DataFrame, reference_date=None) -> dict[str, int]:
    if df.empty:
        return {}

    base_mask = (
        pd.to_numeric(df[DENOMINATOR_COLUMN], errors="coerce") == INCLUDED_DENOMINATOR_VALUE
        if DENOMINATOR_COLUMN in df
        else pd.Series(False, index=df.index)
    )

    weight_column = EXCLUSION_CRITERIA["COLUMNA_PESO"]
    gestation_column = EXCLUSION_CRITERIA["COLUMNA_GESTACION"]
    weight = pd.to_numeric(df[weight_column], errors="coerce") if weight_column in df else pd.Series(pd.NA, index=df.index)
    gestational_age = pd.to_numeric(df[gestation_column], errors="coerce") if gestation_column in df else pd.Series(pd.NA, index=df.index)
    low_weight = base_mask & weight.notna() & (weight < EXCLUSION_CRITERIA["PESO_MIN"])
    premature = base_mask & gestational_age.notna() & (gestational_age < EXCLUSION_CRITERIA["GESTACION_MIN"])
    unknown_exclusion_data = base_mask & (weight.isna() | gestational_age.isna())
    excluded = low_weight | premature
    insurance_included_mask = base_mask & df.apply(lambda row: insurance_included(row), axis=1)
    age_included_mask = base_mask & df.apply(lambda row: age_included(row, reference_date), axis=1)
    age_values = df.apply(lambda row: age_at_cutoff(row, reference_date), axis=1)
    age_unknown = base_mask & age_values.isna()
    age_over_limit = base_mask & age_values.notna() & ((age_values < 0) | (age_values > 364))

    return {
        "registros_base": int(base_mask.sum()),
        "edad_0_364": int(age_included_mask.sum()),
        "excluidos_edad_fuera_rango": int(age_over_limit.sum()),
        "excluidos_edad_insuficiente": int(age_unknown.sum()),
        "seguros_incluidos": int(insurance_included_mask.sum()),
        "excluidos_tipo_seguro": int((base_mask & ~insurance_included_mask).sum()),
        "excluidos_bajo_peso": int(low_weight.sum()),
        "excluidos_prematuridad": int(premature.sum()),
        "con_peso_o_eg_vacio_incluidos": int((unknown_exclusion_data & age_included_mask & insurance_included_mask & ~excluded).sum()),
        "denominador_final": int((base_mask & age_included_mask & insurance_included_mask & ~excluded).sum()),
    }
