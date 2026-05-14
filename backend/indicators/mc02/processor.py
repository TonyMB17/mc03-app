from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from ...core.dates import clean_text
    from ...core.excel import build_validation_error, open_workbook, read_sheet
except ImportError:
    from core.dates import clean_text
    from core.excel import build_validation_error, open_workbook, read_sheet

from .config import CODE, NAME, COLUMNAS_EXCEL, CUTOFF_CELL, DEFAULT_PROVINCE, DEFAULT_TARGET_COVERAGE, EXCEL_SHEET, HEADER_ROW, REGLAS_NEGOCIO, RESUMEN
from .rules import (
    ACTIVE_COMPONENT_FLAGS,
    DENOMINATOR_COLUMN,
    EXCLUSION_CRITERIA,
    INCLUDED_DENOMINATOR_VALUE,
    INCLUDED_INSURANCE_TYPES,
    INSURANCE_COLUMN,
    MONTH_COLUMN,
    NUMERATOR_COLUMN,
    OMITTED_CURRENT_CRITERIA,
    PROVINCE_COLUMN,
)

ALL_PROVINCES_TOKEN = "__ALL__"

COMPONENTS = [
    {
        "key": "neumococo",
        "label": "Vacuna neumococo",
        "obs": "Obs_NEU",
        "flag": "obs_neu1",
        "date": "fecha_NEU",
        "age": "edad_NEU",
        "code": "CIE_NEU",
        "lab": "Lab_NEU",
        "lote": "Lote_Pag_Reg_NEU",
        "facility": "EESS_Ate_NEU",
        "window": "NEUMOCOCO",
        "doses": [
            {"label": "1 dosis", "date": "fecha_NEU", "age": "edad_NEU", "code": "CIE_NEU", "lab": "Lab_NEU", "lote": "Lote_Pag_Reg_NEU", "facility": "EESS_Ate_NEU"},
            {"label": "2 dosis", "date": "fecha_2NEU", "age": "edad_2NEU", "code": "CIE_NEU_2NEU", "lab": "Lab_2NEU", "lote": "Lote_Pag_Reg_2NEU", "facility": "EESS_Ate_2NEU"},
        ],
    },
    {
        "key": "rotavirus",
        "label": "Vacuna rotavirus",
        "obs": "Obs_ROT",
        "flag": "obs_rot1",
        "date": "fecha_1Rot",
        "age": "edad_1Rot",
        "code": "CIE_NEU_1Rot",
        "lab": "Lab_1Rot",
        "lote": "Lote_Pag_Reg_1Rot",
        "facility": "EESS_Ate_1Rot",
        "window": "ROTAVIRUS",
        "doses": [
            {"label": "1 dosis", "date": "fecha_1Rot", "age": "edad_1Rot", "code": "CIE_NEU_1Rot", "lab": "Lab_1Rot", "lote": "Lote_Pag_Reg_1Rot", "facility": "EESS_Ate_1Rot"},
            {"label": "2 dosis", "date": "fecha_2Rot", "age": "edad_2Rot", "code": "CIE_NEU_2Rot", "lab": "Lab_2Rot", "lote": "Lote_Pag_Reg_2Rot", "facility": "EESS_Ate_2Rot"},
        ],
    },
    {
        "key": "antipolio",
        "label": "Vacuna antipolio",
        "obs": "Obs_ANT",
        "flag": "obs_ant1",
        "date": "fecha_1ANT",
        "age": "edad_1ANT",
        "code": "CIE_ANT_1ANT",
        "lab": "Lab_1ANT",
        "lote": "Lote_Pag_Reg_1ANT",
        "facility": "EESS_Ate_1ANT",
        "window": "ANTIPOLIO",
        "doses": [
            {"label": "1 dosis", "date": "fecha_1ANT", "age": "edad_1ANT", "code": "CIE_ANT_1ANT", "lab": "Lab_1ANT", "lote": "Lote_Pag_Reg_1ANT", "facility": "EESS_Ate_1ANT"},
            {"label": "2 dosis", "date": "fecha_2ANT", "age": "edad_2ANT", "code": "CIE_ANT_2ANT", "lab": "Lab_2ANT", "lote": "Lote_Pag_Reg_2ANT", "facility": "EESS_Ate_2ANT"},
            {"label": "3 dosis", "date": "fecha_3ANT", "age": "edad_3ANT", "code": "CIE_ANT_3ANT", "lab": "Lab_3ANT", "lote": "Lote_Pag_Reg_3ANT", "facility": "EESS_Ate_3ANT"},
        ],
    },
    {
        "key": "pentavalente",
        "label": "Vacuna pentavalente",
        "obs": "Obs_PEN",
        "flag": "obs_pen1",
        "date": "fecha_1PENT",
        "age": "edad_1PENT",
        "code": "CIE_PEN_1PENT",
        "lab": "Lab_1PENT",
        "lote": "Lote_Pag_Reg_1PENT",
        "facility": "EESS_Ate_1PENT",
        "window": "PENTAVALENTE",
        "doses": [
            {"label": "1 dosis", "date": "fecha_1PENT", "age": "edad_1PENT", "code": "CIE_PEN_1PENT", "lab": "Lab_1PENT", "lote": "Lote_Pag_Reg_1PENT", "facility": "EESS_Ate_1PENT"},
            {"label": "2 dosis", "date": "fecha_2PENT", "age": "edad_2PENT", "code": "CIE_PEN_2PENT", "lab": "Lab_2PENT", "lote": "Lote_Pag_Reg_2PENT", "facility": "EESS_Ate_2PENT"},
            {"label": "3 dosis", "date": "fecha_3PENT", "age": "edad_3PENT", "code": "CIE_PEN_3PENT", "lab": "Lab_3PENT", "lote": "Lote_Pag_Reg_3PENT", "facility": "EESS_Ate_3PENT"},
        ],
    },
    {
        "key": "hierro_menor_6m",
        "label": "Hierro menor de 6 meses",
        "obs": "Obs_Hierros",
        "flag": "obs_suple41",
        "date": "fecha_1prev",
        "age": "edad_1prev",
        "code": "CIE_Hierro_1prev",
        "lab": "Lab_1prev",
        "lote": "Lote_Pag_Reg_1prev",
        "facility": "EESS_Ate_1prev",
        "window": "HIERRO_MENOR_6_MESES",
    },
    {
        "key": "hierro_mayor_6m",
        "label": "Hierro mayor de 6 meses",
        "obs": "OBS_SUPLE6",
        "flag": "obs_suple61",
        "date": "fecha_1prevhierr",
        "age": "edad_1prevhierr",
        "code": "CIE_Hierro_1prevhierr",
        "lab": "Lab_1prevhierr",
        "lote": "Lote_Pag_Reg_1prevhierr",
        "facility": "EESS_Ate_1prevhierr",
        "window": "HIERRO_MAYOR_6_MESES",
    },
    {
        "key": "hemoglobina",
        "label": "Dosaje de hemoglobina",
        "obs": "Obs_Dh",
        "flag": "Obs_dh1",
        "date": "fecha_1DH",
        "age": "edad_1DH",
        "code": "CIE_DH_1DH",
        "lab": "Lab_1DH",
        "lote": "Lote_Pag_Reg_1DH",
        "facility": "EESS_Ate_1DH",
        "window": "DOSAJE_HEMOGLOBINA",
    },
]

