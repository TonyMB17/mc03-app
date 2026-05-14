from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl import load_workbook

try:
    from .config import CODIGOS_ESTANDAR, REGLAS_NEGOCIO
except ImportError:
    from config import CODIGOS_ESTANDAR, REGLAS_NEGOCIO


MONTHS_2026 = [
    (1, "enero"),
    (2, "febrero"),
    (3, "marzo"),
    (4, "abril"),
    (5, "mayo"),
    (6, "junio"),
    (7, "julio"),
    (8, "agosto"),
    (9, "setiembre"),
    (10, "octubre"),
    (11, "noviembre"),
]
MONTH_LABELS = {month: name for month, name in MONTHS_2026}

VERIFICATION_MONTHS = {6, 7, 8, 9, 10, 11}
DEFAULT_PROVINCE = "ABANCAY"
ALL_PROVINCES_TOKEN = "__ALL__"
CODE = "mc03"
NAME = "Paquete recien nacido"
EXCEL_SHEET = "Detalle_Ate"
CUTOFF_CELL = "B8"
HEADER_ROW = 10

REQUIRED_COLUMNS = [
    "Mes_eva",
    "Obs_Eval",
    "Esta_pac",
    "Desc_prov",
    "afi_DNI",
    "NumCNV",
    "fec_Nac",
    "fec1_BCG",
    "resul1_BCG",
    "Edad_ate1_BCG",
    "fecHVB",
    "resulHVB",
    "Edad_ateHVB",
    "Fecha_Atencion_1",
    "Codigo_HIS_1",
    "Edad_Atencion_1",
    "Fecha_Atencion_2",
    "Codigo_HIS_2",
    "Edad_Atencion_2",
    "Intervalo_2",
    "Fecha_Atencion_3",
    "Codigo_HIS_3",
    "Edad_Atencion_3",
    "Intervalo_3",
    "Fecha_Atencion_TN",
    "Codigo_HIS_TN",
    "Edad_Atencion_TN",
]


def _parse_cutoff_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    parsed = pd.to_datetime(value, errors="coerce")
    return parsed.date() if not pd.isna(parsed) else None


def load_sample_data(filepath: Path) -> dict[str, Any] | None:
    if not filepath.exists():
        return None

    workbook = load_workbook(filepath, data_only=True, read_only=True)
    if EXCEL_SHEET not in workbook.sheetnames:
        raise ValueError("La hoja 'Detalle_Ate' no se encuentra en el archivo de datos")

    sheet = workbook[EXCEL_SHEET]
    cutoff_date = _parse_cutoff_date(sheet[CUTOFF_CELL].value)

    df = pd.read_excel(
        filepath,
        sheet_name=EXCEL_SHEET,
        header=HEADER_ROW - 1,
        engine="openpyxl",
    )

    return {"data": df, "cutoff_date": cutoff_date}


