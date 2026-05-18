from __future__ import annotations

import unittest
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
import sys
from types import SimpleNamespace

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from indicators.mc02.denominator import is_in_denominator
from indicators.mc02.components import COMPONENTS
from indicators.mc02.dashboard import omiso_from_row
from indicators.mc02.engine.component import component_detail, component_complies
from indicators.mc02.engine.package import evaluate_package
from indicators.mc02.excel_loader import operational_columns, required_columns
from indicators.mc02.iron import anemia_alerts, has_anemia_diagnosis
from indicators.mc02.storage import UPLOAD_STATUS_FAILED, fail_upload, report_summary_from_rows, search_result_from_record


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


class MC02ExcelLoaderTests(unittest.TestCase):
    def test_operational_columns_include_required_and_distributed_trace_columns(self):
        operational = set(operational_columns())

        self.assertTrue(set(required_columns()).issubset(operational))
        self.assertIn("fecha_4prev", operational)
        self.assertIn("Lab", operational)
        self.assertIn("fecha_1DH", operational)
        self.assertIn("EESS_Ate_1DH", operational)


class MC02VaccineWindowTests(unittest.TestCase):
    def test_package_complete_matches_component_details(self):
        row, reference_date = row_at_age(211)
        package = evaluate_package(row, reference_date)

        self.assertEqual(package["complete"], all(detail["cumple"] for detail in package["details"].values()))

    def test_missing_required_doses_are_not_counted_as_registered(self):
        row, reference_date = row_at_age(218)
        detail = component_detail(row, component("neumococo"), reference_date)

        self.assertEqual(detail["codigo"], "")
        self.assertEqual(detail["dosis_registradas"], 0)
        self.assertEqual(len(detail["dosis"]), 2)
        self.assertTrue(all(not dose["registrada"] for dose in detail["dosis"]))

    def test_rotavirus_189_days_without_dose_is_programmed(self):
        row, reference_date = row_at_age(189)
        detail = component_detail(row, component("rotavirus"), reference_date)

        self.assertEqual(detail["estado"], "programado")
        self.assertTrue(component_complies(row, component("rotavirus"), reference_date))

    def test_rotavirus_200_days_without_dose_is_pending(self):
        row, reference_date = row_at_age(200)
        detail = component_detail(row, component("rotavirus"), reference_date)

        self.assertEqual(detail["estado"], "pendiente_en_plazo")
        self.assertFalse(detail["cumple"])
        self.assertEqual(detail["dosis_registradas"], 0)

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


class MC02DashboardOmisosTests(unittest.TestCase):
    def test_omiso_lists_all_failed_components_with_labeled_reasons(self):
        row, reference_date = row_at_age(211)
        package = evaluate_package(row, reference_date)
        omiso = omiso_from_row(row, package)

        self.assertIn("Vacuna neumococo", omiso["components_observed"])
        self.assertIn("Vacuna rotavirus", omiso["components_observed"])
        self.assertIn("Vacuna neumococo:", omiso["reason"])
        self.assertIn("Vacuna rotavirus:", omiso["reason"])
        self.assertIn("\n", omiso["reason"])