BASE_REQUIRED_GROUPS = ("UBICACION", "DATOS_GENERALES", "FUENTE_CNV")
OMITTED_GROUP_PREFIXES = ("CRED_RECIEN_NACIDO", "CRED_MAYOR")
OMITTED_SUMMARY_COLUMNS = {"obs_credRN1", "Obs_CRED1mas", "Cred_cumple"}


def _configured_columns(*groups: str) -> list[str]:
    columns: list[str] = []
    for group in groups:
        columns.extend(COLUMNAS_EXCEL.get(group, []))
    return columns


def _component_columns() -> list[str]:
    columns: list[str] = []
    for component in COMPONENTS:
        columns.extend([component["flag"], component["date"], component["age"], component["code"]])
        if component.get("obs"):
            columns.append(component["obs"])
        for dose in component.get("doses", []):
            columns.extend([dose.get("date"), dose.get("age"), dose.get("code")])
    return columns


def _required_columns() -> list[str]:
    summary_columns = [column for column in RESUMEN.keys() if column not in OMITTED_SUMMARY_COLUMNS]
    columns = [
        *_configured_columns(*BASE_REQUIRED_GROUPS),
        *summary_columns,
        *_component_columns(),
    ]
    return sorted({column for column in columns if column})

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


def load_sample_data(filepath: Path) -> dict[str, Any] | None:
    if not filepath.exists():
        return None

    workbook = open_workbook(filepath)
    if EXCEL_SHEET not in workbook.sheetnames:
        raise ValueError("La hoja 'Detalle_Ate' no se encuentra en el archivo de datos")

    cutoff_date = workbook[EXCEL_SHEET][CUTOFF_CELL].value
    df = read_sheet(filepath, EXCEL_SHEET, HEADER_ROW)
    return {"data": df, "cutoff_date": _to_date(cutoff_date)}