def validate_data_file(filepath: Path) -> dict[str, Any]:
    if not filepath.exists():
        return {
            "valid": False,
            "errors": ["No se encontro el archivo cargado."],
            "warnings": [],
            "summary": {},
        }

    errors = []
    warnings = []
    summary: dict[str, Any] = {
        "indicator_code": CODE,
        "indicator_name": NAME,
        "filename": filepath.name,
        "file_size_bytes": filepath.stat().st_size,
        "sheet_name": EXCEL_SHEET,
        "cutoff_cell": CUTOFF_CELL,
        "header_row": HEADER_ROW,
        "validation_label": "Obs_Eval",
        "required_columns_count": len(REQUIRED_COLUMNS),
    }

    try:
        workbook = load_workbook(filepath, data_only=True, read_only=True)
    except Exception as exc:
        return {
            "valid": False,
            "errors": [f"No se pudo abrir el Excel: {exc}"],
            "warnings": [],
            "summary": summary,
        }

    if EXCEL_SHEET not in workbook.sheetnames:
        errors.append("No se encontro la hoja obligatoria 'Detalle_Ate'.")
        return {"valid": False, "errors": errors, "warnings": warnings, "summary": summary}

    sheet = workbook[EXCEL_SHEET]
    cutoff_date = _parse_cutoff_date(sheet[CUTOFF_CELL].value)
    if cutoff_date is None:
        warnings.append(f"No se pudo leer una fecha de corte valida desde la celda {CUTOFF_CELL}.")
    summary["cutoff_date"] = cutoff_date

    try:
        df = pd.read_excel(filepath, sheet_name=EXCEL_SHEET, header=HEADER_ROW - 1, engine="openpyxl")
    except Exception as exc:
        return {
            "valid": False,
            "errors": [f"No se pudo leer la hoja 'Detalle_Ate': {exc}"],
            "warnings": warnings,
            "summary": summary,
        }

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        errors.append("Faltan columnas obligatorias: " + ", ".join(missing_columns))
    summary["missing_columns"] = missing_columns

    total_rows = len(df)
    summary["total_rows"] = total_rows
    summary["total_columns"] = len(df.columns)
    summary["columns_found"] = list(df.columns)

    if total_rows == 0:
        errors.append("La hoja 'Detalle_Ate' no contiene registros.")

    if "Desc_prov" in df.columns:
        provinces = sorted(
            value
            for value in df["Desc_prov"].dropna().astype(str).str.strip().unique().tolist()
            if value
        )
        summary["provinces"] = provinces
    else:
        summary["provinces"] = []

    if "Mes_eva" in df.columns:
        months = sorted(
            value
            for value in df["Mes_eva"].dropna().astype(str).str.strip().unique().tolist()
            if value
        )
        summary["months"] = months
    else:
        summary["months"] = []

    if "Obs_Eval" in df.columns:
        obs_counts = df["Obs_Eval"].fillna("VACIO").astype(str).str.strip().value_counts().to_dict()
        summary["obs_eval_counts"] = obs_counts
        summary["status_counts"] = obs_counts
        if "Evaluado" not in obs_counts and "EVALUADO" not in {key.upper(): value for key, value in obs_counts.items()}:
            warnings.append("No se encontraron registros con Obs_Eval = Evaluado.")
    else:
        summary["obs_eval_counts"] = {}
        summary["status_counts"] = {}

    if "Esta_pac" in df.columns:
        summary["insurance_counts"] = df["Esta_pac"].fillna("VACIO").astype(str).str.strip().value_counts().to_dict()
    else:
        summary["insurance_counts"] = {}

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": summary,
    }


def _clean_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def _to_number(value: Any) -> float | None:
    parsed = pd.to_numeric(value, errors="coerce")
    return None if pd.isna(parsed) else float(parsed)


def _to_int(value: Any) -> int | None:
    parsed = _to_number(value)
    return None if parsed is None else int(parsed)


def _to_date(value: Any) -> date | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    parsed = pd.to_datetime(value, errors="coerce")
    return parsed.date() if not pd.isna(parsed) else None


def _format_date(value: date | None) -> str:
    return value.strftime("%d/%m/%Y") if value else "-"


def _has_value(value: Any) -> bool:
    return value is not None and not pd.isna(value) and str(value).strip() != ""


def _month_key(year: int, month: int) -> str:
    return f"{year}_{month}"


def _parse_month_key(value: Any) -> tuple[int | None, int | None, str | None]:
    text = _clean_text(value)
    if "_" not in text:
        return None, None, None
    year_text, month_text = text.split("_", 1)
    try:
        year = int(year_text)
        month = int(month_text)
    except ValueError:
        return None, None, None
    return year, month, MONTH_LABELS.get(month)


def _safe_row_value(row: pd.Series, column: str) -> Any:
    return row[column] if column in row.index else None


def _normalize_filter(value: str | None) -> str | None:
    if value is None:
        return DEFAULT_PROVINCE

    normalized = value.strip().upper()
    if normalized in {"", "ALL", "TODOS", ALL_PROVINCES_TOKEN}:
        return None
    return normalized


def filter_data(df: pd.DataFrame, province: str | None = DEFAULT_PROVINCE) -> pd.DataFrame:
    selected_province = _normalize_filter(province)
    if selected_province is None or "Desc_prov" not in df.columns:
        return df

    return df[df["Desc_prov"].astype(str).str.strip().str.upper() == selected_province]


def get_filter_options(df: pd.DataFrame) -> dict[str, Any]:
    provinces = []
    if df is not None and not df.empty and "Desc_prov" in df.columns:
        provinces = sorted(
            value
            for value in df["Desc_prov"].dropna().astype(str).str.strip().unique().tolist()
            if value
        )

    return {
        "provinces": provinces,
        "default_province": DEFAULT_PROVINCE,
        "default_target_coverage": REGLAS_NEGOCIO["META_COBERTURA_MENSUAL"],
        "included_insurance_types": sorted(
            "VACIO/SIN SEGURO" if value == "" else value
            for value in REGLAS_NEGOCIO["SEGUROS_INCLUIDOS"]
        ),
        "exclusion_criteria": {
            "included_obs_eval": "Evaluado",
            "excluded_obs_eval": "No_Evaluado",
        },
    }


