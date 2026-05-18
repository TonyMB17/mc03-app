"""Patient-level MC-02 evaluator facade.

The current phase evaluates the package from the operative Excel columns. This
facade keeps the public evaluator entrypoints separate from the vaccine/detail
implementation so phase 2 can swap in raw HIS attendance evaluation more
cleanly.
"""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from .components import COMPONENTS
from .engine.package import evaluate_package, is_compliant


def evaluate_patient(row: pd.Series, reference_date: date | None = None) -> dict[str, Any]:
    return evaluate_package(row, reference_date)


__all__ = ["COMPONENTS", "evaluate_package", "evaluate_patient", "is_compliant"]