def validate_data_file(filepath: Path) -> dict[str, Any]:
    if not filepath.exists():
        return build_validation_error("No se encontro el archivo cargado.")

    errors: list[str] = []
    warnings: list[str] = []
    required_columns = _required_columns()
    summary: dict[str, Any] = {
        "indicator_code": CODE,
        "indicator_name": NAME,
        "filename": filepath.name,
        "file_size_bytes": filepath.stat().st_size,
        "sheet_name": EXCEL_SHEET,
        "cutoff_cell": CUTOFF_CELL,
        "header_row": HEADER_ROW,
        "validation_label": "Estado operativo",
        "required_columns_count": len(required_columns),
    }

    try:
        workbook = open_workbook(filepath)
    except Exception as exc:
        return build_validation_error(f"No se pudo abrir el Excel: {exc}", summary)

    if EXCEL_SHEET not in workbook.sheetnames:
        errors.append("No se encontro la hoja obligatoria 'Detalle_Ate'.")
        return {"valid": False, "errors": errors, "warnings": warnings, "summary": summary}

    cutoff_date = _to_date(workbook[EXCEL_SHEET][CUTOFF_CELL].value)
    if cutoff_date is None:
        warnings.append("No se pudo leer una fecha de corte valida desde la celda D9.")
    summary["cutoff_date"] = cutoff_date

    try:
        df = read_sheet(filepath, EXCEL_SHEET, HEADER_ROW)
    except Exception as exc:
        return {"valid": False, "errors": [f"No se pudo leer la hoja 'Detalle_Ate': {exc}"], "warnings": warnings, "summary": summary}

    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        errors.append("Faltan columnas obligatorias: " + ", ".join(missing_columns))

    summary["total_rows"] = len(df)
    summary["total_columns"] = len(df.columns)
    summary["columns_found"] = list(df.columns)
    summary["missing_columns"] = missing_columns
    summary["omitted_columns"] = _omitted_columns_present(df)
    summary["provinces"] = _unique_text_values(df, PROVINCE_COLUMN)
    summary["months"] = _unique_text_values(df, MONTH_COLUMN)
    status_counts = _value_counts(df, NUMERATOR_COLUMN)
    summary["status_counts"] = status_counts
    summary["obs_eval_counts"] = status_counts
    summary["insurance_counts"] = df[INSURANCE_COLUMN].fillna("VACIO").astype(str).str.strip().value_counts().to_dict() if INSURANCE_COLUMN in df else {}
    summary["denominator_counts"] = _denominator_counts(df)
    summary["component_counts"] = _component_counts(df)

    if len(df) == 0:
        errors.append("La hoja 'Detalle_Ate' no contiene registros.")
    if DENOMINATOR_COLUMN in df and not (pd.to_numeric(df[DENOMINATOR_COLUMN], errors="coerce") == 1).any():
        warnings.append("No se encontraron registros con Registros = 1.")

    return {"valid": not errors, "errors": errors, "warnings": warnings, "summary": summary}


