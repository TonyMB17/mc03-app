"""Commitment verification helpers for SI-02."""

from __future__ import annotations

from datetime import date
from typing import Any

from .config import EXPECTED_PACKAGE_CODES, SUBINDICATORS
from .utils import MONTH_LABELS, parse_month_key


VERIFICATION_RULES: tuple[dict[str, Any], ...] = (
    {
        "code": "may_2026",
        "label": "Primera verificacion mayo 2026",
        "start": (2026, 1),
        "end": (2026, 5),
        "required_months": {"si02_01": 4, "si02_02": 1, "si02_03": 1, "si02_04": 1},
    },
    {
        "code": "nov_2026",
        "label": "Segunda verificacion noviembre 2026",
        "start": (2026, 6),
        "end": (2026, 11),
        "required_months": {code: 5 for code in EXPECTED_PACKAGE_CODES},
    },
)


def build_commitment_summary(subindicators: dict[str, dict[str, Any]], cutoff_date: date | None = None) -> dict[str, Any]:
    verifications = [_verification_status(rule, subindicators) for rule in VERIFICATION_RULES]
    current_code = _current_verification_code(cutoff_date)

    for item in verifications:
        item["is_current"] = item["code"] == current_code

    current = next((item for item in verifications if item["is_current"]), verifications[-1])
    return {
        "current_verification": current["code"],
        "current_label": current["label"],
        "global_committed": current["committed"],
        "verifications": verifications,
    }


def current_commitment_met(subindicators: dict[str, dict[str, Any]], cutoff_date: date | None = None) -> bool:
    return bool(build_commitment_summary(subindicators, cutoff_date).get("global_committed"))


def _verification_status(rule: dict[str, Any], subindicators: dict[str, dict[str, Any]]) -> dict[str, Any]:
    start = rule["start"]
    end = rule["end"]
    details = []
    for code in EXPECTED_PACKAGE_CODES:
        summary = subindicators.get(code, {})
        monthly = summary.get("monthly", [])
        window_months = [item for item in monthly if _month_in_window(item, start, end)]
        months_met = sum(1 for item in window_months if bool(item.get("compliant")))
        required = int(rule["required_months"][code])
        months_expected = _month_distance(start, end)
        details.append(
            {
                "subindicator_code": code,
                "subindicator_name": summary.get("subindicator_name") or SUBINDICATORS[code].title,
                "target_coverage": summary.get("target_coverage") or SUBINDICATORS[code].target_coverage,
                "months_met": months_met,
                "months_with_data": len([item for item in window_months if int(item.get("denominator") or 0) > 0]),
                "months_expected": months_expected,
                "required_months": required,
                "committed": months_met >= required,
            }
        )

    return {
        "code": rule["code"],
        "label": rule["label"],
        "period": _period_label(start, end),
        "required_rule": _rule_label(rule["required_months"]),
        "committed": all(item["committed"] for item in details),
        "subindicators": details,
    }


def _current_verification_code(cutoff_date: date | None) -> str:
    if cutoff_date is None:
        return "may_2026"
    if (cutoff_date.year, cutoff_date.month) <= (2026, 5):
        return "may_2026"
    return "nov_2026"


def _month_in_window(item: dict[str, Any], start: tuple[int, int], end: tuple[int, int]) -> bool:
    parsed = parse_month_key(item.get("month_key"))
    if not parsed:
        parsed = _parse_month_label(item.get("year"), item.get("month"))
    if not parsed:
        return False
    year, month, _ = parsed
    return start <= (year, month) <= end


def _parse_month_label(year: Any, month_label: Any) -> tuple[int, int, str] | None:
    try:
        parsed_year = int(year)
    except (TypeError, ValueError):
        return None
    normalized = str(month_label or "").strip().lower()
    for month, label in MONTH_LABELS.items():
        if label == normalized:
            return parsed_year, month, label
    return None


def _month_distance(start: tuple[int, int], end: tuple[int, int]) -> int:
    return (end[0] * 12 + end[1]) - (start[0] * 12 + start[1]) + 1


def _period_label(start: tuple[int, int], end: tuple[int, int]) -> str:
    return f"{MONTH_LABELS[start[1]]} {start[0]} - {MONTH_LABELS[end[1]]} {end[0]}"


def _rule_label(required_months: dict[str, int]) -> str:
    values = set(required_months.values())
    if len(values) == 1:
        return f"{values.pop()} meses cumplidos por cada subindicador"
    return "SI-02.01 requiere 4 meses; SI-02.02, SI-02.03 y SI-02.04 requieren 1 mes"
