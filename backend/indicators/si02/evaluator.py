"""SI-02 component evaluators based on attendance columns."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import pandas as pd

from .config import ANEMIA_CODES, DOSAGE_CODES, IRON_CODES, SUBINDICATORS
from .utils import (
    age_from_birth,
    clean_value,
    days_between,
    has_value,
    normalize_code,
    normalize_lab,
    to_int,
    value_in_window,
)


@dataclass(frozen=True)
class ComponentRule:
    key: str
    label: str
    evaluator: Callable[[pd.Series], dict[str, Any]]
    observed_only: bool = False


def evaluate_row(row: pd.Series, subindicator_code: str) -> dict[str, Any]:
    rules = component_rules(subindicator_code)
    details = {rule.key: rule.evaluator(row) for rule in rules}
    mandatory = {rule.key: details[rule.key] for rule in rules if not rule.observed_only}
    reasons = [detail["mensaje"] for detail in mandatory.values() if not detail["cumple"]]
    return {
        "subindicator_code": subindicator_code,
        "complete": not reasons,
        "details": details,
        "reasons": reasons,
    }


def evaluate_dataframe(df: pd.DataFrame, subindicator_code: str) -> pd.DataFrame:
    rows = []
    for index, row in df.iterrows():
        package = evaluate_row(row, subindicator_code)
        rows.append(
            {
                "index": index,
                "cumple": package["complete"],
                "componentes_observados": ", ".join(
                    detail["label"] for detail in package["details"].values() if not detail["cumple"]
                ),
                "motivos": "\n".join(package["reasons"]),
                "detalles": package["details"],
            }
        )
    return pd.DataFrame(rows).set_index("index") if rows else pd.DataFrame(columns=["cumple", "componentes_observados", "motivos", "detalles"])


def component_rules(subindicator_code: str) -> list[ComponentRule]:
    if subindicator_code == "si02_01":
        return [
            ComponentRule("hierro_4m", "Hierro 4 meses", lambda row: attention_component(row, "Hierro 4 meses", "Fec_H2", "Cie_H2", "Lab_H2", "Intervalo3", IRON_CODES, 110, 130)),
            ComponentRule("dosaje_6m", "Dosaje hemoglobina 6 meses", lambda row: attention_component(row, "Dosaje hemoglobina 6 meses", "Fec_Dh3", "Cie_Dh3", "Lab_Dh3", "Intervalo5", DOSAGE_CODES, 170, 209)),
            ComponentRule("ta", "Termino de tratamiento", lambda row: attention_component(row, "Termino de tratamiento", "Fec_TA3", "Cie_TA3", "Lab_TA3", "Intervalo6", IRON_CODES, 170, 209, required_lab="TA")),
        ]
    if subindicator_code == "si02_02":
        return [
            ComponentRule("dh_1m", "Dosaje 1 mes", lambda row: attention_component(row, "Dosaje 1 mes", "Fec_Dh1", "Cie_Dh1", "lab_Dh1", "Intervalo1", DOSAGE_CODES, 30, 59)),
            ComponentRule("hierro_1m", "Hierro 1 mes", lambda row: attention_component(row, "Hierro 1 mes", "Fec_H1", "Cie_H1", "Lab_H1", "Intervalo2", {"99199.17"}, 30, 59)),
            ComponentRule("hierro_4m", "Hierro 80 a 130 dias", lambda row: attention_component(row, "Hierro 80 a 130 dias", "Fec_H2", "Cie_H2", "Lab_H2", "Intervalo3", {"99199.17"}, 80, 130)),
            ComponentRule("dh_3m", "Dosaje 3 meses", lambda row: attention_component(row, "Dosaje 3 meses", "Fec_Dh2", "Cie_Dh2", "Lab_Dh2", "Intervalo4", DOSAGE_CODES, 120, 151)),
            ComponentRule("dh_6m", "Dosaje 6 meses", lambda row: attention_component(row, "Dosaje 6 meses", "Fec_Dh3", "Cie_Dh3", "Lab_Dh3", "Intervalo5", DOSAGE_CODES, 170, 209)),
            ComponentRule("ta_observado", "Termino de tratamiento observado", lambda row: attention_component(row, "Termino de tratamiento observado", "Fec_TA3", "Cie_TA3", "Lab_TA3", "Intervalo6", IRON_CODES, 170, 209, required_lab="TA"), observed_only=True),
        ]
    if subindicator_code == "si02_03":
        return [
            ComponentRule("anemia_6m", "Diagnostico de anemia 6 meses", anemia_component),
            ComponentRule("dosaje_denominador", "Dosaje denominador 6 meses", lambda row: attention_component(row, "Dosaje denominador 6 meses", "fec_DH", "Ci10_Dh", "lab_Dh", None, DOSAGE_CODES, 170, 209, age_date_column="fec_DH")),
            ComponentRule("hierro_tratamiento", "Hierro tratamiento", treatment_iron_component),
            ComponentRule("dh_1m", "Dosaje control 1 mes", lambda row: attention_component(row, "Dosaje control 1 mes", "Fec_DH1", "Cie_Dh1", "Lab_Dh1", "intervaloDh1", DOSAGE_CODES, 25, 59)),
            ComponentRule("dh_2m", "Dosaje control 2 meses", lambda row: attention_component(row, "Dosaje control 2 meses", "Fec_DH2", "Cie_Dh2", "Lab_Dh2", "intervaloDh2", DOSAGE_CODES, 55, 89)),
            ComponentRule("dh_3m", "Dosaje control 3 meses", lambda row: attention_component(row, "Dosaje control 3 meses", "Fec_DH3", "Cie_Dh3", "Lab_Dh3", "intervaloDh3", DOSAGE_CODES, 85, 119)),
            ComponentRule("ta", "Termino de tratamiento", lambda row: attention_component(row, "Termino de tratamiento", "Fec_TA1", "Cie10_TA1", "lab_TA1", "intervaloTA", IRON_CODES, 365, 398, required_lab="TA")),
            ComponentRule("dh_6m", "Dosaje control 6 meses", lambda row: attention_component(row, "Dosaje control 6 meses", "Fec_DH12m", "Cie_Dh12m", "Lab_Dh12m", "intervaloDh12m", DOSAGE_CODES, 170, 209)),
        ]
    if subindicator_code == "si02_04":
        return [
            ComponentRule("dosaje_denominador", "Dosaje denominador 6 meses", lambda row: attention_component(row, "Dosaje denominador 6 meses", "fec_DH", "Ci10_Dh", "lab_Dh", None, DOSAGE_CODES, 170, 209, age_date_column="fec_DH")),
            ComponentRule("sin_anemia", "Sin diagnostico de anemia", no_anemia_component),
            ComponentRule("hierro_preventivo", "Hierro preventivo", preventive_iron_component),
            ComponentRule("dh_3m", "Dosaje control 3 meses", lambda row: interval_from_anchor_component(row, "Dosaje control 3 meses", "Fec_hierro1", "Fec_DH1", "Cie_Dh1", "Lab_Dh1", DOSAGE_CODES, 25, 119)),
            ComponentRule("ta", "Termino de tratamiento", lambda row: interval_from_anchor_component(row, "Termino de tratamiento", "Fec_hierro1", "Fec_TA1", "Cie10_TA1", "lab_TA1", IRON_CODES, 120, 209, required_lab="TA")),
            ComponentRule("dh_12m", "Dosaje hemoglobina 12 meses", lambda row: interval_from_anchor_component(row, "Dosaje hemoglobina 12 meses", "Fec_hierro1", "Fec_DH12m", "Cie_Dh12m", "Lab_Dh12m", DOSAGE_CODES, 150, 209)),
        ]
    raise ValueError(f"Subindicador SI-02 no soportado: {subindicator_code}")


def attention_component(
    row: pd.Series,
    label: str,
    date_column: str,
    code_column: str,
    lab_column: str | None,
    interval_column: str | None,
    valid_codes: set[str],
    min_value: int,
    max_value: int,
    *,
    required_lab: str | None = None,
    age_date_column: str | None = None,
) -> dict[str, Any]:
    fecha = clean_value(row.get(date_column)) or None
    code = normalize_code(row.get(code_column))
    lab = normalize_lab(row.get(lab_column)) if lab_column else ""
    interval_value = to_int(row.get(interval_column)) if interval_column else age_from_birth(row, age_date_column or date_column)

    issues = []
    if not fecha:
        issues.append("no registra fecha de atencion")
    if code not in valid_codes:
        issues.append(f"codigo no valido o ausente ({code or '-'})")
    if required_lab and required_lab not in lab:
        issues.append(f"LAB requerido {required_lab} ausente")
    if not value_in_window(interval_value, min_value, max_value):
        issues.append(f"valor {interval_value if interval_value is not None else '-'} fuera de ventana {min_value}-{max_value} dias")

    return component_result(label, not issues, fecha, code, lab, interval_value, f"{min_value}-{max_value} dias", issues)


def interval_from_anchor_component(
    row: pd.Series,
    label: str,
    anchor_date_column: str,
    date_column: str,
    code_column: str,
    lab_column: str | None,
    valid_codes: set[str],
    min_days: int,
    max_days: int,
    *,
    required_lab: str | None = None,
) -> dict[str, Any]:
    fecha = clean_value(row.get(date_column)) or None
    code = normalize_code(row.get(code_column))
    lab = normalize_lab(row.get(lab_column)) if lab_column else ""
    interval_value = days_between(row, anchor_date_column, date_column)

    issues = []
    if not fecha:
        issues.append("no registra fecha de atencion")
    if code not in valid_codes:
        issues.append(f"codigo no valido o ausente ({code or '-'})")
    if required_lab and required_lab not in lab:
        issues.append(f"LAB requerido {required_lab} ausente")
    if not value_in_window(interval_value, min_days, max_days):
        issues.append(f"intervalo {interval_value if interval_value is not None else '-'} fuera de ventana {min_days}-{max_days} dias")

    return component_result(label, not issues, fecha, code, lab, interval_value, f"{min_days}-{max_days} dias desde primera entrega", issues)


def anemia_component(row: pd.Series) -> dict[str, Any]:
    fecha = clean_value(row.get("fec_Anemia")) or None
    code = normalize_code(row.get("Ci10_Anemia"))
    age = age_from_birth(row, "fec_Anemia")
    issues = []
    if not fecha:
        issues.append("no registra fecha de diagnostico de anemia")
    if code not in ANEMIA_CODES:
        issues.append(f"diagnostico de anemia no valido o ausente ({code or '-'})")
    if not value_in_window(age, 170, 209):
        issues.append(f"edad al diagnostico {age if age is not None else '-'} fuera de ventana 170-209 dias")
    return component_result("Diagnostico de anemia 6 meses", not issues, fecha, code, normalize_lab(row.get("Lab_Anemia")), age, "170-209 dias", issues)


def no_anemia_component(row: pd.Series) -> dict[str, Any]:
    code = normalize_code(row.get("Ci10_Anemia"))
    fecha = clean_value(row.get("fec_Anemia")) or None
    if fecha or code in ANEMIA_CODES:
        issues = ["registra diagnostico de anemia en un subindicador sin anemia"]
    else:
        issues = []
    return component_result("Sin diagnostico de anemia", not issues, fecha, code, normalize_lab(row.get("Lab_Anemia")), None, "sin D509/D649", issues)


def treatment_iron_component(row: pd.Series) -> dict[str, Any]:
    deliveries = [
        delivery(
            row,
            index,
            f"Fec_hierro{index}",
            f"Cie10_Hierro{index}",
            f"lab_hierro{index}",
            f"Intervalo{index}",
            anemia_code_column=f"Cie10_Anemia{index}",
        )
        for index in range(1, 7)
    ]
    issues = []
    first = deliveries[0]
    if first["anemia_code"] not in ANEMIA_CODES:
        issues.append("primera entrega no vinculada a diagnostico de anemia")
    if first["interval"] != 0:
        issues.append("primera entrega no figura el mismo dia del diagnostico")
    for item in deliveries[:3]:
        if not item["date"]:
            issues.append(f"no registra entrega {item['number']}")
        if item["code"] != "99199.17":
            issues.append(f"entrega {item['number']} con codigo no valido ({item['code'] or '-'})")
    registered_deliveries = [item for item in deliveries if item["date"]]
    for item in registered_deliveries[1:]:
        if not value_in_window(item["interval"], 25, 70):
            issues.append(f"entrega {item['number']} con intervalo {item['interval'] if item['interval'] is not None else '-'} fuera de 25-70 dias")
    return grouped_component_result("Hierro tratamiento", not issues, deliveries, "entregas 1-3; intervalos 25-70 dias", issues)


def preventive_iron_component(row: pd.Series) -> dict[str, Any]:
    deliveries = [
        delivery(row, index, f"Fec_hierro{index}", f"Cie10_Hierro{index}", f"lab_hierro{index}", f"Intervalo{index}")
        for index in range(1, 7)
    ]
    issues = []
    first = deliveries[0]
    second = deliveries[1]

    if not first["date"]:
        issues.append("no registra primera entrega de hierro")
    if first["code"] not in IRON_CODES:
        issues.append(f"primera entrega con codigo no valido ({first['code'] or '-'})")
    if "TA" in first["lab"]:
        issues.append("primera entrega vinculada a LAB TA")
    if first["interval"] != 0:
        issues.append("primera entrega no figura el mismo dia del primer dosaje")
    if not second["date"]:
        issues.append("no registra segunda entrega de hierro")
    if second["code"] not in IRON_CODES:
        issues.append(f"segunda entrega con codigo no valido ({second['code'] or '-'})")

    registered_deliveries = [item for item in deliveries if item["date"]]
    registered_codes = [item["code"] for item in registered_deliveries]

    if any(item["code"] not in IRON_CODES for item in registered_deliveries):
        issues.append("registra entregas con codigo de hierro no valido")

    if registered_codes and all(code == "99199.19" for code in registered_codes) and len(registered_deliveries) < 6:
        issues.append("multimicronutriente continuo requiere 6 entregas")

    if first["code"] == "99199.19" and len(registered_deliveries) < 6:
        sf_count = sum(1 for code in registered_codes if code == "99199.17")
        if sf_count < 2:
            issues.append("cambio desde multimicronutriente requiere al menos 2 entregas con 99199.17 si no completa 6 entregas")

    if first["code"] == "99199.17" and second["code"] == "99199.19" and len(registered_deliveries) < 6:
        has_later_sf = any(item["code"] == "99199.17" for item in registered_deliveries[2:])
        if not has_later_sf:
            issues.append("cambio desde 99199.17 a multimicronutriente no completa esquema valido")

    for position, item in enumerate(registered_deliveries[1:], start=2):
        if position == 6:
            continue
        interval_min = 25
        interval_max = 35 if item["code"] == "99199.19" else 70
        if not value_in_window(item["interval"], interval_min, interval_max):
            issues.append(
                f"entrega {item['number']} con intervalo {item['interval'] if item['interval'] is not None else '-'} "
                f"fuera de {interval_min}-{interval_max} dias"
            )

    return grouped_component_result("Hierro preventivo", not issues, registered_deliveries or deliveries[:2], "intervalos 25-70 dias para 99199.17 y 25-35 dias para 99199.19", issues)


def delivery(
    row: pd.Series,
    number: int,
    date_column: str,
    code_column: str,
    lab_column: str,
    interval_column: str,
    *,
    anemia_code_column: str | None = None,
) -> dict[str, Any]:
    return {
        "number": number,
        "date": clean_value(row.get(date_column)) or None,
        "code": normalize_code(row.get(code_column)),
        "lab": normalize_lab(row.get(lab_column)),
        "interval": to_int(row.get(interval_column)),
        "anemia_code": normalize_code(row.get(anemia_code_column)) if anemia_code_column else "",
    }


def component_result(
    label: str,
    complies: bool,
    fecha: str | None,
    code: str,
    lab: str,
    interval_value: int | None,
    window: str,
    issues: list[str],
) -> dict[str, Any]:
    return {
        "label": label,
        "cumple": complies,
        "estado": "cumple" if complies else "no_cumple",
        "mensaje": f"{label}: cumple." if complies else f"{label}: " + "; ".join(issues),
        "fecha": fecha,
        "codigo": code or None,
        "lab": lab or None,
        "intervalo_dias": interval_value,
        "ventana_normativa": window,
    }


def grouped_component_result(
    label: str,
    complies: bool,
    deliveries: list[dict[str, Any]],
    window: str,
    issues: list[str],
) -> dict[str, Any]:
    return {
        "label": label,
        "cumple": complies,
        "estado": "cumple" if complies else "no_cumple",
        "mensaje": f"{label}: cumple." if complies else f"{label}: " + "; ".join(issues),
        "entregas": deliveries,
        "ventana_normativa": window,
    }


def excel_component_flag(row: pd.Series, subindicator_code: str, component_key: str) -> bool | None:
    mapping = {
        "si02_01": {"hierro_4m": "Obs_hierro1", "dosaje_6m": "Obs_DH1", "ta": "Obs_TA1", "general": "Obs_General1"},
        "si02_02": {"dh_1m": "DH_1Mes", "hierro_1m": "H1_1Mes", "hierro_4m": "H2_4Mes", "dh_3m": "DH2_3Mes", "dh_6m": "DH3_6Mes", "general": "estado"},
        "si02_03": {"hierro_tratamiento": "Esta_Hierro", "ta": "Esta_TA", "dh_1m": "Esta_DH1", "dh_2m": "Esta_Dh2", "dh_3m": "Esta_DH3", "dh_6m": "Esta_Dh12m", "general": "estado"},
        "si02_04": {"hierro_preventivo": "Esta_Hierro", "ta": "Esta_TA", "dh_3m": "Esta_DH1", "dh_12m": "Esta_Dh12m", "general": "estado"},
    }
    column = mapping.get(subindicator_code, {}).get(component_key)
    if not column or column not in row:
        return None
    return bool(to_int(row.get(column)) == 1)


def subindicator_target(subindicator_code: str) -> float:
    return SUBINDICATORS[subindicator_code].target_coverage