def _unique_text_values(df: pd.DataFrame, column: str) -> list[str]:
    if column not in df:
        return []
    return sorted(value for value in df[column].dropna().astype(str).str.strip().unique().tolist() if value)


def _value_counts(df: pd.DataFrame, column: str) -> dict[str, int]:
    if column not in df:
        return {}
    counts = df[column].fillna("VACIO").astype(str).str.strip().replace("", "VACIO").value_counts().to_dict()
    return {str(key): int(value) for key, value in counts.items()}


def _component_counts(df: pd.DataFrame) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for component in COMPONENTS:
        flag_column = component["flag"]
        if flag_column not in df:
            continue
        normalized = df[flag_column].apply(lambda value: "Cumple" if _flag_is_true(value) else ("Sin dato" if not _has_value(value) else "No cumple"))
        counts[component["label"]] = {str(key): int(value) for key, value in normalized.value_counts().to_dict().items()}
    return counts


def _denominator_counts(df: pd.DataFrame) -> dict[str, int]:
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
    insurance_included = base_mask & df.apply(lambda row: _insurance_included(row), axis=1)

    return {
        "registros_base": int(base_mask.sum()),
        "seguros_incluidos": int(insurance_included.sum()),
        "excluidos_tipo_seguro": int((base_mask & ~insurance_included).sum()),
        "excluidos_bajo_peso": int(low_weight.sum()),
        "excluidos_prematuridad": int(premature.sum()),
        "con_peso_o_eg_vacio_incluidos": int((unknown_exclusion_data & insurance_included & ~excluded).sum()),
        "denominador_final": int((base_mask & insurance_included & ~excluded).sum()),
    }


def _omitted_columns_present(df: pd.DataFrame) -> list[str]:
    omitted: list[str] = []
    for group, columns in COLUMNAS_EXCEL.items():
        if group.startswith(OMITTED_GROUP_PREFIXES):
            omitted.extend(column for column in columns if column in df.columns)
    omitted.extend(column for column in OMITTED_SUMMARY_COLUMNS if column in df.columns)
    return sorted(set(omitted))


def _clean_text(value: Any) -> str:
    return clean_text(value)


def _to_date(value: Any) -> date | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    parsed = pd.to_datetime(value, errors="coerce")
    return parsed.date() if not pd.isna(parsed) else None


def _to_number(value: Any) -> float | None:
    parsed = pd.to_numeric(value, errors="coerce")
    return None if pd.isna(parsed) else float(parsed)


def _to_int(value: Any) -> int | None:
    number = _to_number(value)
    return None if number is None else int(number)


def _has_value(value: Any) -> bool:
    return bool(_clean_text(value))


def _flag_is_true(value: Any) -> bool:
    if value is None or pd.isna(value):
        return False
    if isinstance(value, str):
        clean = value.strip().lower()
        return clean in {"1", "cumple", "si", "true", "evaluado"}
    return _to_number(value) == 1


def _normalize_target(value: float | None) -> float:
    return DEFAULT_TARGET_COVERAGE if value is None else float(value)


def _coverage_semaphore(coverage: float, target: float) -> str:
    return "green" if coverage >= target else "red"


def _parse_month_key(value: Any) -> tuple[int, int, str] | None:
    text = _clean_text(value)
    if not text or "_" not in text:
        return None
    year_text, month_text = text.split("_", 1)
    try:
        year = int(float(year_text))
        month = int(float(month_text))
    except ValueError:
        return None
    return year, month, MONTH_LABELS.get(month, text)


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
        "provinces": _unique_text_values(df, PROVINCE_COLUMN),
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


def _is_in_denominator(row: pd.Series) -> bool:
    return (
        _to_number(row.get(DENOMINATOR_COLUMN)) == INCLUDED_DENOMINATOR_VALUE
        and _insurance_included(row)
        and not _has_exclusion(row)
    )


def _insurance_included(row: pd.Series) -> bool:
    insurance = _clean_text(row.get(INSURANCE_COLUMN)).upper()
    return insurance in INCLUDED_INSURANCE_TYPES


