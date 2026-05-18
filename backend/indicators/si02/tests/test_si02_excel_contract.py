from __future__ import annotations

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from indicators.si02.config import EXPECTED_PACKAGE_CODES, SUBINDICATORS
from indicators.si02.excel_loader import (
    identify_subindicator,
    operational_columns,
    prepare_subindicator_file,
    prepare_upload_package,
    required_columns,
)


DOWNLOADS_DIR = Path("E:/Downloads")
SAMPLE_PATTERNS = {
    "si02_01": "SI_02_01*.xlsx",
    "si02_02": "SI_02_02*.xlsx",
    "si02_03": "SI_02_03*.xlsx",
    "si02_04": "SI_02_04*.xlsx",
}
EXPECTED_ROWS = {
    "si02_01": 4895,
    "si02_02": 396,
    "si02_03": 225,
    "si02_04": 5156,
}
EXPECTED_ABANCAY_ROWS = {
    "si02_01": 1543,
    "si02_02": 124,
    "si02_03": 58,
    "si02_04": 1604,
}


def sample_files() -> dict[str, Path]:
    files: dict[str, Path] = {}
    for code, pattern in SAMPLE_PATTERNS.items():
        matches = sorted(DOWNLOADS_DIR.glob(pattern))
        if matches:
            files[code] = matches[0]
    return files


class SI02ExcelContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = sample_files()
        if set(cls.files) != set(EXPECTED_PACKAGE_CODES):
            raise unittest.SkipTest("No se encontraron los cuatro Excel SI-02 de ejemplo en E:/Downloads.")

    def test_required_columns_are_subset_of_operational_columns(self):
        for code in EXPECTED_PACKAGE_CODES:
            with self.subTest(code=code):
                self.assertTrue(set(required_columns(code)).issubset(operational_columns(code)))

    def test_identifies_each_subindicator_from_excel_contract(self):
        for code, filepath in self.files.items():
            with self.subTest(code=code):
                self.assertEqual(identify_subindicator(filepath), code)

    def test_validates_each_subindicator_file(self):
        for code, filepath in self.files.items():
            with self.subTest(code=code):
                prepared = prepare_subindicator_file(filepath, expected_code=code)
                validation = prepared["validation"]
                summary = validation["summary"]

                self.assertTrue(validation["valid"], validation["errors"])
                self.assertEqual(summary["subindicator_code"], code)
                self.assertEqual(summary["header_row"], SUBINDICATORS[code].header_row)
                self.assertEqual(summary["total_rows"], EXPECTED_ROWS[code])
                self.assertIn("ABANCAY", summary["provinces"])
                self.assertEqual(summary["status_counts"].get("Cumple", 0) + summary["status_counts"].get("No_Cumple", 0), EXPECTED_ROWS[code])

                province_column = SUBINDICATORS[code].province_column
                abancay_rows = int((prepared["data"][province_column].astype(str).str.upper().str.strip() == "ABANCAY").sum())
                self.assertEqual(abancay_rows, EXPECTED_ABANCAY_ROWS[code])

    def test_validates_complete_upload_package(self):
        prepared = prepare_upload_package(self.files.values())
        validation = prepared["validation"]
        summary = validation["summary"]

        self.assertTrue(validation["valid"], validation["errors"])
        self.assertEqual(summary["files_received"], 4)
        self.assertEqual(summary["subindicators_found"], sorted(EXPECTED_PACKAGE_CODES))
        self.assertEqual(summary["total_rows"], sum(EXPECTED_ROWS.values()))

    def test_package_requires_all_four_files(self):
        partial_files = [path for code, path in self.files.items() if code != "si02_04"]
        validation = prepare_upload_package(partial_files, load_data=False)["validation"]

        self.assertFalse(validation["valid"])
        self.assertIn("si02_04", validation["summary"]["missing_subindicators"])


if __name__ == "__main__":
    unittest.main()
