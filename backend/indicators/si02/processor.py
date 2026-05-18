"""SI-02 processing helpers."""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from .config import DEFAULT_PROVINCE, DEFAULT_TARGET_COVERAGE, EXPECTED_PACKAGE_CODES, SUBINDICATORS
from .commitment import build_commitment_summary, current_commitment_met
from .evaluator import evaluate_dataframe, evaluate_row
from .utils import clean_value, parse_month_key


ALL_PROVINCES_TOKEN = "__ALL__"


def filter_data(df: pd.DataFrame, subindicator_code: str, province: str | None = DEFAULT_PROVINCE) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    if not province or province == ALL_PROVINCES_TOKEN:
        return df

    province_column = SUBINDICATORS[subindicator_code].province_column
    if province_column not in df:
        return df.iloc[0:0]
    return df[df[province_column].astype(str).str.strip().str.upper() == province.strip().upper()]


def build_subindicator_summary(
    df: pd.DataFrame,
    subindicator_code: str,
    province: str | None = DEFAULT_PROVINCE,
    target_coverage: float | None = None,
) -> dict[str, Any]:
    spec = SUBINDICATORS[subindicator_code]
    filtered = filter_data(df, subindicator_code, province)
    evaluated = evaluate_dataframe(filtered, subindicator_code)
    target = spec.target_coverage if target_coverage is None else float(target_coverage)

    month_values = []
    if spec.month_column in filtered:
        for value in filtered[spec.month_column].dropna().unique().tolist():
            parsed = parse_month_key(value)
            if parsed:
                month_values.append(parsed)
    month_values = sorted(set(month_values), key=lambda item: (item[0], item[1]))

    monthly = []
    omisos = []
    for year, month, month_name in month_values:
        key = f"{year}_{month}"
        month_df = filtered[filtered[spec.month_column].astype(str).str.strip() == key]
        month_eval = evaluated.loc[month_df.index] if not evaluated.empty else pd.DataFrame()
        denominator = len(month_df)
        numerator = int(month_eval["cumple"].sum()) if not month_eval.empty else 0
        coverage = round((numerator / denominator) * 100, 2) if denominator else 0.0
        monthly.append(
            {
                "month": month_name,
                "year": year,
                "month_key": key,
                "coverage": coverage,
                "denominator": denominator,
                "numerator": numerator,
                "target_coverage": target,
                "compliant": denominator > 0 and coverage >= target,
                "semaphore": "green" if denominator > 0 and coverage >= target else "red",
            }
        )
        for row_index, evaluation in month_eval[~month_eval["cumple"]].iterrows():
            omisos.append(omiso_from_row(month_df.loc[row_index], subindicator_code, evaluation))

    return {
        "subindicator_code": subindicator_code,
        "subindicator_name": spec.title,
        "target_coverage": target,
        "province": province,
        "months_evaluated": len(monthly),
        "months_met": sum(1 for item in monthly if item["compliant"]),
        "monthly": monthly,
        "omisos": omisos,
    }


def build_package_summary(
    package_data: dict[str, pd.DataFrame],
    cutoff_date=None,
    province: str | None = DEFAULT_PROVINCE,
    target_coverage: float | None = None,
) -> dict[str, Any]:
    sub_summaries = {
        code: build_subindicator_summary(package_data[code], code, province)
        for code in EXPECTED_PACKAGE_CODES
        if code in package_data
    }
    subindicator_months_met = {code: summary["months_met"] for code, summary in sub_summaries.items()}
    monthly = aggregate_monthly(sub_summaries, target_coverage)
    omisos = [item for summary in sub_summaries.values() for item in summary["omisos"]]
    resolved_cutoff_date = latest_cutoff_date(cutoff_date)
    commitment_summary = build_commitment_summary(sub_summaries, resolved_cutoff_date)
    return {
        "indicator_code": "si02",
        "province": province,
        "period_start": period_boundary(monthly, first=True),
        "period_end": period_boundary(monthly, first=False),
        "cut_off_date": resolved_cutoff_date,
        "target_coverage": DEFAULT_TARGET_COVERAGE if target_coverage is None else float(target_coverage),
        "months_evaluated": len(monthly),
        "months_met": sum(1 for item in monthly if item["compliant"]),
        "committed": current_commitment_met(sub_summaries, resolved_cutoff_date),
        "monthly": monthly,
        "omisos": omisos,
        "subindicators": sub_summaries,
        "subindicator_months_met": subindicator_months_met,
        "package_complete": set(sub_summaries.keys()) == set(EXPECTED_PACKAGE_CODES),
        "commitment_summary": commitment_summary,
    }


