from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from indicators.si02.commitment import build_commitment_summary
from indicators.si02.config import EXPECTED_PACKAGE_CODES


def monthly(months: range, met_months: set[int]) -> list[dict]:
    return [
        {
            "month": "",
            "year": 2026,
            "month_key": f"2026_{month}",
            "denominator": 10,
            "numerator": 10 if month in met_months else 0,
            "compliant": month in met_months,
        }
        for month in months
    ]


class SI02CommitmentTests(unittest.TestCase):
    def test_may_verification_uses_different_required_months(self):
        subindicators = {
            "si02_01": {"monthly": monthly(range(1, 6), {1, 2, 3, 4})},
            "si02_02": {"monthly": monthly(range(1, 6), {5})},
            "si02_03": {"monthly": monthly(range(1, 6), {4})},
            "si02_04": {"monthly": monthly(range(1, 6), {3})},
        }

        summary = build_commitment_summary(subindicators, date(2026, 5, 31))

        self.assertEqual(summary["current_verification"], "may_2026")
        self.assertTrue(summary["global_committed"])

    def test_november_verification_requires_five_of_six_for_each_subindicator(self):
        subindicators = {
            code: {"monthly": monthly(range(6, 12), {6, 7, 8, 9, 10})}
            for code in EXPECTED_PACKAGE_CODES
        }
        subindicators["si02_04"] = {"monthly": monthly(range(6, 12), {6, 7, 8, 9})}

        summary = build_commitment_summary(subindicators, date(2026, 11, 30))

        self.assertEqual(summary["current_verification"], "nov_2026")
        self.assertFalse(summary["global_committed"])


if __name__ == "__main__":
    unittest.main()