def _normalize_target(value: float | None) -> float:
    if value is None:
        return float(REGLAS_NEGOCIO["META_COBERTURA_MENSUAL"])

    return max(0.0, min(100.0, float(value)))


def _coverage_semaphore(coverage: float, target: float) -> str:
    if coverage >= target:
        return "green"
    return "red"


def _is_in_denominator(row: pd.Series, year: int, month: int) -> bool:
    if _clean_text(_safe_row_value(row, "Mes_eva")) != _month_key(year, month):
        return False

    if _clean_text(_safe_row_value(row, "Obs_Eval")).upper() != "EVALUADO":
        return False

    insurance = _clean_text(_safe_row_value(row, "Esta_pac")).upper()
    if insurance not in REGLAS_NEGOCIO["SEGUROS_INCLUIDOS"]:
        return False

    return True


def _valid_vaccine(row: pd.Series, date_col: str, result_col: str, age_col: str) -> bool:
    age = _to_number(_safe_row_value(row, age_col))
    result = _clean_text(_safe_row_value(row, result_col)).upper()
    return (
        _has_value(_safe_row_value(row, date_col))
        and result != "PENDIENTE"
        and age is not None
        and age <= 1
    )


def _valid_cred(row: pd.Series, number: int) -> bool:
    age = _to_number(_safe_row_value(row, f"Edad_Atencion_{number}"))
    code = _clean_text(_safe_row_value(row, f"Codigo_HIS_{number}"))
    window_key = ["1ER_CRED", "2DO_CRED", "3ER_CRED"][number - 1]
    window = REGLAS_NEGOCIO["CRED_VENTANAS"][window_key]

    if not (_has_value(_safe_row_value(row, f"Fecha_Atencion_{number}")) and code == CODIGOS_ESTANDAR["CRED"]):
        return False
    if age is None or not (window["inicio"] <= age <= window["fin"]):
        return False

    if number > 1:
        interval = _to_number(_safe_row_value(row, f"Intervalo_{number}"))
        if interval is not None and interval < REGLAS_NEGOCIO["INTERVALO_MIN_CRED"]:
            return False

    return True


def _valid_tamizaje(row: pd.Series) -> bool:
    age = _to_number(_safe_row_value(row, "Edad_Atencion_TN"))
    code = _clean_text(_safe_row_value(row, "Codigo_HIS_TN")).removesuffix(".0")
    window = REGLAS_NEGOCIO["TAMIZAJE_VENTANA"]
    return (
        _has_value(_safe_row_value(row, "Fecha_Atencion_TN"))
        and code == CODIGOS_ESTANDAR["TAMIZAJE"]
        and age is not None
        and window["inicio_dia"] <= age <= window["fin_dia"]
    )


def _window_dates(birth_date: date | None, start_day: int, end_day: int) -> tuple[date | None, date | None]:
    if birth_date is None:
        return None, None
    return birth_date + timedelta(days=start_day), birth_date + timedelta(days=end_day)


def _missing_attention_detail(
    label: str,
    birth_date: date | None,
    start_day: int,
    end_day: int,
    reference_date: date,
) -> dict[str, Any]:
    start_date, deadline = _window_dates(birth_date, start_day, end_day)
    detail = {
        "cumple": False,
        "fecha_inicio": start_date,
        "fecha_limite": deadline,
    }

    if birth_date is None:
        return {
            **detail,
            "estado": "incumplimiento",
            "mensaje": f"No se registra atención de {label} y no hay fecha de nacimiento para calcular la ventana normativa.",
        }

    if reference_date < start_date:
        return {
            **detail,
            "estado": "programado",
            "mensaje": f"Próximo {label}: desde {_format_date(start_date)} hasta {_format_date(deadline)}.",
        }

    if start_date <= reference_date <= deadline:
        return {
            **detail,
            "estado": "advertencia",
            "mensaje": f"No se registra atención de {label}. Aún está dentro de la ventana; fecha límite: {_format_date(deadline)}.",
        }

    return {
        **detail,
        "estado": "incumplimiento",
        "mensaje": f"No se registra atención de {label}; el plazo venció el {_format_date(deadline)}.",
    }