def _has_exclusion(row: pd.Series) -> bool:
    weight = _to_number(row.get(EXCLUSION_CRITERIA["COLUMNA_PESO"]))
    gestational_age = _to_number(row.get(EXCLUSION_CRITERIA["COLUMNA_GESTACION"]))

    low_weight = weight is not None and weight < EXCLUSION_CRITERIA["PESO_MIN"]
    premature = gestational_age is not None and gestational_age < EXCLUSION_CRITERIA["GESTACION_MIN"]
    return low_weight or premature


def _birth_date(row: pd.Series) -> date | None:
    return _to_date(row.get("Fec_Nac"))


def _date_from_birth(row: pd.Series, age_days: int | None) -> date | None:
    birth_date = _birth_date(row)
    if birth_date is None or age_days is None:
        return None
    return birth_date + timedelta(days=age_days)


def _format_short_date(value: date | None) -> str:
    if value is None:
        return ""
    return f"{value.day:02d} {MONTH_ABBR[value.month]} {value.year}"


def _current_age_days(row: pd.Series, reference_date: date | None = None) -> int | None:
    birth_date = _birth_date(row)
    if birth_date is not None and reference_date is not None:
        return max((reference_date - birth_date).days, 0)
    return _to_int(row.get("Edad_Act(dia)"))


def _is_compliant(row: pd.Series, reference_date: date | None = None) -> bool:
    return all(_component_complies(row, component, reference_date) for component in COMPONENTS)


def _matched_window_range(row: pd.Series, component: dict[str, str], reference_date: date | None = None) -> dict[str, Any] | None:
    rule = REGLAS_NEGOCIO["VENTANAS_ATENCION"].get(component["window"])
    current_age = _current_age_days(row, reference_date)
    if not rule or current_age is None:
        return None
    for item in rule.get("rangos", []):
        if item["edad_min"] <= current_age <= item["edad_max"]:
            return item
    return None


def _required_amount(window_range: dict[str, Any] | None) -> int:
    if window_range is None:
        return 1
    required = window_range.get("dosis_requeridas", window_range.get("entregas_requeridas", 1))
    return int(required) > 0


def _component_required(row: pd.Series, component: dict[str, str], reference_date: date | None = None) -> bool:
    return bool(_required_amount(_matched_window_range(row, component, reference_date)))


def _component_complies(row: pd.Series, component: dict[str, str], reference_date: date | None = None) -> bool:
    if not _component_required(row, component, reference_date):
        return True
    return _flag_is_true(row.get(component["flag"]))


def _next_required_range(row: pd.Series, component: dict[str, str], reference_date: date | None = None) -> dict[str, Any] | None:
    rule = REGLAS_NEGOCIO["VENTANAS_ATENCION"].get(component["window"])
    current_age = _current_age_days(row, reference_date)
    if not rule:
        return None

    required_ranges = [item for item in rule.get("rangos", []) if _required_amount(item)]
    if current_age is None:
        return required_ranges[0] if required_ranges else None

    for item in required_ranges:
        if current_age <= item["edad_max"]:
            return item
    return required_ranges[-1] if required_ranges else None


def _active_or_next_range(row: pd.Series, component: dict[str, str], reference_date: date | None = None) -> dict[str, Any] | None:
    matched_range = _matched_window_range(row, component, reference_date)
    if matched_range is not None:
        return matched_range
    return _next_required_range(row, component, reference_date)