def build_report_summary(data, cutoff_date=None, province: str | None = DEFAULT_PROVINCE, target_coverage: float | None = None) -> dict[str, Any]:
    return build_package_summary(data, cutoff_date, province, target_coverage)


def search_by_dni(package_data: dict[str, pd.DataFrame], dni: str, reference_date=None, province: str | None = DEFAULT_PROVINCE) -> dict[str, Any] | None:
    query = str(dni).strip()
    results = []
    personal = None
    flat_components = {}
    for code, df in package_data.items():
        filtered = filter_data(df, code, province)
        matches = filtered[
            (filtered.get("afi_dni", pd.Series(dtype=object)).astype(str).str.strip() == query)
            | (filtered.get("NUMCNV", pd.Series(dtype=object)).astype(str).str.strip() == query)
        ]
        for _, row in matches.iterrows():
            package = evaluate_row(row, code)
            if personal is None:
                personal = personal_from_row(row, code)
            results.append(
                {
                    "subindicator_code": code,
                    "subindicator_name": SUBINDICATORS[code].title,
                    "complete": package["complete"],
                    "details": package["details"],
                    "reasons": package["reasons"],
                }
            )
            for component_key, detail in package["details"].items():
                flat_components[f"{code}.{component_key}"] = normalize_component_detail(detail, code, component_key)

    if not results:
        return None
    return {
        "personal": personal,
        "vacunas": flat_components,
        "clinical_alerts": [],
        "cred_controls": [],
        "tamizaje": {},
        "paquete_completo": all(item["complete"] for item in results),
        "subindicators": results,
    }


def personal_from_row(row: pd.Series, subindicator_code: str) -> dict[str, Any]:
    spec = SUBINDICATORS[subindicator_code]
    return {
        "afi_DNI": clean_value(row.get("afi_dni")) or None,
        "NumCNV": clean_value(row.get("NUMCNV")) or None,
        "afi_nombres": clean_value(row.get("NOMBRE")) or None,
        "afi_appaterno": clean_value(row.get("APELLPAT")) or None,
        "afi_apmaterno": clean_value(row.get("APEMAT")) or None,
        "fec_Nac": clean_value(row.get("FEC_NAC")) or None,
        "peso": clean_value(row.get("Peso")) or None,
        "edadGEst": clean_value(row.get("SEMANAGESTACION")) or None,
        "Desc_prov": clean_value(row.get(spec.province_column)) or None,
        "Des_MicroRed": clean_value(row.get("des_micro")) or None,
        "pre_CodigoRENAES": clean_value(row.get("Renaes_ate")) or None,
        "Des_EESS": clean_value(row.get("EESS")) or None,
    }


