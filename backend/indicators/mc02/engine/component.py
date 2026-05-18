"""MC-02 component evaluation engine."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pandas as pd

from ..components import COMPONENTS
from ..config import REGLAS_NEGOCIO
from ..messages import build_component_message
from ..utils import clean_value, flag_is_true, format_short_date, has_value, to_date, to_int


def birth_date(row: pd.Series) -> date | None:
    return to_date(row.get("Fec_Nac"))


def date_from_birth(row: pd.Series, age_days: int | None) -> date | None:
    base_birth_date = birth_date(row)
    if base_birth_date is None or age_days is None:
        return None
    return base_birth_date + timedelta(days=age_days)


def current_age_days(row: pd.Series, reference_date: date | None = None) -> int | None:
    base_birth_date = birth_date(row)
    if base_birth_date is not None and reference_date is not None:
        return max((reference_date - base_birth_date).days, 0)
    return to_int(row.get("Edad_Act(dia)"))


def required_count(window_range: dict[str, Any] | None) -> int:
    if window_range is None:
        return 1
    required = window_range.get("dosis_requeridas", window_range.get("entregas_requeridas", 1))
    return int(required)


def required_amount(window_range: dict[str, Any] | None) -> bool:
    return required_count(window_range) > 0


def max_required_count(component: dict[str, Any]) -> int:
    rule = REGLAS_NEGOCIO["VENTANAS_ATENCION"].get(component["window"], {})
    return max((required_count(item) for item in rule.get("rangos", [])), default=0)


def matched_window_range(row: pd.Series, component: dict[str, str], reference_date: date | None = None) -> dict[str, Any] | None:
    rule = REGLAS_NEGOCIO["VENTANAS_ATENCION"].get(component["window"])
    current_age = current_age_days(row, reference_date)
    if not rule or current_age is None:
        return None
    for item in rule.get("rangos", []):
        if item["edad_min"] <= current_age <= item["edad_max"]:
            return item
    return None


def component_required(row: pd.Series, component: dict[str, str], reference_date: date | None = None) -> bool:
    matched_range = matched_window_range(row, component, reference_date)
    return bool(matched_range is not None and required_amount(matched_range))


def next_required_range(row: pd.Series, component: dict[str, str], reference_date: date | None = None) -> dict[str, Any] | None:
    rule = REGLAS_NEGOCIO["VENTANAS_ATENCION"].get(component["window"])
    current_age = current_age_days(row, reference_date)
    if not rule:
        return None

    required_ranges = [item for item in rule.get("rangos", []) if required_amount(item)]
    if current_age is None:
        return required_ranges[0] if required_ranges else None

    for item in required_ranges:
        if current_age <= item["edad_max"]:
            return item
    return required_ranges[-1] if required_ranges else None


def active_or_next_range(row: pd.Series, component: dict[str, str], reference_date: date | None = None) -> dict[str, Any] | None:
    matched_range = matched_window_range(row, component, reference_date)
    if matched_range is not None:
        return matched_range
    return next_required_range(row, component, reference_date)


def window_text(row: pd.Series, component: dict[str, str], reference_date: date | None = None) -> str | None:
    rule = REGLAS_NEGOCIO["VENTANAS_ATENCION"].get(component["window"])
    if not rule:
        return None

    current_age = current_age_days(row, reference_date)
    matched_range = matched_window_range(row, component, reference_date)
    evaluation_range = active_or_next_range(row, component, reference_date)
    if matched_range is not None and not required_amount(matched_range):
        evaluation_range = next_required_range(row, component, reference_date)

    pieces = []
    if matched_range:
        pieces.append(f"Edad actual {current_age} dias: {matched_range['mensaje']}")
    elif current_age is not None:
        pieces.append(f"Edad actual {current_age} dias fuera de rangos configurados.")

    if evaluation_range:
        start_date = date_from_birth(row, evaluation_range.get("edad_min"))
        limit_date = date_from_birth(row, evaluation_range.get("edad_max"))
        if start_date and limit_date:
            pieces.append(f"Periodo de seguimiento: {format_short_date(start_date)} a {format_short_date(limit_date)}.")

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


def dose_date(row: pd.Series, dose: dict[str, str]) -> date | None:
    return to_date(row.get(dose["date"]))


def dose_age(row: pd.Series, dose: dict[str, str]) -> int | None:
    age = to_int(row.get(dose["age"]))
    date_value = dose_date(row, dose)
    base_birth_date = birth_date(row)
    if age is None and date_value and base_birth_date:
        return max((date_value - base_birth_date).days, 0)
    return age


def dose_registered(row: pd.Series, dose: dict[str, str]) -> bool:
    return has_value(row.get(dose["date"])) or has_value(row.get(dose["code"]))


def dose_age_rule(component: dict[str, Any], dose_number: int) -> dict[str, Any]:
    rule = REGLAS_NEGOCIO["VENTANAS_ATENCION"].get(component["window"], {})
    age_rules = rule.get("edad_dosis", {})
    return age_rules.get(dose_number) or age_rules.get(str(dose_number)) or {}


def dose_age_window(row: pd.Series, component: dict[str, Any], dose_number: int) -> tuple[date | None, date | None]:
    age_rule = dose_age_rule(component, dose_number)
    return date_from_birth(row, age_rule.get("min_dias")), date_from_birth(row, age_rule.get("max_dias"))


def dose_interval_days(row: pd.Series, current_dose: dict[str, str], previous_dose: dict[str, str]) -> int | None:
    current_age = dose_age(row, current_dose)
    previous_age = dose_age(row, previous_dose)
    if current_age is not None and previous_age is not None:
        return current_age - previous_age

    current_date = dose_date(row, current_dose)
    previous_date = dose_date(row, previous_dose)
    if current_date and previous_date:
        return (current_date - previous_date).days
    return None


def dose_interval_window(row: pd.Series, previous_dose: dict[str, str], interval: dict[str, Any]) -> tuple[date | None, date | None]:
    min_days = interval.get("min_dias")
    if min_days is None:
        return None, None

    previous_date = dose_date(row, previous_dose)
    if previous_date is not None:
        start_date = previous_date + timedelta(days=int(min_days))
        end_date = previous_date + timedelta(days=int(interval["max_dias"])) if interval.get("max_dias") is not None else None
        return start_date, end_date

    base_birth_date = birth_date(row)
    previous_age = dose_age(row, previous_dose)
    if base_birth_date is None or previous_age is None:
        return None, None

    start_date = base_birth_date + timedelta(days=previous_age + int(min_days))
    end_date = base_birth_date + timedelta(days=previous_age + int(interval["max_dias"])) if interval.get("max_dias") is not None else None
    return start_date, end_date


def dose_evaluations(row: pd.Series, component: dict[str, Any], reference_date: date | None = None) -> list[dict[str, Any]]:
    component_doses = component.get("doses", [])
    if not component_doses:
        return []

    rule = REGLAS_NEGOCIO["VENTANAS_ATENCION"].get(component["window"], {})
    interval = rule.get("intervalo_dosis", {})
    matched_range = matched_window_range(row, component, reference_date)
    required_range = matched_range if matched_range is not None else next_required_range(row, component, reference_date)
    required_count_value = min(required_count(required_range), len(component_doses))
    evaluations: list[dict[str, Any]] = []
    current_age = current_age_days(row, reference_date)

    for index, dose in enumerate(component_doses):
        dose_number = index + 1
        registered = dose_registered(row, dose)
        age = dose_age(row, dose)
        required_for_age = dose_number <= required_count_value
        status = "registrada" if registered else "no_requerida"
        complies = True
        messages: list[str] = []
        interval_start: date | None = None
        interval_end: date | None = None
        age_rule = dose_age_rule(component, dose_number)
        age_window_start, age_window_end = dose_age_window(row, component, dose_number)

        if age_window_start or age_window_end:
            interval_start = age_window_start
            interval_end = age_window_end

        if required_for_age and not registered:
            status = "no_registrada"
            complies = False
            max_age = age_rule.get("max_dias")
            if max_age is not None and current_age is not None and current_age > int(max_age):
                status = "fuera_plazo"
                messages.append(f"No se registra {dose['label']} requerida; ventana valida hasta los {max_age} dias.")
            else:
                messages.append(f"No se registra {dose['label']} requerida.")

        if registered and age_rule.get("min_dias") is not None and age is not None and age < int(age_rule["min_dias"]):
            status = "fuera_plazo"
            complies = False
            messages.append(f"{dose['label']} aplicada a los {age} dias; la edad minima es {age_rule['min_dias']} dias.")

        if registered and age_rule.get("max_dias") is not None and age is not None and age > int(age_rule["max_dias"]):
            status = "fuera_plazo"
            complies = False
            messages.append(f"{dose['label']} aplicada a los {age} dias; la edad maxima es {age_rule['max_dias']} dias.")

        if registered and interval.get("max_edad_dias") is not None and age is not None and age > int(interval["max_edad_dias"]):
            status = "fuera_plazo"
            complies = False
            messages.append(f"{dose['label']} aplicada a los {age} dias; la edad maxima es {interval['max_edad_dias']} dias.")

        if registered and index > 0:
            previous_dose = component_doses[index - 1]
            previous_registered = dose_registered(row, previous_dose)
            interval_days = dose_interval_days(row, dose, previous_dose) if previous_registered else None
            dose_interval_start, dose_interval_end = dose_interval_window(row, previous_dose, interval) if previous_registered else (None, None)
            interval_start = dose_interval_start or interval_start
            interval_end = dose_interval_end or interval_end
            interval_text = ""
            if interval_start and interval_end:
                interval_text = f" Ventana valida: {format_short_date(interval_start)} a {format_short_date(interval_end)}."
            elif interval_start:
                interval_text = f" Ventana valida desde {format_short_date(interval_start)}."

            if not previous_registered:
                status = "fuera_plazo"
                complies = False
                messages.append(f"{dose['label']} no puede validarse porque falta la dosis previa.")
            elif interval_days is not None:
                if interval_days < int(interval.get("min_dias", 0)):
                    status = "fuera_plazo"
                    complies = False
                    messages.append(f"Intervalo de {interval_days} dias desde la dosis previa; minimo {interval['min_dias']} dias.{interval_text}")
                if interval.get("max_dias") is not None and interval_days > int(interval["max_dias"]):
                    status = "fuera_plazo"
                    complies = False
                    messages.append(f"Intervalo de {interval_days} dias desde la dosis previa; maximo {interval['max_dias']} dias.{interval_text}")

        if required_for_age and not registered and index > 0:
            previous_dose = component_doses[index - 1]
            if dose_registered(row, previous_dose):
                interval_start, interval_end = dose_interval_window(row, previous_dose, interval)
                if interval_end and reference_date and reference_date > interval_end:
                    status = "fuera_plazo"
                    messages.append(f"No se registra {dose['label']} requerida; ventana valida hasta {format_short_date(interval_end)}.")

        if status == "fuera_plazo" and interval_start and interval_end and not any("Ventana valida" in message for message in messages):
            messages.append(f"Ventana valida: {format_short_date(interval_start)} a {format_short_date(interval_end)}.")

        if registered and complies:
            status = "registrada" if required_for_age else "registrada_no_exigible"

        evaluations.append(
            {
                "label": dose["label"],
                "registrada": registered,
                "requerida": required_for_age,
                "cumple": complies,
                "estado": status,
                "tipo": "dosis",
                "ventana_inicio": interval_start,
                "ventana_fin": interval_end,
                "motivo": " ".join(messages) or (
                    "Dosis registrada; aun no corresponde exigirla por edad actual."
                    if registered and not required_for_age
                    else ("Dosis valida." if registered else "Aun no requerida.")
                ),
            }
        )

    return evaluations


def dose_issues(row: pd.Series, component: dict[str, Any], reference_date: date | None = None) -> list[dict[str, Any]]:
    return [dose for dose in dose_evaluations(row, component, reference_date) if not dose["cumple"]]


def attention_registered(row: pd.Series, component: dict[str, Any]) -> bool:
    if component.get("deliveries") and primary_delivery_detail(row, component):
        return True
    return has_value(row.get(component["date"])) or has_value(row.get(component["code"]))


def attention_age(row: pd.Series, component: dict[str, Any]) -> int | None:
    delivery = primary_delivery_detail(row, component) if component.get("deliveries") else None
    if delivery:
        return delivery.get("edad_atencion_dias")

    age = to_int(row.get(component["age"]))
    date_value = to_date(row.get(component["date"]))
    base_birth_date = birth_date(row)
    if age is None and date_value and base_birth_date:
        return max((date_value - base_birth_date).days, 0)
    return age


def attention_window(row: pd.Series, component: dict[str, Any]) -> tuple[date | None, date | None]:
    rule = REGLAS_NEGOCIO["VENTANAS_ATENCION"].get(component["window"], {})
    window = rule.get("ventana_atencion")
    if not window:
        return None, None
    return date_from_birth(row, window.get("inicio_dia")), date_from_birth(row, window.get("fin_dia"))


def attention_issues(row: pd.Series, component: dict[str, Any]) -> list[dict[str, Any]]:
    if component.get("doses") or component.get("deliveries") or not attention_registered(row, component):
        return []

    rule = REGLAS_NEGOCIO["VENTANAS_ATENCION"].get(component["window"], {})
    window = rule.get("ventana_atencion")
    age = attention_age(row, component)
    if not window or age is None:
        return []

    start_age = int(window["inicio_dia"])
    end_age = int(window["fin_dia"])
    if start_age <= age <= end_age:
        return []

    start_date, end_date = attention_window(row, component)
    return [
        {
            "label": component["label"],
            "estado": "fuera_plazo",
            "tipo": "atencion",
            "motivo": f"Atencion registrada a los {age} dias; ventana valida de {start_age} a {end_age} dias.",
            "ventana_inicio": start_date,
            "ventana_fin": end_date,
        }
    ]


def required_doses_complete(row: pd.Series, component: dict[str, Any], reference_date: date | None = None) -> bool | None:
    if not component.get("doses"):
        return None

    evaluations = dose_evaluations(row, component, reference_date)
    required_doses = [dose for dose in evaluations if dose["requerida"]]
    if not required_doses:
        return None
    return all(dose["registrada"] and dose["cumple"] for dose in required_doses)


def completed_ahead_of_window(row: pd.Series, component: dict[str, Any], reference_date: date | None = None) -> bool:
    if attention_based_component(component) and component_has_trace(row, component) and not attention_issues(row, component):
        return True

    if (
        flag_is_true(row.get(component["flag"]))
        and component_has_trace(row, component)
        and not dose_issues(row, component, reference_date)
        and not attention_issues(row, component)
        and not delivery_issues(row, component)
    ):
        return True

    max_required = max_required_count(component)
    if max_required <= 0:
        return False

    valid_registered = [
        dose
        for dose in dose_evaluations(row, component, reference_date)
        if dose["registrada"] and dose["cumple"]
    ]
    return len(valid_registered) >= max_required


def component_has_trace(row: pd.Series, component: dict[str, Any]) -> bool:
    if component.get("doses"):
        return any(dose_registered(row, dose) for dose in component["doses"])
    if component.get("deliveries"):
        return any(delivery_registered(row, delivery) for delivery in component["deliveries"])
    return has_value(row.get(component["date"])) or has_value(row.get(component["code"]))


def attention_based_component(component: dict[str, Any]) -> bool:
    rule = REGLAS_NEGOCIO["VENTANAS_ATENCION"].get(component["window"], {})
    return bool(not component.get("doses") and not component.get("deliveries") and rule.get("ventana_atencion"))


def dose_details(row: pd.Series, component: dict[str, Any], reference_date: date | None = None) -> list[dict[str, Any]]:
    doses: list[dict[str, Any]] = []
    evaluations = dose_evaluations(row, component, reference_date)
    for dose, evaluation in zip(component.get("doses", []), evaluations):
        has_date = has_value(row.get(dose["date"]))
        has_code = has_value(row.get(dose["code"]))
        if not has_date and not has_code and not evaluation["requerida"]:
            continue
        doses.append(
            {
                "label": dose["label"],
                "fecha": clean_value(row.get(dose["date"])) or None,
                "edad_atencion_dias": dose_age(row, dose),
                "codigo": clean_value(row.get(dose["code"])) or None,
                "lab": clean_value(row.get(dose.get("lab"))) or None,
                "lote": clean_value(row.get(dose.get("lote"))) or None,
                "establecimiento_atencion": clean_value(row.get(dose.get("facility"))) or None,
                "registrada": evaluation["registrada"],
                "requerida": evaluation["requerida"],
                "cumple": evaluation["cumple"],
                "estado": evaluation["estado"],
                "motivo": evaluation["motivo"],
                "ventana_inicio": evaluation["ventana_inicio"],
                "ventana_fin": evaluation["ventana_fin"],
            }
        )
    return doses


def delivery_registered(row: pd.Series, delivery: dict[str, str]) -> bool:
    return has_value(row.get(delivery["date"])) or has_value(row.get(delivery["code"]))


def delivery_age(row: pd.Series, delivery: dict[str, str]) -> int | None:
    age = to_int(row.get(delivery["age"]))
    delivery_date = to_date(row.get(delivery["date"]))
    base_birth_date = birth_date(row)
    if age is None and delivery_date and base_birth_date:
        return max((delivery_date - base_birth_date).days, 0)
    return age


def delivery_details(row: pd.Series, component: dict[str, Any]) -> list[dict[str, Any]]:
    deliveries: list[dict[str, Any]] = []
    for delivery in component.get("deliveries", []):
        if not delivery_registered(row, delivery):
            continue
        deliveries.append(
            {
                "label": delivery["label"],
                "tipo": delivery.get("kind") or component.get("delivery_kind"),
                "fecha": clean_value(row.get(delivery["date"])) or None,
                "edad_atencion_dias": delivery_age(row, delivery),
                "codigo": clean_value(row.get(delivery["code"])) or None,
                "codigo_anemia": clean_value(row.get(delivery.get("anemia_code"))) or None,
                "lab": clean_value(row.get(delivery.get("lab"))) or None,
                "lote": clean_value(row.get(delivery.get("lote"))) or None,
                "intervalo_dias": to_int(row.get(delivery.get("interval"))) if delivery.get("interval") else None,
                "establecimiento_atencion": clean_value(row.get(delivery.get("facility"))) or None,
            }
        )
    return deliveries


def delivery_in_attention_window(delivery: dict[str, Any], component: dict[str, Any]) -> bool:
    window = REGLAS_NEGOCIO["VENTANAS_ATENCION"].get(component["window"], {}).get("ventana_atencion")
    age = delivery.get("edad_atencion_dias")
    if not window or age is None:
        return False
    return int(window["inicio_dia"]) <= int(age) <= int(window["fin_dia"])


def primary_delivery_detail(row: pd.Series, component: dict[str, Any]) -> dict[str, Any] | None:
    deliveries = delivery_details(row, component)
    if not deliveries:
        return None

    valid_deliveries = [delivery for delivery in deliveries if delivery_in_attention_window(delivery, component)]
    return valid_deliveries[0] if valid_deliveries else deliveries[0]


def delivery_issues(row: pd.Series, component: dict[str, Any]) -> list[dict[str, Any]]:
    if component.get("doses") or not component.get("deliveries"):
        return []

    window = REGLAS_NEGOCIO["VENTANAS_ATENCION"].get(component["window"], {}).get("ventana_atencion")
    deliveries = delivery_details(row, component)
    if not window or not deliveries:
        return []
    if any(delivery_in_attention_window(delivery, component) for delivery in deliveries):
        return []

    delivery = deliveries[0]
    age = delivery.get("edad_atencion_dias")
    if age is None:
        return []

    start_date, end_date = attention_window(row, component)
    return [
        {
            "label": delivery["label"],
            "estado": "fuera_plazo",
            "tipo": "entrega",
            "motivo": f"{delivery['label']} registrada a los {age} dias; ventana valida de {window['inicio_dia']} a {window['fin_dia']} dias.",
            "ventana_inicio": start_date,
            "ventana_fin": end_date,
        }
    ]


def required_deliveries_complete(row: pd.Series, component: dict[str, Any], reference_date: date | None = None) -> bool | None:
    if not component.get("deliveries"):
        return None

    window = REGLAS_NEGOCIO["VENTANAS_ATENCION"].get(component["window"], {}).get("ventana_atencion")
    if not window:
        return None

    required_range = matched_window_range(row, component, reference_date)
    if required_range is None:
        required_range = next_required_range(row, component, reference_date)
    if not required_amount(required_range):
        return None

    return any(delivery_in_attention_window(delivery, component) for delivery in delivery_details(row, component))


def component_complies(row: pd.Series, component: dict[str, str], reference_date: date | None = None) -> bool:
    if not component_required(row, component, reference_date):
        return (
            not dose_issues(row, component, reference_date)
            and not attention_issues(row, component)
            and not delivery_issues(row, component)
        )
    required_complete = required_doses_complete(row, component, reference_date)
    if required_complete is not None:
        return required_complete and not dose_issues(row, component, reference_date)
    delivery_complete = required_deliveries_complete(row, component, reference_date)
    if delivery_complete is not None:
        return (delivery_complete or flag_is_true(row.get(component["flag"]))) and not delivery_issues(row, component)
    if attention_based_component(component):
        return attention_registered(row, component) and not attention_issues(row, component)
    return flag_is_true(row.get(component["flag"])) and not attention_issues(row, component)


def is_compliant(row: pd.Series, reference_date: date | None = None) -> bool:
    return all(component_complies(row, component, reference_date) for component in COMPONENTS)


def component_detail(row: pd.Series, component: dict[str, Any], reference_date: date | None = None) -> dict[str, Any]:
    current_age = current_age_days(row, reference_date)
    evaluation_range = active_or_next_range(row, component, reference_date)
    required = component_required(row, component, reference_date)
    complies = component_complies(row, component, reference_date)
    if not required:
        evaluation_range = next_required_range(row, component, reference_date)
    obs_text = clean_value(row.get(component["obs"]))
    has_attention = attention_registered(row, component)
    message_window_text = window_text(row, component, reference_date)
    issues = [*dose_issues(row, component, reference_date), *attention_issues(row, component), *delivery_issues(row, component)]
    issue_text = " ".join(f"{issue['label']}: {issue['motivo']}" for issue in issues)
    has_late_issue = any(issue.get("estado") == "fuera_plazo" for issue in issues)
    has_late_dose = any(issue.get("estado") == "fuera_plazo" and issue.get("tipo") == "dosis" for issue in issues)
    age = attention_age(row, component)
    attention_start_date, attention_limit_date = attention_window(row, component)
    start_date = attention_start_date or (date_from_birth(row, evaluation_range.get("edad_min")) if evaluation_range else None)
    limit_date = attention_limit_date or (date_from_birth(row, evaluation_range.get("edad_max")) if evaluation_range else None)
    issue_limit_dates = [issue["ventana_fin"] for issue in issues if issue.get("ventana_fin")]
    if issue_limit_dates and not any(issue.get("estado") == "fuera_plazo" for issue in issues):
        limit_date = min(issue_limit_dates)
    attention_window_rule = REGLAS_NEGOCIO["VENTANAS_ATENCION"].get(component["window"], {}).get("ventana_atencion")
    deadline_age = attention_window_rule.get("fin_dia") if attention_window_rule else (evaluation_range.get("edad_max") if evaluation_range else None)
    after_deadline = bool(deadline_age is not None and current_age is not None and current_age > int(deadline_age))

    completed_ahead = not required and completed_ahead_of_window(row, component, reference_date)
    dose_detail_items = dose_details(row, component, reference_date)
    delivery_detail_items = delivery_details(row, component)
    primary_delivery = primary_delivery_detail(row, component)
    estado, mensaje = build_component_message(
        component=component,
        completed_ahead=completed_ahead,
        required=required,
        complies=complies,
        has_attention=has_attention,
        after_deadline=after_deadline,
        has_late_issue=has_late_issue,
        has_late_dose=has_late_dose,
        issue_text=issue_text,
        obs_text=obs_text,
        limit_date=limit_date,
        message_window_text=message_window_text,
        current_age=current_age,
        next_required_range=next_required_range(row, component, reference_date),
        date_from_birth=lambda age_days: date_from_birth(row, age_days),
    )

    return {
        "codigo": (primary_delivery.get("codigo") if primary_delivery else clean_value(row.get(component["code"]))) or "",
        "fecha": (primary_delivery.get("fecha") if primary_delivery else clean_value(row.get(component["date"]))) or None,
        "resultado": obs_text or None,
        "edad_atencion_dias": age,
        "cumple": complies,
        "estado": estado,
        "mensaje": mensaje,
        "establecimiento_atencion": (primary_delivery.get("establecimiento_atencion") if primary_delivery else clean_value(row.get(component["facility"]))) or None,
        "profesional": clean_value(row.get(component.get("professional"))) or "No disponible en Excel",
        "lab": (primary_delivery.get("lab") if primary_delivery else clean_value(row.get(component["lab"]))) or None,
        "lote": (primary_delivery.get("lote") if primary_delivery else clean_value(row.get(component["lote"]))) or None,
        "ventana_normativa": message_window_text,
        "fecha_inicio": start_date,
        "fecha_limite": limit_date,
        "dosis": dose_detail_items,
        "dosis_registradas": sum(1 for dose in dose_detail_items if dose["registrada"]),
        "dosis_evaluadas": len(dose_detail_items),
        "entregas": delivery_detail_items,
        "tipo_atencion": component.get("delivery_kind"),
    }


def evaluate_package(row: pd.Series, reference_date: date | None = None) -> dict[str, Any]:
    details = {component["key"]: component_detail(row, component, reference_date) for component in COMPONENTS}
    reasons = [detail["mensaje"] for detail in details.values() if not detail["cumple"]]
    return {"complete": all(detail["cumple"] for detail in details.values()), "details": details, "reasons": reasons}