def _window_text(row: pd.Series, component: dict[str, str], reference_date: date | None = None) -> str | None:
    rule = REGLAS_NEGOCIO["VENTANAS_ATENCION"].get(component["window"])
    if not rule:
        return None

    current_age = _current_age_days(row, reference_date)
    matched_range = _matched_window_range(row, component, reference_date)
    evaluation_range = _active_or_next_range(row, component, reference_date)
    if matched_range is not None and not _required_amount(matched_range):
        evaluation_range = _next_required_range(row, component, reference_date)

    pieces = []
    if matched_range:
        pieces.append(
            f"Edad actual {current_age} dias: {matched_range['mensaje']}"
        )
    elif current_age is not None:
        pieces.append(f"Edad actual {current_age} dias fuera de rangos configurados.")

    if evaluation_range:
        start_date = _date_from_birth(row, evaluation_range.get("edad_min"))
        limit_date = _date_from_birth(row, evaluation_range.get("edad_max"))
        if start_date and limit_date:
            pieces.append(f"Periodo de seguimiento: {_format_short_date(start_date)} a {_format_short_date(limit_date)}.")

    if "ventana_atencion" in rule:
        window = rule["ventana_atencion"]
        pieces.append(f"Ventana de atencion: {window['inicio_dia']} a {window['fin_dia']} dias.")
    if "intervalo_dosis" in rule:
        interval = rule["intervalo_dosis"]
        if "max_dias" in interval:
            pieces.append(f"Intervalo entre dosis: {interval['min_dias']} a {interval['max_dias']} dias.")
        elif "max_edad_dias" in interval:
            pieces.append(f"Intervalo minimo {interval['min_dias']} dias; edad maxima {interval['max_edad_dias']} dias.")
    if "intervalo_hierro" in rule:
        interval = rule["intervalo_hierro"]
        pieces.append(f"Intervalo hierro: {interval['min_dias']} a {interval['max_dias']} dias.")
    if "intervalo_micronutrientes" in rule:
        interval = rule["intervalo_micronutrientes"]
        pieces.append(f"Intervalo micronutrientes: {interval['min_dias']} a {interval['max_dias']} dias.")

    return " ".join(pieces) or rule.get("descripcion")


def _dose_details(row: pd.Series, component: dict[str, Any]) -> list[dict[str, Any]]:
    doses: list[dict[str, Any]] = []
    for dose in component.get("doses", []):
        has_date = _has_value(row.get(dose["date"]))
        has_code = _has_value(row.get(dose["code"]))
        if not has_date and not has_code:
            continue
        doses.append(
            {
                "label": dose["label"],
                "fecha": _clean_text(row.get(dose["date"])) or None,
                "edad_atencion_dias": _to_int(row.get(dose["age"])),
                "codigo": _clean_text(row.get(dose["code"])) or None,
                "lab": _clean_text(row.get(dose.get("lab"))) or None,
                "lote": _clean_text(row.get(dose.get("lote"))) or None,
                "establecimiento_atencion": _clean_text(row.get(dose.get("facility"))) or None,
            }
        )
    return doses


