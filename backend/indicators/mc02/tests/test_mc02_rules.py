from __future__ import annotations

import unittest
from datetime import date, timedelta
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from indicators.mc02.denominator import is_in_denominator
from indicators.mc02.vaccines import COMPONENTS, component_detail, component_complies


def component(key: str) -> dict:
    return next(item for item in COMPONENTS if item["key"] == key)


def row_at_age(age_days: int | None, **overrides) -> tuple[pd.Series, date | None]:
    birth = date(2026, 1, 1)
    row = {
        "Fec_Nac": birth if age_days is not None else None,
        "Edad_Act(dia)": age_days,
        "Registros": 1,
        "Obs_Niño": "SIS",
        "Peso": 3000,
        "Edad_Gestacional": 39,
    }
    row.update(overrides)
    reference_date = birth + timedelta(days=age_days) if age_days is not None else None
    return pd.Series(row), reference_date


class MC02DenominatorTests(unittest.TestCase):
    def test_denominator_includes_364_days(self):
        row, reference_date = row_at_age(364)

        self.assertTrue(is_in_denominator(row, reference_date))

    def test_denominator_excludes_365_days(self):
        row, reference_date = row_at_age(365)

        self.assertFalse(is_in_denominator(row, reference_date))

    def test_denominator_keeps_empty_birth_weight_and_gestation(self):
        row, reference_date = row_at_age(120, Peso=None, Edad_Gestacional=None)

        self.assertTrue(is_in_denominator(row, reference_date))

    def test_denominator_excludes_insufficient_age(self):
        row, reference_date = row_at_age(None)

        self.assertFalse(is_in_denominator(row, reference_date))


class MC02VaccineWindowTests(unittest.TestCase):
    def test_rotavirus_210_days_without_dose_is_programmed(self):
        row, reference_date = row_at_age(210)
        detail = component_detail(row, component("rotavirus"), reference_date)

        self.assertEqual(detail["estado"], "programado")
        self.assertTrue(component_complies(row, component("rotavirus"), reference_date))

    def test_rotavirus_211_days_without_dose_is_late(self):
        row, reference_date = row_at_age(211)
        detail = component_detail(row, component("rotavirus"), reference_date)

        self.assertEqual(detail["estado"], "incumplimiento_fuera_plazo")
        self.assertFalse(detail["cumple"])
        self.assertIn("1 dosis", detail["mensaje"])

    def test_rotavirus_second_dose_after_240_days_is_late(self):
        row, reference_date = row_at_age(
            250,
            fecha_1Rot=date(2026, 3, 2),
            edad_1Rot=60,
            CIE_NEU_1Rot="90681",
            fecha_2Rot=date(2026, 9, 3),
            edad_2Rot=245,
            CIE_NEU_2Rot="90681",
        )
        detail = component_detail(row, component("rotavirus"), reference_date)

        self.assertEqual(detail["estado"], "incumplimiento_fuera_plazo")
        self.assertFalse(detail["cumple"])
        self.assertIn("240 dias", detail["mensaje"])

    def test_antipolio_120_days_without_first_dose_is_late(self):
        row, reference_date = row_at_age(120)
        detail = component_detail(row, component("antipolio"), reference_date)

        self.assertEqual(detail["estado"], "incumplimiento_fuera_plazo")
        self.assertIn("1 dosis", detail["mensaje"])


class MC02IronAndHemoglobinWindowTests(unittest.TestCase):
    def test_iron_4m_130_days_without_delivery_is_programmed(self):
        row, reference_date = row_at_age(130)
        detail = component_detail(row, component("hierro_menor_6m"), reference_date)

        self.assertEqual(detail["estado"], "programado")
        self.assertTrue(component_complies(row, component("hierro_menor_6m"), reference_date))

    def test_iron_4m_131_days_without_delivery_is_late(self):
        row, reference_date = row_at_age(131)
        detail = component_detail(row, component("hierro_menor_6m"), reference_date)

        self.assertEqual(detail["estado"], "incumplimiento_fuera_plazo")
        self.assertFalse(detail["cumple"])

    def test_iron_4m_delivery_before_window_is_late(self):
        row, reference_date = row_at_age(
            150,
            obs_suple41=1,
            fecha_1prev=date(2026, 4, 11),
            edad_1prev=100,
            CIE_Hierro_1prev="99199.17",
        )
        detail = component_detail(row, component("hierro_menor_6m"), reference_date)

        self.assertEqual(detail["estado"], "incumplimiento_fuera_plazo")
        self.assertIn("100 dias", detail["mensaje"])

    def test_hemoglobin_210_days_without_dosage_is_late(self):
        row, reference_date = row_at_age(210)
        detail = component_detail(row, component("hemoglobina"), reference_date)

        self.assertEqual(detail["estado"], "incumplimiento_fuera_plazo")
        self.assertFalse(detail["cumple"])

    def test_hemoglobin_valid_dosage_complies(self):
        row, reference_date = row_at_age(
            230,
            Obs_dh1=1,
            fecha_1DH=date(2026, 7, 1),
            edad_1DH=181,
            CIE_DH_1DH="85018",
        )
        detail = component_detail(row, component("hemoglobina"), reference_date)

        self.assertEqual(detail["estado"], "cumple")
        self.assertTrue(detail["cumple"])


if __name__ == "__main__":
    unittest.main()
