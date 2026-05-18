"""Public MC-02 processor facade.

The platform loads every indicator through this stable module-level contract.
MC-02 internals are split into loader, dashboard and evaluator modules; this
file keeps the integration surface small for the shared API.
"""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from .config import DEFAULT_PROVINCE
from .dashboard import ALL_PROVINCES_TOKEN, build_report_summary, filter_data, get_filter_options
from .evaluator import evaluate_package
from .excel_loader import load_sample_data, prepare_data_file, validate_data_file
from .iron import anemia_alerts
from .rules import PROVINCE_COLUMN
from .storage import active_upload_id, build_active_report_summary, persist_active_upload, search_active_by_dni
from .utils import clean_value, flag_is_true, to_int, to_number


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
        "afi_DNI": clean_value(row.get("DNI o CNV")) or None,
        "NumCNV": clean_value(row.get("NumCNV")) or None,
        "afi_nombres": clean_value(row.get("Nombres")) or None,
        "afi_appaterno": clean_value(row.get("Ape_Paterno")) or None,
        "afi_apmaterno": clean_value(row.get("Ape_Materno")) or None,
        "fec_Nac": clean_value(row.get("Fec_Nac")) or None,
        "peso": to_number(row.get("Peso")),
        "edadGEst": to_int(row.get("Edad_Gestacional")),
        "Desc_prov": clean_value(row.get(PROVINCE_COLUMN)) or None,
        "Des_MicroRed": clean_value(row.get("MicroRed")) or None,
        "pre_CodigoRENAES": clean_value(row.get("Renaes")) or None,
        "Des_EESS": clean_value(row.get("EESS")) or None,
    }

    hemoglobin = package["details"]["hemoglobina"]

    return {
        "personal": personal,
        "vacunas": package["details"],
        "clinical_alerts": anemia_alerts(row),
        "cred_controls": [],
        "tamizaje": {
            "fecha": clean_value(row.get("fecha_1DH")) or None,
            "edad_atencion_dias": to_int(row.get("edad_1DH")),
            "cumple": flag_is_true(row.get("Obs_dh1")),
            "estado": hemoglobin["estado"],
            "mensaje": hemoglobin["mensaje"],
            "fecha_inicio": hemoglobin["fecha_inicio"],
            "fecha_limite": hemoglobin["fecha_limite"],
        },
        "paquete_completo": package["complete"],
    }


__all__ = [
    "ALL_PROVINCES_TOKEN",
    "build_report_summary",
    "evaluate_package",
    "filter_data",
    "get_filter_options",
    "load_sample_data",
    "prepare_data_file",
    "active_upload_id",
    "build_active_report_summary",
    "persist_active_upload",
    "search_active_by_dni",
    "search_by_dni",
    "validate_data_file",
]
