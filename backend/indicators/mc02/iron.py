"""MC-02 iron delivery rules and anemia alerts.

Technical sheet summary kept close to code:

- Preventive iron: CPMS ``99199.17`` for sulfato ferroso or hierro
  polimaltosado.
- Preventive micronutrients: CPMS ``99199.19``.
- Treatment for anemia: diagnosis ``D509`` or ``D649`` plus iron delivery
  ``99199.17``. The first treatment delivery must be linked to definitive
  anemia diagnosis; later deliveries do not require searching the diagnosis
  again.
- Common exclusions: telemedicine ``99499`` and first delivery marked with
  LAB ``TA`` for the preventive/treatment routes defined in the sheet.
- Preventive iron interval: 25 to 70 days between deliveries.
- Micronutrient interval: 25 to 35 days between deliveries.

The operative Excel already brings calculated flags for the current phase:
``obs_suple41`` (preventive iron around 4 months), ``obs_suple61`` (iron or
micronutrients from 6 to 11 months) and ``Obs_Anemia`` (anemia/treatment
route). This module adds the clinical warning used by search and reports, and
keeps the detailed route constants ready for future raw-attendance
recalculation.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .config import CODIGOS_ESTANDAR
from .utils import clean_value, format_short_date, has_value, to_date


ANEMIA_DIAGNOSIS_COLUMNS = ("Dx_Anemia", "CIE_Anemia_1Hier")
ANEMIA_DATE_COLUMNS = ("Fec_Anemia", "fecha_1Hier")
ANEMIA_OBSERVATION_COLUMNS = ("Obs_Anemia",)

IRON_TREATMENT_RULES = {
    "diagnosis_codes": sorted(CODIGOS_ESTANDAR["ANEMIA"]),
    "iron_code": "99199.17",
    "required_deliveries": 3,
    "excluded_codes": ["99499"],
    "excluded_first_delivery_lab": "TA",
}

PREVENTIVE_IRON_RULES = {
    "iron_code": "99199.17",
    "micronutrient_code": "99199.19",
    "iron_interval_days": {"min": 25, "max": 70},
    "micronutrient_interval_days": {"min": 25, "max": 35},
    "excluded_codes": ["99499"],
    "excluded_first_delivery_lab": "TA",
}


def _contains_anemia_code(value: Any) -> bool:
    text = clean_value(value).upper()
    return any(code in text for code in CODIGOS_ESTANDAR["ANEMIA"])


def has_anemia_diagnosis(row: pd.Series) -> bool:
    """Return true when the operative row carries anemia evidence."""
    if any(_contains_anemia_code(row.get(column)) for column in ANEMIA_DIAGNOSIS_COLUMNS):
        return True
    if any(has_value(row.get(column)) for column in ANEMIA_DATE_COLUMNS):
        return True

    observation = clean_value(row.get("Obs_Anemia")).upper()
    if observation and observation not in {"0", "NO", "NO CUMPLE", "SIN DATO"}:
        return True
    return False


def _meaningful_observation(value: Any) -> str:
    observation = clean_value(value)
    if observation.upper() in {"", "0", "NO", "NO CUMPLE", "SIN DATO"}:
        return ""
    return observation


def anemia_alerts(row: pd.Series) -> list[str]:
    """Build user-facing alerts for children with anemia diagnosis."""
    if not has_anemia_diagnosis(row):
        return []

    diagnosis = next((clean_value(row.get(column)) for column in ANEMIA_DIAGNOSIS_COLUMNS if has_value(row.get(column))), "")
    anemia_date = next((to_date(row.get(column)) for column in ANEMIA_DATE_COLUMNS if to_date(row.get(column))), None)
    observation = next((_meaningful_observation(row.get(column)) for column in ANEMIA_OBSERVATION_COLUMNS if _meaningful_observation(row.get(column))), "")

    pieces = ["Registra diagnostico o ruta de anemia"]
    if diagnosis:
        pieces.append(f"diagnostico: {diagnosis}")
    if anemia_date:
        pieces.append(f"fecha: {format_short_date(anemia_date)}")
    if observation:
        pieces.append(f"observacion: {observation}")

    detail = "; ".join(pieces) + "."
    return [
        f"{detail} La entrega de hierro debe revisarse como tratamiento de anemia: "
        "primera entrega vinculada a D509/D649 y al menos 3 entregas validas segun ficha tecnica."
    ]
