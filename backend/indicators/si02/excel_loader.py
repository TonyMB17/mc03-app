"""Excel package loading and validation for SI-02."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import pandas as pd

try:
    from ...core.dates import clean_text, parse_excel_date
    from ...core.excel import build_validation_error, open_workbook, read_header_values, read_sheet
except ImportError:
    from core.dates import clean_text, parse_excel_date
    from core.excel import build_validation_error, open_workbook, read_header_values, read_sheet

from .config import CODE, DETAIL_SHEET, EXPECTED_PACKAGE_CODES, NAME, SUBINDICATORS, SubindicatorSpec


def required_columns(subindicator_code: str) -> list[str]:
    return sorted(set(_spec(subindicator_code).required_columns))


def operational_columns(subindicator_code: str) -> list[str]:
    spec = _spec(subindicator_code)
    return sorted(set((*spec.required_columns, *spec.optional_columns)))


def identify_subindicator(filepath: Path) -> str | None:
    candidates: list[tuple[int, int, str]] = []
    for spec in SUBINDICATORS.values():
        try:
            headers = set(read_header_values(filepath, DETAIL_SHEET, spec.header_row))
        except Exception:
            continue
        required = set(required_columns(spec.code))
        missing_count = len(required - headers)
        token_count = sum(1 for token in spec.identifier_tokens if token in headers)
        score = token_count * 1000 - missing_count
        candidates.append((score, -missing_count, spec.code))

    if not candidates:
        return None

    candidates.sort(reverse=True)
    best_score, best_missing, best_code = candidates[0]
    if best_score <= 0 or best_missing < -10:
        return None
    return best_code


def validate_data_file(filepath: Path) -> dict[str, Any]:
    return validate_subindicator_file(filepath)


def validate_subindicator_file(filepath: Path, expected_code: str | None = None) -> dict[str, Any]:
    return prepare_subindicator_file(filepath, expected_code=expected_code, load_data=False)["validation"]


def load_subindicator_data(filepath: Path, expected_code: str | None = None) -> dict[str, Any] | None:
    if not filepath.exists():
        return None
    prepared = prepare_subindicator_file(filepath, expected_code=expected_code, load_data=True)
    validation = prepared["validation"]
    if not validation["valid"]:
        raise ValueError("; ".join(validation["errors"]))
    return {
        "data": prepared["data"],
        "cutoff_date": prepared["cutoff_date"],
        "subindicator_code": prepared["subindicator_code"],
    }


def prepare_subindicator_file(filepath: Path, expected_code: str | None = None, load_data: bool = True) -> dict[str, Any]:
    if not filepath.exists():
        return {"validation": build_validation_error("No se encontro el archivo cargado.")}

    detected_code = identify_subindicator(filepath)
    subindicator_code = expected_code or detected_code
    if subindicator_code is None:
        return {
            "validation": build_validation_error(
                "No se pudo identificar el subindicador SI-02 del archivo.",
                _base_summary(filepath, None, detected_code),
            )
        }

    spec = _spec(subindicator_code)
    errors: list[str] = []
    warnings: list[str] = []
    summary = _base_summary(filepath, spec, detected_code)

    if expected_code and detected_code and expected_code != detected_code:
        errors.append(f"El archivo parece corresponder a {detected_code}, pero se esperaba {expected_code}.")

    try:
        workbook = open_workbook(filepath)
    except Exception as exc:
        return {"validation": build_validation_error(f"No se pudo abrir el Excel: {exc}", summary)}

    if DETAIL_SHEET not in workbook.sheetnames:
        workbook.close()
        errors.append("No se encontro la hoja obligatoria 'Detalle_Ate'.")
        return {"validation": {"valid": False, "errors": errors, "warnings": warnings, "summary": summary}}

    cutoff_date = parse_excel_date(workbook[DETAIL_SHEET][spec.cutoff_cell].value)
    workbook.close()
    if cutoff_date is None:
        warnings.append(f"No se pudo leer una fecha de corte valida desde la celda {spec.cutoff_cell}.")
    summary["cutoff_date"] = cutoff_date

    try:
        headers = read_header_values(filepath, DETAIL_SHEET, spec.header_row)
    except Exception as exc:
        return {"validation": {"valid": False, "errors": [f"No se pudo leer cabecera: {exc}"], "warnings": warnings, "summary": summary}}

    expected_columns = required_columns(spec.code)
    missing_columns = [column for column in expected_columns if column not in headers]
    if missing_columns:
        errors.append("Faltan columnas obligatorias: " + ", ".join(missing_columns))

    summary["columns_found"] = headers
    summary["total_columns"] = len(headers)
    summary["required_columns_count"] = len(expected_columns)
    summary["missing_columns"] = missing_columns

    df: pd.DataFrame | None = None
    if load_data or not missing_columns:
        try:
            columns_to_read = [column for column in operational_columns(spec.code) if column in headers]
            df = read_sheet(filepath, DETAIL_SHEET, spec.header_row, usecols=columns_to_read)
        except Exception as exc:
            return {
                "validation": {
                    "valid": False,
                    "errors": [f"No se pudo leer la hoja 'Detalle_Ate': {exc}"],
                    "warnings": warnings,
                    "summary": summary,
                }
            }

        summary.update(_dataframe_summary(df, spec))
        if len(df) == 0:
            errors.append("La hoja 'Detalle_Ate' no contiene registros.")

    validation = {"valid": not errors, "errors": errors, "warnings": warnings, "summary": summary}
    return {
        "validation": validation,
        "data": df,
        "cutoff_date": cutoff_date,
        "subindicator_code": spec.code,
        "spec": spec,
    }


def validate_upload_package(filepaths: Iterable[Path]) -> dict[str, Any]:
    return prepare_upload_package(filepaths, load_data=False)["validation"]


def prepare_data_files(filepaths: Iterable[Path]) -> dict[str, Any]:
    return prepare_upload_package(filepaths, load_data=True)


def prepare_data_file(filepath: Path) -> dict[str, Any]:
    return prepare_subindicator_file(filepath, load_data=True)


def load_sample_data(filepath: Path) -> dict[str, Any] | None:
    loaded = load_subindicator_data(filepath)
    if loaded is None:
        return None
    return {"data": {loaded["subindicator_code"]: loaded["data"]}, "cutoff_date": {loaded["subindicator_code"]: loaded["cutoff_date"]}}


def prepare_upload_package(filepaths: Iterable[Path], load_data: bool = True) -> dict[str, Any]:
    files = [Path(path) for path in filepaths]
    errors: list[str] = []
    warnings: list[str] = []
    subindicators: dict[str, dict[str, Any]] = {}
    data: dict[str, pd.DataFrame] = {}
    cutoff_dates: dict[str, Any] = {}
    duplicate_subindicators: list[str] = []
    unknown_files: list[str] = []

    if len(files) != len(EXPECTED_PACKAGE_CODES):
        errors.append(
            f"SI-02 requiere exactamente {len(EXPECTED_PACKAGE_CODES)} archivos Excel, uno por subindicador. "
            f"Se recibieron {len(files)}."
        )

    for filepath in files:
        prepared = prepare_subindicator_file(filepath, load_data=load_data)
        validation = prepared["validation"]
        code = prepared.get("subindicator_code") or validation.get("summary", {}).get("subindicator_code")

        if code in subindicators:
            duplicate_subindicators.append(code)
            errors.append(f"Se encontro mas de un archivo para {code}.")
        if not validation["valid"]:
            errors.extend(f"{filepath.name}: {error}" for error in validation["errors"])
        warnings.extend(f"{filepath.name}: {warning}" for warning in validation["warnings"])

        if code:
            subindicators[code] = validation["summary"]
            if prepared.get("data") is not None:
                data[code] = prepared["data"]
            cutoff_dates[code] = prepared.get("cutoff_date")
        else:
            unknown_files.append(filepath.name)

    missing = [code for code in EXPECTED_PACKAGE_CODES if code not in subindicators]
    if missing:
        errors.append("Faltan archivos obligatorios del paquete SI-02: " + ", ".join(missing))

    non_empty_cutoffs = {code: value for code, value in cutoff_dates.items() if value is not None}
    distinct_cutoffs = sorted({value for value in non_empty_cutoffs.values()})
    cutoff_date_mismatch = len(distinct_cutoffs) > 1
    if cutoff_date_mismatch:
        errors.append(
            "Las fechas de corte del paquete SI-02 no coinciden: "
            + ", ".join(f"{code}={value}" for code, value in sorted(non_empty_cutoffs.items()))
        )

    summary = {
        "indicator_code": CODE,
        "indicator_name": NAME,
        "sheet_name": DETAIL_SHEET,
        "files_received": len(files),
        "expected_files": len(EXPECTED_PACKAGE_CODES),
        "subindicators_found": sorted(subindicators.keys()),
        "missing_subindicators": missing,
        "duplicate_subindicators": sorted(set(duplicate_subindicators)),
        "unknown_files": unknown_files,
        "subindicators": subindicators,
        "cutoff_dates": {code: value for code, value in cutoff_dates.items()},
        "cutoff_date_mismatch": cutoff_date_mismatch,
        "cutoff_date": _latest_date(cutoff_dates.values()),
        "package_files": _package_file_status(subindicators, missing, duplicate_subindicators),
        "total_rows": sum(int(item.get("total_rows", 0)) for item in subindicators.values()),
        "total_columns": sum(int(item.get("total_columns", 0)) for item in subindicators.values()),
        "total_loaded_columns": sum(int(item.get("loaded_columns", 0)) for item in subindicators.values()),
        "loaded_columns": sum(int(item.get("loaded_columns", 0)) for item in subindicators.values()),
        "required_columns_count": sum(int(item.get("required_columns_count", 0)) for item in subindicators.values()),
        "missing_columns": sorted({column for item in subindicators.values() for column in item.get("missing_columns", [])}),
        "provinces": sorted({province for item in subindicators.values() for province in item.get("provinces", [])}),
        "months": sorted({month for item in subindicators.values() for month in item.get("months", [])}),
        "insurance_counts": _merge_count_dicts(item.get("insurance_counts", {}) for item in subindicators.values()),
    }

    validation = {"valid": not errors, "errors": errors, "warnings": warnings, "summary": summary}
    return {"validation": validation, "data": data, "cutoff_dates": cutoff_dates}


def _package_file_status(
    subindicators: dict[str, dict[str, Any]],
    missing: list[str],
    duplicate_subindicators: list[str],
) -> list[dict[str, Any]]:
    duplicates = set(duplicate_subindicators)
    missing_set = set(missing)
    items = []
    for code in EXPECTED_PACKAGE_CODES:
        spec = SUBINDICATORS[code]
        summary = subindicators.get(code, {})
        status = "missing" if code in missing_set else "duplicate" if code in duplicates else "ok"
        items.append(
            {
                "subindicator_code": code,
                "subindicator_official_code": spec.official_code,
                "subindicator_name": spec.title,
                "status": status,
                "filename": summary.get("filename"),
                "cutoff_date": summary.get("cutoff_date"),
                "rows": summary.get("total_rows", 0),
                "columns": summary.get("total_columns", 0),
                "missing_columns": summary.get("missing_columns", []),
            }
        )
    return items


def _spec(subindicator_code: str) -> SubindicatorSpec:
    try:
        return SUBINDICATORS[subindicator_code]
    except KeyError as exc:
        raise ValueError(f"Subindicador SI-02 no configurado: {subindicator_code}") from exc


def _base_summary(filepath: Path, spec: SubindicatorSpec | None, detected_code: str | None) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "indicator_code": CODE,
        "indicator_name": NAME,
        "filename": filepath.name,
        "file_size_bytes": filepath.stat().st_size if filepath.exists() else 0,
        "sheet_name": DETAIL_SHEET,
        "detected_subindicator_code": detected_code,
    }
    if spec:
        summary.update(
            {
                "subindicator_code": spec.code,
                "subindicator_official_code": spec.official_code,
                "subindicator_name": spec.title,
                "target_coverage": spec.target_coverage,
                "cutoff_cell": spec.cutoff_cell,
                "header_row": spec.header_row,
                "province_column": spec.province_column,
                "month_column": spec.month_column,
                "status_column": spec.status_column,
                "status_flag_column": spec.status_flag_column,
            }
        )
    return summary


def _dataframe_summary(df: pd.DataFrame, spec: SubindicatorSpec) -> dict[str, Any]:
    return {
        "total_rows": int(len(df)),
        "loaded_columns": int(len(df.columns)),
        "provinces": _unique_text_values(df, spec.province_column),
        "months": _unique_text_values(df, spec.month_column),
        "status_counts": _value_counts(df, spec.status_column),
        "status_flag_counts": _value_counts(df, spec.status_flag_column),
        "insurance_counts": _value_counts(df, "TIPO_SEGURO"),
    }


def _unique_text_values(df: pd.DataFrame, column: str) -> list[str]:
    if column not in df:
        return []
    return sorted({value for value in df[column].dropna().map(clean_text).tolist() if value})


def _value_counts(df: pd.DataFrame, column: str) -> dict[str, int]:
    if column not in df:
        return {}
    counts = df[column].fillna("VACIO").map(clean_text).replace("", "VACIO").value_counts().to_dict()
    return {str(key): int(value) for key, value in counts.items()}


def _latest_date(values: Iterable[Any]) -> Any:
    dates = [value for value in values if value is not None]
    return max(dates) if dates else None


def _merge_count_dicts(items: Iterable[dict[str, int]]) -> dict[str, int]:
    merged: dict[str, int] = {}
    for item in items:
        for key, value in item.items():
            merged[key] = merged.get(key, 0) + int(value)
    return merged