def _attention_detail(
    label: str,
    has_attention: bool,
    valid_code: bool,
    valid_age: bool,
    birth_date: date | None,
    start_day: int,
    end_day: int,
    reference_date: date,
    expected_code: str | None = None,
    actual_code: str | None = None,
    actual_age: int | None = None,
    interval_valid: bool = True,
    interval: int | None = None,
) -> dict[str, Any]:
    start_date, deadline = _window_dates(birth_date, start_day, end_day)

    if not has_attention:
        return _missing_attention_detail(label, birth_date, start_day, end_day, reference_date)

    if not valid_code:
        actual = actual_code or "vacío"
        return {
            "cumple": False,
            "estado": "incumplimiento",
            "mensaje": f"Se registra atención de {label}, pero con código {actual}; se esperaba {expected_code}.",
            "fecha_inicio": start_date,
            "fecha_limite": deadline,
        }

    if not valid_age:
        age_text = f"{actual_age} días" if actual_age is not None else "edad no registrada"
        return {
            "cumple": False,
            "estado": "incumplimiento",
            "mensaje": f"Atención de {label} registrada fuera de plazo ({age_text}); ventana: día {start_day} al {end_day}.",
            "fecha_inicio": start_date,
            "fecha_limite": deadline,
        }

    if not interval_valid:
        interval_text = f"{interval} días" if interval is not None else "intervalo no registrado"
        return {
            "cumple": False,
            "estado": "incumplimiento",
            "mensaje": f"Atención de {label} registrada, pero no cumple el intervalo mínimo de 7 días ({interval_text}).",
            "fecha_inicio": start_date,
            "fecha_limite": deadline,
        }

    return {
        "cumple": True,
        "estado": "cumple",
        "mensaje": f"{label} registrado dentro del plazo normativo.",
        "fecha_inicio": start_date,
        "fecha_limite": deadline,
    }