class MC02StorageSearchTests(unittest.TestCase):
    def test_search_result_from_persisted_record_matches_api_shape(self):
        record = SimpleNamespace(
            dni="94429279",
            cnv="94429279",
            first_names="KAYARA",
            paternal_surname="GUILLEN",
            maternal_surname="NOVOA",
            birth_date=date(2025, 10, 27),
            raw_selected_data={"Peso": 3410, "Edad_Gestacional": 40},
            province="ABANCAY",
            microred="MICAELA BASTIDAS",
            facility_code="2672",
            facility="TACMARA",
            clinical_alerts=[],
            package_complete=True,
        )
        components = [
            SimpleNamespace(
                component_key="hemoglobina",
                details={
                    "codigo": "85018.01",
                    "fecha": "2026-05-04",
                    "edad_atencion_dias": 189,
                    "cumple": True,
                    "estado": "cumple",
                    "mensaje": None,
                    "fecha_inicio": "2026-04-15",
                    "fecha_limite": "2026-05-24",
                },
                code="85018.01",
                attention_date=date(2026, 5, 4),
                result_text="Cumple",
                attention_age_days=189,
                complies=True,
                status="cumple",
                message=None,
                attention_facility="TACMARA",
                professional=None,
                lab=None,
                lot=None,
            )
        ]

        result = search_result_from_record(record, components)

        self.assertEqual(result["personal"]["afi_DNI"], "94429279")
        self.assertEqual(result["personal"]["peso"], 3410)
        self.assertEqual(result["personal"]["edadGEst"], 40)
        self.assertEqual(result["vacunas"]["hemoglobina"]["codigo"], "85018.01")
        self.assertEqual(result["tamizaje"]["estado"], "cumple")
        self.assertTrue(result["paquete_completo"])

    def test_search_result_normalizes_empty_component_code_for_schema(self):
        record = SimpleNamespace(
            dni="94405414",
            cnv=None,
            first_names=None,
            paternal_surname=None,
            maternal_surname=None,
            birth_date=None,
            raw_selected_data={},
            province="ABANCAY",
            microred=None,
            facility_code=None,
            facility=None,
            clinical_alerts=[],
            package_complete=False,
        )
        components = [
            SimpleNamespace(
                component_key="neumococo",
                details={"codigo": None, "cumple": False, "estado": "incumplimiento_fuera_plazo"},
                code=None,
                attention_date=None,
                result_text=None,
                attention_age_days=None,
                complies=False,
                status="incumplimiento_fuera_plazo",
                message="No se registra dosis.",
                attention_facility=None,
                professional=None,
                lab=None,
                lot=None,
            )
        ]

        result = search_result_from_record(record, components)

        self.assertEqual(result["vacunas"]["neumococo"]["codigo"], "")
        self.assertEqual(result["vacunas"]["neumococo"]["dosis"], [])
        self.assertEqual(result["vacunas"]["neumococo"]["entregas"], [])


class MC02StorageReportTests(unittest.TestCase):
    def test_report_summary_from_rows_recalculates_target_status(self):
        upload = SimpleNamespace(cutoff_date=date(2026, 5, 11))
        dashboard_rows = [
            SimpleNamespace(
                period_label="mayo",
                period_year=2026,
                period_month=5,
                in_verification_period=True,
                denominator=10,
                numerator=8,
                coverage=Decimal("80.00"),
            )
        ]
        omissions = [
            SimpleNamespace(
                export_data={
                    "Mes_eva": "2026_5",
                    "month": "mayo",
                    "year": 2026,
                    "afi_DNI": "94405414",
                    "components_observed": "Vacuna neumococo",
                    "reason": "Vacuna neumococo: No registra dosis.",
                },
                period_key="2026_5",
                period_label="mayo",
                dni="94405414",
                cnv=None,
                birth_date=None,
                province="ABANCAY",
                facility="TACMARA",
                components_observed="Vacuna neumococo",
                clinical_alerts=[],
                reason="Vacuna neumococo: No registra dosis.",
            )
        ]

        summary = report_summary_from_rows(upload, dashboard_rows, omissions, target_coverage=90)

        self.assertEqual(summary["target_coverage"], 90)
        self.assertEqual(summary["monthly"][0]["semaphore"], "red")
        self.assertFalse(summary["monthly"][0]["compliant"])
        self.assertEqual(summary["months_met"], 0)
        self.assertEqual(summary["omisos"][0]["afi_DNI"], "94405414")


