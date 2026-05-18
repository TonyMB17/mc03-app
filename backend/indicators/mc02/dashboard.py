"""Dashboard aggregations and filter options for MC-02."""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from .config import DEFAULT_PROVINCE, DEFAULT_TARGET_COVERAGE
from .denominator import is_in_denominator
from .evaluator import COMPONENTS, evaluate_package
from .excel_loader import unique_text_values
from .iron import anemia_alerts
from .rules import (
    ACTIVE_COMPONENT_FLAGS,
    DENOMINATOR_COLUMN,
    EXCLUSION_CRITERIA,
    INCLUDED_DENOMINATOR_VALUE,
    INCLUDED_INSURANCE_TYPES,
    INSURANCE_COLUMN,
    MONTH_COLUMN,
    OMITTED_CURRENT_CRITERIA,
    PROVINCE_COLUMN,
)
from .utils import clean_value, parse_month_key


ALL_PROVINCES_TOKEN = "__ALL__"
COMPONENT_LABELS = {component["key"]: component["label"] for component in COMPONENTS}


def normalize_target(value: float | None) -> float:
    return DEFAULT_TARGET_COVERAGE if value is None else float(value)


def coverage_semaphore(coverage: float, target: float) -> str:
    return "green" if coverage >= target else "red"


def filter_data(df: pd.DataFrame, province: str | None = DEFAULT_PROVINCE) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    if not province or province == ALL_PROVINCES_TOKEN:
        return df
    if PROVINCE_COLUMN not in df:
        return df.iloc[0:0]
    return df[df[PROVINCE_COLUMN].astype(str).str.strip().str.upper() == province.strip().upper()]


def get_filter_options(df: pd.DataFrame) -> dict[str, Any]:
    return {
        "provinces": unique_text_values(df, PROVINCE_COLUMN),
        "default_province": DEFAULT_PROVINCE,
        "default_target_coverage": DEFAULT_TARGET_COVERAGE,
        "included_insurance_types": ["SIS", "Sin seguro (celda vacia)"],
        "exclusion_criteria": {
            "included_population": f"{DENOMINATOR_COLUMN} = {INCLUDED_DENOMINATOR_VALUE}",
            "excluded_population": f"{DENOMINATOR_COLUMN} vacio o diferente de {INCLUDED_DENOMINATOR_VALUE}",
            "included_insurance_column": INSURANCE_COLUMN,
            "included_insurance_types": sorted(INCLUDED_INSURANCE_TYPES),
            "birth_weight_min": EXCLUSION_CRITERIA["PESO_MIN"],
            "gestational_age_min": EXCLUSION_CRITERIA["GESTACION_MIN"],
            "exclusion_source": EXCLUSION_CRITERIA["FUENTE"],
            "exclusion_note": EXCLUSION_CRITERIA["NOTA"],
            "active_components": ACTIVE_COMPONENT_FLAGS,
            "omitted_now": OMITTED_CURRENT_CRITERIA,
        },
    }