def _vaccine_detail(
    row: pd.Series,
    label: str,
    date_col: str,
    result_col: str,
    age_col: str,
    reference_date: date,
) -> dict[str, Any]:
    age = _to_int(_safe_row_value(row, age_col))
    has_attention = _has_value(_safe_row_value(row, date_col))
    result = _clean_text(_safe_row_value(row, result_col)).upper()
    birth_date = _to_date(_safe_row_value(row, "fec_Nac"))
    detail = _attention_detail(
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


def _cred_detail(row: pd.Series, number: int, reference_date: date) -> dict[str, Any]:
    window_key = ["1ER_CRED", "2DO_CRED", "3ER_CRED"][number - 1]
    window = REGLAS_NEGOCIO["CRED_VENTANAS"][window_key]
    age = _to_int(_safe_row_value(row, f"Edad_Atencion_{number}"))
    code = _clean_text(_safe_row_value(row, f"Codigo_HIS_{number}"))
    interval = _to_int(_safe_row_value(row, f"Intervalo_{number}"))
    interval_valid = number == 1 or interval is None or interval >= REGLAS_NEGOCIO["INTERVALO_MIN_CRED"]

    return _attention_detail(
        label=f"CRED {number}",
        has_attention=_has_value(_safe_row_value(row, f"Fecha_Atencion_{number}")),
        valid_code=code == CODIGOS_ESTANDAR["CRED"],
        valid_age=age is not None and window["inicio"] <= age <= window["fin"],
        birth_date=_to_date(_safe_row_value(row, "fec_Nac")),
        start_day=window["inicio"],
        end_day=window["fin"],
        reference_date=reference_date,
        expected_code=CODIGOS_ESTANDAR["CRED"],
        actual_code=code,
        actual_age=age,
        interval_valid=interval_valid,
        interval=interval,
    )


def _tamizaje_detail(row: pd.Series, reference_date: date) -> dict[str, Any]:
    age = _to_int(_safe_row_value(row, "Edad_Atencion_TN"))
    code = _clean_text(_safe_row_value(row, "Codigo_HIS_TN")).removesuffix(".0")
    window = REGLAS_NEGOCIO["TAMIZAJE_VENTANA"]

    return _attention_detail(
        label="tamizaje neonatal",
        has_attention=_has_value(_safe_row_value(row, "Fecha_Atencion_TN")),
        valid_code=code == CODIGOS_ESTANDAR["TAMIZAJE"],
        valid_age=age is not None and window["inicio_dia"] <= age <= window["fin_dia"],
        birth_date=_to_date(_safe_row_value(row, "fec_Nac")),
        start_day=window["inicio_dia"],
        end_day=window["fin_dia"],
        reference_date=reference_date,
        expected_code=CODIGOS_ESTANDAR["TAMIZAJE"],
        actual_code=code,
        actual_age=age,
    )


def evaluate_package(row: pd.Series, reference_date: date | None = None) -> dict[str, Any]:
    reference_date = reference_date or date.today()
    details = {
        "bcg": _vaccine_detail(row, "BCG", "fec1_BCG", "resul1_BCG", "Edad_ate1_BCG", reference_date),
        "hvb": _vaccine_detail(row, "HvB", "fecHVB", "resulHVB", "Edad_ateHVB", reference_date),
        "cred_1": _cred_detail(row, 1, reference_date),
        "cred_2": _cred_detail(row, 2, reference_date),
        "cred_3": _cred_detail(row, 3, reference_date),
        "tamizaje": _tamizaje_detail(row, reference_date),
    }
    checks = {key: value["cumple"] for key, value in details.items()}
    reasons = [value["mensaje"] for value in details.values() if not value["cumple"]]
    return {"complete": not reasons, "checks": checks, "details": details, "reasons": reasons}


def _omiso_from_row(row: pd.Series, reasons: list[str]) -> dict[str, Any]:
    year, month, month_name = _parse_month_key(_safe_row_value(row, "Mes_eva"))
    return {
        "Mes_eva": _clean_text(_safe_row_value(row, "Mes_eva")) or None,
        "month": month_name,
        "year": year,
        "afi_DNI": _clean_text(_safe_row_value(row, "afi_DNI")) or None,
        "NumCNV": _clean_text(_safe_row_value(row, "NumCNV")) or None,
        "fec_Nac": _clean_text(_safe_row_value(row, "fec_Nac")) or None,
        "afi_nombres": _clean_text(_safe_row_value(row, "afi_nombres")) or None,
        "afi_appaterno": _clean_text(_safe_row_value(row, "afi_appaterno")) or None,
        "afi_apmaterno": _clean_text(_safe_row_value(row, "afi_apmaterno")) or None,
        "Desc_prov": _clean_text(_safe_row_value(row, "Desc_prov")) or None,
        "Des_MicroRed": _clean_text(_safe_row_value(row, "Des_MicroRed")) or None,
        "pre_CodigoRENAES": _clean_text(_safe_row_value(row, "pre_CodigoRENAES")) or None,
        "Des_EESS": _clean_text(_safe_row_value(row, "Des_EESS")) or None,
        "reason": "; ".join(reasons),
    }


def build_report_summary(
    df: pd.DataFrame,
    cutoff_date: date | None = None,
    province: str | None = DEFAULT_PROVINCE,
    target_coverage: float | None = None,
) -> Any:
    df = filter_data(df, province)
    period_start = date(2026, 6, 1)
    period_end = date(2026, 11, 30)
    target = _normalize_target(target_coverage)
    monthly = []
    omisos = []

    for month, month_name in MONTHS_2026:
        year = 2026
        denominator_df = df[df.apply(lambda row: _is_in_denominator(row, year, month), axis=1)]

        numerator = 0
        for _, row in denominator_df.iterrows():
            package = evaluate_package(row, cutoff_date)
            if package["complete"]:
                numerator += 1
            else:
                omisos.append(_omiso_from_row(row, package["reasons"]))

        denominator = len(denominator_df)
        coverage = round((numerator / denominator) * 100, 2) if denominator else 0.0
        monthly.append(
            {
                "month": month_name,
                "year": year,
                "in_verification_period": month in VERIFICATION_MONTHS,
                "compliant": denominator > 0 and coverage >= target,
                "semaphore": _coverage_semaphore(coverage, target),
                "coverage": coverage,
                "denominator": denominator,
                "numerator": numerator,
            }
        )

    verification_monthly = [item for item in monthly if item["in_verification_period"]]
    months_met = sum(1 for item in verification_monthly if item["compliant"])

    return {
        "period_start": period_start,
        "period_end": period_end,
        "cut_off_date": cutoff_date,
        "target_coverage": target,
        "months_evaluated": len(verification_monthly),
        "months_met": months_met,
        "committed": months_met >= 5,
        "monthly": monthly,
        "omisos": omisos,
    }


def search_by_dni(
    df: pd.DataFrame,
    dni: str,
    reference_date: date | None = None,
    province: str | None = DEFAULT_PROVINCE,
) -> dict[str, Any] | None:
    """Busca un registro por DNI y retorna los datos de cumplimiento del paquete."""
    if df is None or df.empty:
        return None

    df = filter_data(df, province)
    result = df[df["afi_DNI"].astype(str).str.strip() == dni.strip()]
    if result.empty:
        return None

    row = result.iloc[0]
    package = evaluate_package(row, reference_date)

    personal = {
        "afi_DNI": _clean_text(row.get("afi_DNI")) or None,
        "NumCNV": _clean_text(row.get("NumCNV")) or None,
        "afi_nombres": _clean_text(row.get("afi_nombres")) or None,
        "afi_appaterno": _clean_text(row.get("afi_appaterno")) or None,
        "afi_apmaterno": _clean_text(row.get("afi_apmaterno")) or None,
        "fec_Nac": _clean_text(row.get("fec_Nac")) or None,
        "peso": _to_number(row.get("peso")),
        "edadGEst": _to_int(row.get("edadGEst")),
        "Desc_prov": _clean_text(row.get("Desc_prov")) or None,
        "Des_MicroRed": _clean_text(row.get("Des_MicroRed")) or None,
        "pre_CodigoRENAES": _clean_text(row.get("pre_CodigoRENAES")) or None,
        "Des_EESS": _clean_text(row.get("Des_EESS")) or None,
    }

    cred_controls = []
    for i in range(1, 4):
        fecha_col = f"Fecha_Atencion_{i}"
        cred_controls.append(
            {
                "numero": i,
                "fecha": _clean_text(row.get(fecha_col)) or None,
                "edad_atencion_dias": _to_int(row.get(f"Edad_Atencion_{i}")),
                "cumple": package["checks"][f"cred_{i}"],
                "estado": package["details"][f"cred_{i}"]["estado"],
                "mensaje": package["details"][f"cred_{i}"]["mensaje"],
                "fecha_inicio": package["details"][f"cred_{i}"]["fecha_inicio"],
                "fecha_limite": package["details"][f"cred_{i}"]["fecha_limite"],
            }
        )

    return {
        "personal": personal,
        "vacunas": {
            "BCG": {
                "codigo": CODIGOS_ESTANDAR["BCG"],
                "fecha": _clean_text(row.get("fec1_BCG")) or None,
                "resultado": _clean_text(row.get("resul1_BCG")) or None,
                "edad_atencion_dias": _to_int(row.get("Edad_ate1_BCG")),
                "cumple": package["checks"]["bcg"],
                "estado": package["details"]["bcg"]["estado"],
                "mensaje": package["details"]["bcg"]["mensaje"],
                "fecha_inicio": package["details"]["bcg"]["fecha_inicio"],
                "fecha_limite": package["details"]["bcg"]["fecha_limite"],
            },
            "HVB": {
                "codigo": CODIGOS_ESTANDAR["HVB"],
                "fecha": _clean_text(row.get("fecHVB")) or None,
                "resultado": _clean_text(row.get("resulHVB")) or None,
                "edad_atencion_dias": _to_int(row.get("Edad_ateHVB")),
                "cumple": package["checks"]["hvb"],
                "estado": package["details"]["hvb"]["estado"],
                "mensaje": package["details"]["hvb"]["mensaje"],
                "fecha_inicio": package["details"]["hvb"]["fecha_inicio"],
                "fecha_limite": package["details"]["hvb"]["fecha_limite"],
            },
        },
        "cred_controls": cred_controls,
        "tamizaje": {
            "fecha": _clean_text(row.get("Fecha_Atencion_TN")) or None,
            "edad_atencion_dias": _to_int(row.get("Edad_Atencion_TN")),
            "cumple": package["checks"]["tamizaje"],
            "estado": package["details"]["tamizaje"]["estado"],
            "mensaje": package["details"]["tamizaje"]["mensaje"],
            "fecha_inicio": package["details"]["tamizaje"]["fecha_inicio"],
            "fecha_limite": package["details"]["tamizaje"]["fecha_limite"],
        },
        "paquete_completo": package["complete"],
    }
