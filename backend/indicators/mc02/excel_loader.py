"""Excel loading and validation for MC-02 operative files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

try:
    from ...core.excel import build_validation_error, open_workbook, read_sheet
except ImportError:
    from core.excel import build_validation_error, open_workbook, read_sheet

from .config import CODE, NAME, COLUMNAS_EXCEL, CUTOFF_CELL, EXCEL_SHEET, HEADER_ROW, RESUMEN
from .denominator import denominator_counts
from .evaluator import COMPONENTS
from .rules import DENOMINATOR_COLUMN, INSURANCE_COLUMN, MONTH_COLUMN, NUMERATOR_COLUMN, PROVINCE_COLUMN
from .utils import flag_is_true, has_value, to_date


BASE_REQUIRED_GROUPS = ("UBICACION", "DATOS_GENERALES", "FUENTE_CNV", "Dx_ANEMIA")
OMITTED_GROUP_PREFIXES = ("CRED_RECIEN_NACIDO", "CRED_MAYOR")
OMITTED_SUMMARY_COLUMNS = {"obs_credRN1", "Obs_CRED1mas", "Cred_cumple"}


def configured_columns(*groups: str) -> list[str]:
    columns: list[str] = []
    for group in groups:
        columns.extend(COLUMNAS_EXCEL.get(group, []))
    return columns


def component_columns() -> list[str]:
    columns: list[str] = []
    for component in COMPONENTS:
        columns.extend([component["flag"], component["date"], component["age"], component["code"]])
        if component.get("obs"):
            columns.append(component["obs"])
        for dose in component.get("doses", []):
            columns.extend([dose.get("date"), dose.get("age"), dose.get("code")])
    return columns


def required_columns() -> list[str]:
    summary_columns = [column for column in RESUMEN.keys() if column not in OMITTED_SUMMARY_COLUMNS]
    columns = [
        *configured_columns(*BASE_REQUIRED_GROUPS),
        *summary_columns,
        *component_columns(),
    ]
    return sorted({column for column in columns if column})


def load_sample_data(filepath: Path) -> dict[str, Any] | None:
    if not filepath.exists():
        return None

    workbook = open_workbook(filepath)
    if EXCEL_SHEET not in workbook.sheetnames:
        raise ValueError("La hoja 'Detalle_Ate' no se encuentra en el archivo de datos")

    cutoff_date = workbook[EXCEL_SHEET][CUTOFF_CELL].value
    df = read_sheet(filepath, EXCEL_SHEET, HEADER_ROW)
    return {"data": df, "cutoff_date": to_date(cutoff_date)}


def validate_data_file(filepath: Path) -> dict[str, Any]:
    if not filepath.exists():
        return build_validation_error("No se encontro el archivo cargado.")

    errors: list[str] = []
    warnings: list[str] = []
    expected_columns = required_columns()
    summary: dict[str, Any] = {
        "indicator_code": CODE,
        "indicator_name": NAME,
        "filename": filepath.name,
        "file_size_bytes": filepath.stat().st_size,
        "sheet_name": EXCEL_SHEET,
        "cutoff_cell": CUTOFF_CELL,
        "header_row": HEADER_ROW,
        "validation_label": "Estado operativo",
        "required_columns_count": len(expected_columns),
    }

    try:
        workbook = open_workbook(filepath)
    except Exception as exc:
        return build_validation_error(f"No se pudo abrir el Excel: {exc}", summary)

    if EXCEL_SHEET not in workbook.sheetnames:
        errors.append("No se encontro la hoja obligatoria 'Detalle_Ate'.")
        return {"valid": False, "errors": errors, "warnings": warnings, "summary": summary}

    cutoff_date = to_date(workbook[EXCEL_SHEET][CUTOFF_CELL].value)
    if cutoff_date is None:
        warnings.append("No se pudo leer una fecha de corte valida desde la celda D9.")
    summary["cutoff_date"] = cutoff_date

    try:
        df = read_sheet(filepath, EXCEL_SHEET, HEADER_ROW)
    except Exception as exc:
        return {"valid": False, "errors": [f"No se pudo leer la hoja 'Detalle_Ate': {exc}"], "warnings": warnings, "summary": summary}

    missing_columns = [column for column in expected_columns if column not in df.columns]
    if missing_columns:
        errors.append("Faltan columnas obligatorias: " + ", ".join(missing_columns))

    summary["total_rows"] = len(df)
    summary["total_columns"] = len(df.columns)
    summary["columns_found"] = list(df.columns)
    summary["missing_columns"] = missing_columns
    summary["omitted_columns"] = omitted_columns_present(df)
    summary["provinces"] = unique_text_values(df, PROVINCE_COLUMN)
    summary["months"] = unique_text_values(df, MONTH_COLUMN)
    status_counts = value_counts(df, NUMERATOR_COLUMN)
    summary["status_counts"] = status_counts
    summary["obs_eval_counts"] = status_counts
    summary["insurance_counts"] = value_counts(df, INSURANCE_COLUMN)
    summary["denominator_counts"] = denominator_counts(df, cutoff_date)
    summary["component_counts"] = component_counts(df)

    if len(df) == 0:
        errors.append("La hoja 'Detalle_Ate' no contiene registros.")
    if DENOMINATOR_COLUMN in df and not (pd.to_numeric(df[DENOMINATOR_COLUMN], errors="coerce") == 1).any():
        warnings.append("No se encontraron registros con Registros = 1.")

    return {"valid": not errors, "errors": errors, "warnings": warnings, "summary": summary}


def unique_text_values(df: pd.DataFrame, column: str) -> list[str]:
    if column not in df:
        return []
    return sorted(value for value in df[column].dropna().astype(str).str.strip().unique().tolist() if value)


def value_counts(df: pd.DataFrame, column: str) -> dict[str, int]:
    if column not in df:
        return {}
    counts = df[column].fillna("VACIO").astype(str).str.strip().replace("", "VACIO").value_counts().to_dict()
    return {str(key): int(value) for key, value in counts.items()}


def component_counts(df: pd.DataFrame) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for component in COMPONENTS:
        flag_column = component["flag"]
        if flag_column not in df:
            continue
        normalized = df[flag_column].apply(
            lambda value: "Cumple" if flag_is_true(value) else ("Sin dato" if not has_value(value) else "No cumple")
        )
        counts[component["label"]] = {str(key): int(value) for key, value in normalized.value_counts().to_dict().items()}
    return counts


def omitted_columns_present(df: pd.DataFrame) -> list[str]:
    omitted: list[str] = []
    for group, columns in COLUMNAS_EXCEL.items():
        if group.startswith(OMITTED_GROUP_PREFIXES):
            omitted.extend(column for column in columns if column in df.columns)
    omitted.extend(column for column in OMITTED_SUMMARY_COLUMNS if column in df.columns)
    return sorted(set(omitted))