def omiso_from_row(row: pd.Series, subindicator_code: str, evaluation: pd.Series) -> dict[str, Any]:
    spec = SUBINDICATORS[subindicator_code]
    parsed_month = parse_month_key(row.get(spec.month_column))
    year, month_name = (parsed_month[0], parsed_month[2]) if parsed_month else (None, None)
    return {
        "Mes_eva": clean_value(row.get(spec.month_column)) or None,
        "month": month_name,
        "year": year,
        "afi_DNI": clean_value(row.get("afi_dni")) or None,
        "NumCNV": clean_value(row.get("NUMCNV")) or None,
        "fec_Nac": clean_value(row.get("FEC_NAC")) or None,
        "afi_nombres": clean_value(row.get("NOMBRE")) or None,
        "afi_appaterno": clean_value(row.get("APELLPAT")) or None,
        "afi_apmaterno": clean_value(row.get("APEMAT")) or None,
        "Desc_prov": clean_value(row.get(spec.province_column)) or None,
        "Des_MicroRed": clean_value(row.get("des_micro")) or None,
        "pre_CodigoRENAES": clean_value(row.get("Renaes_ate")) or None,
        "Des_EESS": clean_value(row.get("EESS")) or None,
        "subindicator_code": subindicator_code,
        "subindicator_name": spec.title,
        "component": None,
        "components_observed": clean_value(evaluation.get("componentes_observados")) or None,
        "reason": clean_value(evaluation.get("motivos")) or "No cumple SI-02.",
    }


def get_filter_options(package_data: dict[str, pd.DataFrame]) -> dict[str, Any]:
    provinces = set()
    for code, df in package_data.items():
        province_column = SUBINDICATORS[code].province_column
        if province_column in df:
            provinces.update(value for value in df[province_column].dropna().astype(str).str.strip().tolist() if value)
    return {
        "provinces": sorted(provinces),
        "default_province": DEFAULT_PROVINCE,
        "default_target_coverage": DEFAULT_TARGET_COVERAGE,
        "included_insurance_types": ["SIS", "Sin seguro"],
        "exclusion_criteria": {"package": "SI-02 requiere los cuatro archivos semanales completos."},
    }


def normalize_component_detail(detail: dict[str, Any], subindicator_code: str, component_key: str) -> dict[str, Any]:
    item = dict(detail)
    item["codigo"] = item.get("codigo") or ""
    item["component_key"] = component_key
    item["subindicator_code"] = subindicator_code
    item["subindicator_name"] = SUBINDICATORS[subindicator_code].title
    item.setdefault("dosis", [])
    item.setdefault("entregas", [])
    return item


def aggregate_monthly(sub_summaries: dict[str, dict[str, Any]], target_coverage: float | None) -> list[dict[str, Any]]:
    target = DEFAULT_TARGET_COVERAGE if target_coverage is None else float(target_coverage)
    by_key: dict[tuple[int, str], dict[str, Any]] = {}
    for summary in sub_summaries.values():
        for item in summary["monthly"]:
            key = (item["year"], item["month"])
            aggregate = by_key.setdefault(key, {"month": item["month"], "year": item["year"], "denominator": 0, "numerator": 0})
            aggregate["denominator"] += item["denominator"]
            aggregate["numerator"] += item["numerator"]

    monthly = []
    for item in sorted(by_key.values(), key=lambda value: (value["year"], month_number(value["month"]))):
        denominator = item["denominator"]
        numerator = item["numerator"]
        coverage = round((numerator / denominator) * 100, 2) if denominator else 0.0
        compliant = denominator > 0 and coverage >= target
        monthly.append(
            {
                "month": item["month"],
                "year": item["year"],
                "month_key": f'{item["year"]}_{month_number(item["month"])}',
                "in_verification_period": True,
                "compliant": compliant,
                "semaphore": "green" if compliant else "red",
                "coverage": coverage,
                "denominator": denominator,
                "numerator": numerator,
            }
        )
    return monthly


def month_number(label: str | None) -> int:
    for number in range(1, 13):
        parsed = parse_month_key(f"2026_{number}")
        if parsed and parsed[2] == label:
            return number
    return 0


def period_boundary(monthly: list[dict[str, Any]], *, first: bool):
    from datetime import date

    pairs = [(item["year"], month_number(item["month"])) for item in monthly if item.get("year") and month_number(item.get("month"))]
    if not pairs:
        return date(2026, 1, 1) if first else date(2026, 12, 31)
    year, month = min(pairs) if first else max(pairs)
    return date(year, month, 1 if first else 28)


def latest_cutoff_date(value):
    if isinstance(value, dict):
        values = [item for item in value.values() if item is not None]
        return max(values) if values else None
    return value
