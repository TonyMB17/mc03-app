"""Backward-compatible MC-02 evaluator exports.

The vaccine component definitions now live in ``components/vaccines.py`` and
the shared evaluator lives in ``engine/component.py``. This module remains as a
stable import surface for older tests or callers during the migration.
"""

from .components import COMPONENTS
from .components.vaccines import VACCINE_COMPONENTS, VACCINE_WINDOWS
from .engine.component import (
    active_or_next_range,
    attention_age,
    attention_issues,
    attention_registered,
    attention_window,
    birth_date,
    component_complies,
    component_detail,
    component_required,
    completed_ahead_of_window,
    current_age_days,
    date_from_birth,
    delivery_details,
    delivery_registered,
    dose_details,
    dose_evaluations,
    dose_issues,
    evaluate_package,
    is_compliant,
    matched_window_range,
    next_required_range,
    required_doses_complete,
    window_text,
)

__all__ = [
    "COMPONENTS",
    "VACCINE_COMPONENTS",
    "VACCINE_WINDOWS",
    "active_or_next_range",
    "attention_age",
    "attention_issues",
    "attention_registered",
    "attention_window",
    "birth_date",
    "component_complies",
    "component_detail",
    "component_required",
    "completed_ahead_of_window",
    "current_age_days",
    "date_from_birth",
    "delivery_details",
    "delivery_registered",
    "dose_details",
    "dose_evaluations",
    "dose_issues",
    "evaluate_package",
    "is_compliant",
    "matched_window_range",
    "next_required_range",
    "required_doses_complete",
    "window_text",
]