def first_failed_detail(package: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    for key, detail in package["details"].items():
        if not detail["cumple"]:
            return key, detail
    return None, None


def failed_details(package: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    return [(key, detail) for key, detail in package["details"].items() if not detail["cumple"]]


def component_label(component_key: str) -> str:
    return COMPONENT_LABELS.get(component_key, component_key)


def observed_components_text(package: dict[str, Any]) -> str:
    return "; ".join(component_label(key) for key, _ in failed_details(package))


def labeled_failure_reasons(package: dict[str, Any]) -> str:
    reasons = []
    for key, detail in failed_details(package):
        message = clean_value(detail.get("mensaje"))
        if message:
            reasons.append(f"{component_label(key)}: {message}")
    return "\n".join(reasons)


def omiso_from_row(row: pd.Series, package: dict[str, Any]) -> dict[str, Any]:
    parsed_month = parse_month_key(row.get(MONTH_COLUMN))
    year, month_name = (parsed_month[0], parsed_month[2]) if parsed_month else (None, None)
    component_key, failed_detail = first_failed_detail(package)
    components_text = observed_components_text(package)
    return {
        "Mes_eva": clean_value(row.get(MONTH_COLUMN)) or None,
        "month": month_name,
        "year": year,
        "afi_DNI": clean_value(row.get("DNI o CNV")) or None,
        "NumCNV": clean_value(row.get("NumCNV")) or None,
        "fec_Nac": clean_value(row.get("Fec_Nac")) or None,
        "afi_nombres": clean_value(row.get("Nombres")) or None,
        "afi_appaterno": clean_value(row.get("Ape_Paterno")) or None,
        "afi_apmaterno": clean_value(row.get("Ape_Materno")) or None,
        "Desc_prov": clean_value(row.get(PROVINCE_COLUMN)) or None,
        "Des_MicroRed": clean_value(row.get("MicroRed")) or None,
        "pre_CodigoRENAES": clean_value(row.get("Renaes")) or None,
        "Des_EESS": clean_value(row.get("EESS")) or None,
        "component": component_key,
        "components_observed": components_text or (component_label(component_key) if component_key else None),
        "attention_date": failed_detail.get("fecha") if failed_detail else None,
        "attention_age_days": failed_detail.get("edad_atencion_dias") if failed_detail else None,
        "attention_facility": failed_detail.get("establecimiento_atencion") if failed_detail else None,
        "attention_professional": failed_detail.get("profesional") if failed_detail else None,
        "clinical_alerts": anemia_alerts(row),
        "reason": labeled_failure_reasons(package)
        or clean_value(row.get("Obs_General"))
        or "No cumple paquete integrado.",
    }


def build_report_summary(
    df: pd.DataFrame,
    cutoff_date: date | None = None,
    province: str | None = DEFAULT_PROVINCE,
    target_coverage: float | None = None,
) -> dict[str, Any]:
    df = filter_data(df, province)
    target = normalize_target(target_coverage)
    denominator_df = df[df.apply(lambda row: is_in_denominator(row, cutoff_date), axis=1)]

    month_keys = []
    for value in denominator_df.get(MONTH_COLUMN, pd.Series(dtype=object)).dropna().unique().tolist():
        parsed = parse_month_key(value)
        if parsed:
            month_keys.append(parsed)
    month_keys = sorted(set(month_keys), key=lambda item: (item[0], item[1]))

    monthly = []
    omisos = []
    for year, month, month_name in month_keys:
        key = f"{year}_{month}"
        month_df = denominator_df[denominator_df[MONTH_COLUMN].astype(str).str.strip() == key]
        numerator = 0
        month_omisos = []
        for _, row in month_df.iterrows():
            package = evaluate_package(row, cutoff_date)
            if package["complete"]:
                numerator += 1
            else:
                month_omisos.append(omiso_from_row(row, package))

        denominator = len(month_df)
        coverage = round((numerator / denominator) * 100, 2) if denominator else 0.0
        monthly.append(
            {
                "month": month_name,
                "year": year,
                "in_verification_period": True,
                "compliant": denominator > 0 and coverage >= target,
                "semaphore": coverage_semaphore(coverage, target),
                "coverage": coverage,
                "denominator": denominator,
                "numerator": numerator,
            }
        )
        omisos.extend(month_omisos)

    months_met = sum(1 for item in monthly if item["compliant"])
    period_start = date(month_keys[0][0], month_keys[0][1], 1) if month_keys else date(2026, 1, 1)
    period_end = date(month_keys[-1][0], month_keys[-1][1], 28) if month_keys else date(2026, 12, 31)

    return {
        "period_start": period_start,
        "period_end": period_end,
        "cut_off_date": cutoff_date,
        "target_coverage": target,
        "months_evaluated": len(monthly),
        "months_met": months_met,
        "committed": bool(monthly) and months_met == len(monthly),
        "monthly": monthly,
        "omisos": omisos,
    }
