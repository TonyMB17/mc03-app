from __future__ import annotations

import os
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from db.models import ComponentResult, DashboardSummary, IndicatorOmission, IndicatorRecord
from db.session import SessionLocal
from indicators.si02.excel_loader import prepare_upload_package
from indicators.si02.storage import active_upload_id, build_active_report_summary, persist_active_upload, search_active_by_dni


DOWNLOADS_DIR = Path("E:/Downloads")
SAMPLE_PATTERNS = ("SI_02_01*.xlsx", "SI_02_02*.xlsx", "SI_02_03*.xlsx", "SI_02_04*.xlsx")


def sample_files() -> list[Path]:
    files = []
    for pattern in SAMPLE_PATTERNS:
        matches = sorted(DOWNLOADS_DIR.glob(pattern))
        if matches:
            files.append(matches[0])
    return files


@unittest.skipUnless(os.getenv("RUN_SI02_DB_TESTS") == "1", "Define RUN_SI02_DB_TESTS=1 para ejecutar pruebas de PostgreSQL SI-02.")
class SI02StorageTests(unittest.TestCase):
    def test_persist_active_upload_package(self):
        files = sample_files()
        if len(files) != len(SAMPLE_PATTERNS):
            raise unittest.SkipTest("No se encontraron los cuatro Excel SI-02 de ejemplo en E:/Downloads.")

        prepared = prepare_upload_package(files)
        validation = prepared["validation"]
        self.assertTrue(validation["valid"], validation["errors"])
        summary = validation["summary"]
        summary["storage_format"] = "processed_si02_package"
        summary["source_preserved"] = False

        try:
            with SessionLocal() as db:
                upload_id = persist_active_upload(
                    db,
                    prepared["data"],
                    prepared["cutoff_dates"],
                    Path("E:/Downloads/SI02_package_processed.pkl"),
                    {"original_name": "SI-02 paquete semanal test", "uploaded_by": "test", "activated_by": "test", "actor_role": "admin"},
                    summary,
                )

                self.assertEqual(active_upload_id(db), upload_id)
                counts = {
                    "records": db.execute(select(func.count()).select_from(IndicatorRecord).where(IndicatorRecord.upload_id == upload_id)).scalar_one(),
                    "components": db.execute(select(func.count()).select_from(ComponentResult).where(ComponentResult.upload_id == upload_id)).scalar_one(),
                    "dashboard": db.execute(select(func.count()).select_from(DashboardSummary).where(DashboardSummary.upload_id == upload_id)).scalar_one(),
                    "omissions": db.execute(select(func.count()).select_from(IndicatorOmission).where(IndicatorOmission.upload_id == upload_id)).scalar_one(),
                }
                self.assertEqual(counts["records"], 10672)
                self.assertEqual(counts["components"], 49797)
                self.assertGreater(counts["dashboard"], 0)
                self.assertGreater(counts["omissions"], 0)

                report = build_active_report_summary(db, "ABANCAY")
                self.assertEqual(set(report["subindicators"]), {"si02_01", "si02_02", "si02_03", "si02_04"})
                self.assertGreater(len(report["omisos"]), 0)

                result = search_active_by_dni(db, "94061040", province=None)
                self.assertIsNotNone(result)
                self.assertTrue(result["subindicators"])
        except SQLAlchemyError as exc:
            raise unittest.SkipTest(f"No se pudo conectar a PostgreSQL: {exc}") from exc


if __name__ == "__main__":
    unittest.main()