def _component_detail(row: pd.Series, component: dict[str, str], reference_date: date | None = None) -> dict[str, Any]:
    current_age = _current_age_days(row, reference_date)
    matched_range = _matched_window_range(row, component, reference_date)
    evaluation_range = _active_or_next_range(row, component, reference_date)
    required = _component_required(row, component, reference_date)
    complies = _component_complies(row, component, reference_date)
    if not required:
        evaluation_range = _next_required_range(row, component, reference_date)
    obs_text = _clean_text(row.get(component["obs"]))
    has_attention = _has_value(row.get(component["date"]))
    window_message = _window_text(row, component, reference_date)
    age = _to_int(row.get(component["age"]))
    fecha_inicio = _date_from_birth(row, evaluation_range.get("edad_min")) if evaluation_range else None
    fecha_limite = _date_from_birth(row, evaluation_range.get("edad_max")) if evaluation_range else None
    after_deadline = bool(evaluation_range and current_age is not None and current_age > int(evaluation_range.get("edad_max", current_age)))

    if not required:
        estado = "programado"
        mensaje = f"{component['label']} aun no es exigible para la edad actual."
        next_range = _next_required_range(row, component, reference_date)
        if next_range and current_age is not None and current_age < int(next_range["edad_min"]):
            next_start = _date_from_birth(row, next_range["edad_min"])
            if next_start:
                mensaje = f"{mensaje} Proximo control desde {_format_short_date(next_start)}."
        if window_message:
            mensaje = f"{mensaje} {window_message}"
    elif complies:
        estado = "cumple"
        mensaje = f"{component['label']} cumple segun la evaluacion del Excel operativo."
    elif has_attention:
        estado = "incumplimiento_fuera_plazo" if after_deadline else "pendiente_en_plazo"
        mensaje = obs_text or f"{component['label']} registra atencion, pero no cumple el criterio del indicador."
        if after_deadline and fecha_limite:
            mensaje = f"Incumplimiento por atencion fuera de plazo. Fecha limite: {_format_short_date(fecha_limite)}. {mensaje}"
        elif fecha_limite:
            mensaje = f"Pendiente dentro de plazo. Fecha limite: {_format_short_date(fecha_limite)}. {mensaje}"
        if window_message:
            mensaje = f"{mensaje} {window_message}"
    else:
        estado = "incumplimiento_fuera_plazo" if after_deadline else "pendiente_en_plazo"
        if after_deadline and fecha_limite:
            mensaje = f"No se registra atencion para {component['label']}. Incumplimiento fuera de plazo; fecha limite: {_format_short_date(fecha_limite)}."
        elif fecha_limite:
            mensaje = f"No se registra atencion para {component['label']}. Pendiente dentro de plazo; fecha limite: {_format_short_date(fecha_limite)}."
        else:
            mensaje = obs_text or f"No se registra atencion para {component['label']}."
        if window_message:
            mensaje = f"{mensaje} {window_message}"

    return {
        "codigo": _clean_text(row.get(component["code"])) or component["label"],
        "fecha": _clean_text(row.get(component["date"])) or None,
        "resultado": obs_text or None,
        "edad_atencion_dias": age,
        "cumple": complies,
        "estado": estado,
        "mensaje": mensaje,
        "establecimiento_atencion": _clean_text(row.get(component["facility"])) or None,
        "profesional": _clean_text(row.get(component.get("professional"))) or "No disponible en Excel",
        "lab": _clean_text(row.get(component["lab"])) or None,
        "lote": _clean_text(row.get(component["lote"])) or None,
        "ventana_normativa": window_message,
        "fecha_inicio": fecha_inicio,
        "fecha_limite": fecha_limite,
        "dosis": _dose_details(row, component),
    }


def evaluate_package(row: pd.Series, reference_date: date | None = None) -> dict[str, Any]:
    details = {component["key"]: _component_detail(row, component, reference_date) for component in COMPONENTS}
    reasons = [detail["mensaje"] for detail in details.values() if not detail["cumple"]]
    return {"complete": _is_compliant(row, reference_date), "details": details, "reasons": reasons}


