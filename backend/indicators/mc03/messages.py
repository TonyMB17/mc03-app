"""Human-readable MC-03 evaluation messages."""

from datetime import date, timedelta
from typing import Any

from .utils import format_date


def window_dates(birth_date: date | None, start_day: int, end_day: int) -> tuple[date | None, date | None]:
    if birth_date is None:
        return None, None
    return birth_date + timedelta(days=start_day), birth_date + timedelta(days=end_day)


def missing_attention_detail(
    label: str,
    birth_date: date | None,
    start_day: int,
    end_day: int,
    reference_date: date,
) -> dict[str, Any]:
    start_date, deadline = window_dates(birth_date, start_day, end_day)
    detail = {
        "cumple": False,
        "fecha_inicio": start_date,
        "fecha_limite": deadline,
    }

    if birth_date is None:
        return {
            **detail,
            "estado": "incumplimiento",
            "mensaje": f"No se registra atencion de {label} y no hay fecha de nacimiento para calcular la ventana normativa.",
        }

    if reference_date < start_date:
        return {
            **detail,
            "estado": "programado",
            "mensaje": f"Proximo {label}: desde {format_date(start_date)} hasta {format_date(deadline)}.",
        }

    if start_date <= reference_date <= deadline:
        return {
            **detail,
            "estado": "advertencia",
            "mensaje": f"No se registra atencion de {label}. Aun esta dentro de la ventana; fecha limite: {format_date(deadline)}.",
        }

    return {
        **detail,
        "estado": "incumplimiento",
        "mensaje": f"No se registra atencion de {label}; el plazo vencio el {format_date(deadline)}.",
    }


def attention_detail(
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
    start_date, deadline = window_dates(birth_date, start_day, end_day)

    if not has_attention:
        return missing_attention_detail(label, birth_date, start_day, end_day, reference_date)

    if not valid_code:
        actual = actual_code or "vacio"
        return {
            "cumple": False,
            "estado": "incumplimiento",
            "mensaje": f"Se registra atencion de {label}, pero con codigo {actual}; se esperaba {expected_code}.",
            "fecha_inicio": start_date,
            "fecha_limite": deadline,
        }

    if not valid_age:
        age_text = f"{actual_age} dias" if actual_age is not None else "edad no registrada"
        return {
            "cumple": False,
            "estado": "incumplimiento",
            "mensaje": f"Atencion de {label} registrada fuera de plazo ({age_text}); ventana: dia {start_day} al {end_day}.",
            "fecha_inicio": start_date,
            "fecha_limite": deadline,
        }

    if not interval_valid:
        interval_text = f"{interval} dias" if interval is not None else "intervalo no registrado"
        return {
            "cumple": False,
            "estado": "incumplimiento",
            "mensaje": f"Atencion de {label} registrada, pero no cumple el intervalo minimo de 7 dias ({interval_text}).",
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
