"""User-facing MC-02 component message composition."""

from __future__ import annotations

from datetime import date
from typing import Any, Callable

from .utils import format_short_date


def build_component_message(
    *,
    component: dict[str, Any],
    completed_ahead: bool,
    required: bool,
    complies: bool,
    has_attention: bool,
    after_deadline: bool,
    has_late_issue: bool,
    has_late_dose: bool,
    issue_text: str,
    obs_text: str,
    limit_date: date | None,
    message_window_text: str | None,
    current_age: int | None,
    next_required_range: dict[str, Any] | None,
    date_from_birth: Callable[[int | None], date | None],
) -> tuple[str, str]:
    if completed_ahead:
        if component["key"] == "hemoglobina":
            return "cumple", f"{component['label']} ya cuenta con un dosaje valido para el indicador."
        if component.get("deliveries"):
            return "cumple", f"{component['label']} ya cuenta con las entregas completas y validas para el indicador."
        return "cumple", f"{component['label']} ya cuenta con las dosis completas y validas para el indicador."

    if not required:
        mensaje = f"{component['label']} aun no es exigible para la edad actual."
        if next_required_range and current_age is not None and current_age < int(next_required_range["edad_min"]):
            next_start = date_from_birth(next_required_range["edad_min"])
            if next_start:
                mensaje = f"{mensaje} Proximo control desde {format_short_date(next_start)}."
        if message_window_text and not has_late_dose:
            mensaje = f"{mensaje} {message_window_text}"
        return "programado", mensaje

    if complies:
        return "cumple", f"{component['label']} cumple segun la evaluacion del Excel operativo."

    if has_attention:
        estado = "incumplimiento_fuera_plazo" if after_deadline or has_late_issue else "pendiente_en_plazo"
        mensaje = issue_text or obs_text or f"{component['label']} registra atencion, pero no cumple el criterio del indicador."
        if has_late_dose:
            mensaje = f"Incumplimiento por dosis fuera de plazo. {mensaje}"
        elif has_late_issue:
            mensaje = f"Incumplimiento por atencion fuera de plazo. {mensaje}"
        elif after_deadline and limit_date:
            mensaje = f"Incumplimiento por atencion fuera de plazo. Fecha limite: {format_short_date(limit_date)}. {mensaje}"
        elif limit_date:
            mensaje = f"Pendiente dentro de plazo. Fecha limite: {format_short_date(limit_date)}. {mensaje}"
        if message_window_text and not has_late_dose:
            mensaje = f"{mensaje} {message_window_text}"
        return estado, mensaje

    estado = "incumplimiento_fuera_plazo" if after_deadline or has_late_issue else "pendiente_en_plazo"
    if after_deadline and limit_date:
        mensaje = issue_text or f"No se registra atencion para {component['label']}."
        mensaje = f"{mensaje} Incumplimiento fuera de plazo; fecha limite: {format_short_date(limit_date)}."
    elif has_late_issue:
        mensaje = issue_text or f"{component['label']} no cumple la ventana normativa."
    elif limit_date:
        mensaje = issue_text or f"No se registra atencion para {component['label']}."
        mensaje = f"{mensaje} Pendiente dentro de plazo; fecha limite: {format_short_date(limit_date)}."
    else:
        mensaje = obs_text or f"No se registra atencion para {component['label']}."
    if message_window_text:
        mensaje = f"{mensaje} {message_window_text}"
    return estado, mensaje