class MC02StorageActivationStatusTests(unittest.TestCase):
    def test_fail_upload_marks_upload_as_failed(self):
        upload = SimpleNamespace(status="processing", error_message=None, processing_summary={})

        class FakeSession:
            def __init__(self):
                self.rollback_called = False
                self.commit_called = False

            def rollback(self):
                self.rollback_called = True

            def get(self, model, upload_id):
                return upload

            def commit(self):
                self.commit_called = True

        db = FakeSession()

        fail_upload(db, "upload-id", RuntimeError("fallo de procesamiento"))

        self.assertTrue(db.rollback_called)
        self.assertTrue(db.commit_called)
        self.assertEqual(upload.status, UPLOAD_STATUS_FAILED)
        self.assertIn("fallo de procesamiento", upload.error_message)
        self.assertIn("error", upload.processing_summary)


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

    def test_iron_4m_delivery_in_fourth_slot_is_used_for_summary(self):
        row, reference_date = row_at_age(
            150,
            fecha_4prev=date(2026, 5, 3),
            edad_4prev=122,
            CIE_Hierro_4prev="99199.17",
            Lab=1,
            Lote_Pag_Reg_4prev="lote:CED_Pag:1_Reg:1",
            EESS_Ate_4prev="CASINCHIHUA",
        )
        detail = component_detail(row, component("hierro_menor_6m"), reference_date)

        self.assertTrue(detail["cumple"])
        self.assertEqual(detail["fecha"], "2026-05-03")
        self.assertEqual(detail["edad_atencion_dias"], 122)
        self.assertEqual(detail["codigo"], "99199.17")
        self.assertEqual(detail["lab"], "1")
        self.assertEqual(detail["establecimiento_atencion"], "CASINCHIHUA")
        self.assertEqual(len(detail["entregas"]), 1)
        self.assertEqual(detail["entregas"][0]["label"], "Entrega 4")

    def test_non_required_iron_6m_without_trace_is_programmed_even_if_excel_flag_is_true(self):
        row, reference_date = row_at_age(200, obs_suple61=1, OBS_SUPLE6="Cumple")
        detail = component_detail(row, component("hierro_mayor_6m"), reference_date)

        self.assertTrue(detail["cumple"])
        self.assertEqual(detail["estado"], "programado")
        self.assertEqual(detail["fecha"], None)
        self.assertEqual(detail["entregas"], [])

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

    def test_hemoglobin_required_flag_without_trace_does_not_comply(self):
        row, reference_date = row_at_age(230, Obs_dh1=1, Obs_Dh="Cumple")
        detail = component_detail(row, component("hemoglobina"), reference_date)

        self.assertFalse(detail["cumple"])
        self.assertEqual(detail["estado"], "incumplimiento_fuera_plazo")
        self.assertEqual(detail["fecha"], None)
        self.assertEqual(detail["codigo"], "")

    def test_hemoglobin_valid_trace_complies_without_excel_flag(self):
        row, reference_date = row_at_age(
            230,
            Obs_dh1=0,
            fecha_1DH=date(2026, 7, 1),
            edad_1DH=181,
            CIE_DH_1DH="85018",
            EESS_Ate_1DH="TACMARA",
        )
        detail = component_detail(row, component("hemoglobina"), reference_date)

        self.assertTrue(detail["cumple"])
        self.assertEqual(detail["estado"], "cumple")
        self.assertEqual(detail["fecha"], "2026-07-01")
        self.assertEqual(detail["edad_atencion_dias"], 181)
        self.assertEqual(detail["codigo"], "85018")

    def test_obs_anemia_numeric_flag_without_diagnosis_does_not_alert(self):
        row, _ = row_at_age(
            196,
            Obs_Anemia=1,
            Dx_Anemia=None,
            CIE_Anemia_1Hier=None,
            Fec_Anemia=None,
            fecha_1Hier=None,
        )

        self.assertFalse(has_anemia_diagnosis(row))
        self.assertEqual(anemia_alerts(row), [])

    def test_treatment_anemia_code_without_dx_anemia_does_not_alert(self):
        row, _ = row_at_age(230, CIE_Anemia_1Hier="D509", fecha_1Hier=date(2026, 7, 29))

        self.assertFalse(has_anemia_diagnosis(row))
        self.assertEqual(anemia_alerts(row), [])

    def test_dx_anemia_code_alerts(self):
        row, _ = row_at_age(230, Dx_Anemia="D509")

        self.assertTrue(has_anemia_diagnosis(row))
        self.assertTrue(anemia_alerts(row))

    def test_fec_anemia_alerts_even_without_code(self):
        row, _ = row_at_age(230, Fec_Anemia=date(2026, 7, 29))

        self.assertTrue(has_anemia_diagnosis(row))
        self.assertTrue(anemia_alerts(row))

    def test_iron_6m_preventive_delivery_is_exposed_as_delivery(self):
        row, reference_date = row_at_age(
            230,
            obs_suple61=1,
            fecha_1prevhierr=date(2026, 7, 29),
            edad_1prevhierr=209,
            CIE_Hierro_1prevhierr="99199.17",
            Lab_1prevhierr=1,
            Intervalo1s=30,
            EESS_Ate_1prevhierr="TACMARA",
        )
        detail = component_detail(row, component("hierro_mayor_6m"), reference_date)

        self.assertEqual(detail["estado"], "cumple")
        self.assertEqual(len(detail["entregas"]), 1)
        self.assertEqual(detail["entregas"][0]["tipo"], "Preventiva 6 a 11 meses")


if __name__ == "__main__":
    unittest.main()