def _first_failed_detail(package: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    for key, detail in package["details"].items():
        if not detail["cumple"]:
            return key, detail
    return None, None


def _omiso_from_row(row: pd.Series, package: dict[str, Any]) -> dict[str, Any]:
    parsed_month = _parse_month_key(row.get(MONTH_COLUMN))
    year, month_name = (parsed_month[0], parsed_month[2]) if parsed_month else (None, None)
    component_key, failed_detail = _first_failed_detail(package)
    reasons = package["reasons"]
    return {
        "Mes_eva": _clean_text(row.get(MONTH_COLUMN)) or None,
        "month": month_name,
        "year": year,
        "afi_DNI": _clean_text(row.get("DNI o CNV")) or None,
        "NumCNV": _clean_text(row.get("NumCNV")) or None,
        "fec_Nac": _clean_text(row.get("Fec_Nac")) or None,
        "afi_nombres": _clean_text(row.get("Nombres")) or None,
        "afi_appaterno": _clean_text(row.get("Ape_Paterno")) or None,
        "afi_apmaterno": _clean_text(row.get("Ape_Materno")) or None,
        "Desc_prov": _clean_text(row.get(PROVINCE_COLUMN)) or None,
        "Des_MicroRed": _clean_text(row.get("MicroRed")) or None,
        "pre_CodigoRENAES": _clean_text(row.get("Renaes")) or None,
        "Des_EESS": _clean_text(row.get("EESS")) or None,
        "component": component_key,
        "attention_date": failed_detail.get("fecha") if failed_detail else None,
        "attention_age_days": failed_detail.get("edad_atencion_dias") if failed_detail else None,
        "attention_facility": failed_detail.get("establecimiento_atencion") if failed_detail else None,
        "attention_professional": failed_detail.get("profesional") if failed_detail else None,
        "reason": "; ".join(reasons) or _clean_text(row.get("Obs_General")) or "No cumple paquete integrado.",
    }


def build_report_summary(
    df: pd.DataFrame,
    cutoff_date: date | None = None,
    province: str | None = DEFAULT_PROVINCE,
    target_coverage: float | None = None,
) -> dict[str, Any]:
    df = filter_data(df, province)
    target = _normalize_target(target_coverage)
    denominator_df = df[df.apply(_is_in_denominator, axis=1)]

    month_keys = []
    for value in denominator_df.get(MONTH_COLUMN, pd.Series(dtype=object)).dropna().unique().tolist():
        parsed = _parse_month_key(value)
        if parsed:
            month_keys.append(parsed)
    month_keys = sorted(set(month_keys), key=lambda item: (item[0], item[1]))

    monthly = []
    omisos = []
    for year, month, month_name in month_keys:
        key = f"{year}_{month}"
        month_df = denominator_df[denominator_df[MONTH_COLUMN].astype(str).str.strip() == key]
        numerator = int(month_df.apply(lambda row: _is_compliant(row, cutoff_date), axis=1).sum())
        denominator = len(month_df)
        coverage = round((numerator / denominator) * 100, 2) if denominator else 0.0
        monthly.append(
            {
                "month": month_name,
                "year": year,
                "in_verification_period": True,
                "compliant": denominator > 0 and coverage >= target,
                "semaphore": _coverage_semaphore(coverage, target),
                "coverage": coverage,
                "denominator": denominator,
                "numerator": numerator,
            }
        )

        for _, row in month_df.iterrows():
            if not _is_compliant(row, cutoff_date):
                package = evaluate_package(row, cutoff_date)
                omisos.append(_omiso_from_row(row, package))

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


def search_by_dni(
    df: pd.DataFrame,
    dni: str,
    reference_date: date | None = None,
    province: str | None = DEFAULT_PROVINCE,
) -> dict[str, Any] | None:
    if df is None or df.empty:
        return None

    df = filter_data(df, province)
    search_value = dni.strip()
    mask = (
        df["DNI o CNV"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip().eq(search_value)
        | df["NumCNV"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip().eq(search_value)
    )
    result = df[mask]
    if result.empty:
        return None

    row = result.iloc[0]
    package = evaluate_package(row, reference_date)

    personal = {
        "afi_DNI": _clean_text(row.get("DNI o CNV")) or None,
        "NumCNV": _clean_text(row.get("NumCNV")) or None,
        "afi_nombres": _clean_text(row.get("Nombres")) or None,
        "afi_appaterno": _clean_text(row.get("Ape_Paterno")) or None,
        "afi_apmaterno": _clean_text(row.get("Ape_Materno")) or None,
        "fec_Nac": _clean_text(row.get("Fec_Nac")) or None,
        "peso": _to_number(row.get("Peso")),
        "edadGEst": _to_int(row.get("Edad_Gestacional")),
        "Desc_prov": _clean_text(row.get(PROVINCE_COLUMN)) or None,
        "Des_MicroRed": _clean_text(row.get("MicroRed")) or None,
        "pre_CodigoRENAES": _clean_text(row.get("Renaes")) or None,
        "Des_EESS": _clean_text(row.get("EESS")) or None,
    }

    return {
        "personal": personal,
        "vacunas": package["details"],
        "cred_controls": [],
        "tamizaje": {
            "fecha": _clean_text(row.get("fecha_1DH")) or None,
            "edad_atencion_dias": _to_int(row.get("edad_1DH")),
            "cumple": _flag_is_true(row.get("Obs_dh1")),
            "estado": package["details"]["hemoglobina"]["estado"],
            "mensaje": package["details"]["hemoglobina"]["mensaje"],
            "fecha_inicio": package["details"]["hemoglobina"]["fecha_inicio"],
            "fecha_limite": package["details"]["hemoglobina"]["fecha_limite"],
        },
        "paquete_completo": package["complete"],
    }
