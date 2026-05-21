from __future__ import annotations

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from indicators.si02.evaluator import component_rules, evaluate_dataframe, evaluate_row, excel_component_flag
from indicators.si02.excel_loader import prepare_upload_package
from indicators.si02.processor import build_package_summary, search_by_dni


DOWNLOADS_DIR = Path("E:/Downloads")
SAMPLE_PATTERNS = {
    "si02_01": "SI_02_01*.xlsx",
    "si02_02": "SI_02_02*.xlsx",
    "si02_03": "SI_02_03*.xlsx",
    "si02_04": "SI_02_04*.xlsx",
}
EXPECTED_COMPLETE_COUNTS = {
    "si02_01": 1503,
    "si02_02": 93,
    "si02_03": 65,
    "si02_04": 1281,
}
EXPECTED_COMPONENT_TRUE_COUNTS = {
    "si02_01": {"hierro_4m": 2312, "dosaje_6m": 1651, "ta": 1568},
    "si02_02": {"dh_1m": 233, "hierro_1m": 245, "hierro_4m": 192, "dh_3m": 138, "dh_6m": 125, "ta_observado": 111},
    "si02_03": {"hierro_tratamiento": 166, "dh_1m": 201, "dh_2m": 157, "dh_3m": 136, "ta": 81, "dh_6m": 98},
    "si02_04": {"hierro_preventivo": 2722, "dh_3m": 2343, "ta": 1405, "dh_12m": 1462},
}


def sample_files() -> dict[str, Path]:
    files: dict[str, Path] = {}
    for code, pattern in SAMPLE_PATTERNS.items():
        matches = sorted(DOWNLOADS_DIR.glob(pattern))
        if matches:
            files[code] = matches[0]
    return files


class SI02RuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = sample_files()
        if set(cls.files) != set(SAMPLE_PATTERNS):
            raise unittest.SkipTest("No se encontraron los cuatro Excel SI-02 de ejemplo en E:/Downloads.")
        prepared = prepare_upload_package(cls.files.values())
        validation = prepared["validation"]
        if not validation["valid"]:
            raise unittest.SkipTest("; ".join(validation["errors"]))
        cls.package_data = prepared["data"]

    def test_component_flags_reconcile_with_reference_excel(self):
        for code, df in self.package_data.items():
            evaluated = evaluate_dataframe(df, code)
            with self.subTest(code=code, component="general"):
                self.assertEqual(int(evaluated["cumple"].sum()), EXPECTED_COMPLETE_COUNTS[code])

            for rule in component_rules(code):
                true_count = sum(1 for details in evaluated["detalles"] if details[rule.key]["cumple"])
                with self.subTest(code=code, component=rule.key):
                    self.assertEqual(true_count, EXPECTED_COMPONENT_TRUE_COUNTS.get(code, {}).get(rule.key, true_count))

                mismatches = 0
                compared = 0
                for index, row in df.iterrows():
                    reference_flag = excel_component_flag(row, code, rule.key)
                    if reference_flag is None:
                        continue
                    compared += 1
                    if reference_flag != evaluated.loc[index, "detalles"][rule.key]["cumple"]:
                        mismatches += 1

                if compared:
                    with self.subTest(code=code, component=f"{rule.key}_reference"):
                        self.assertEqual(mismatches, 0)

    def test_si0204_preventive_iron_transition_examples(self):
        df = self.package_data["si02_04"]
        examples = {
            "94061040": True,
            "94118433": False,
            "80881953": False,
        }
        for dni, expected in examples.items():
            row = df[df["afi_dni"].astype(str).str.strip() == dni].iloc[0]
            result = evaluate_row(row, "si02_04")["details"]["hierro_preventivo"]
            with self.subTest(dni=dni):
                self.assertEqual(result["cumple"], expected)

    def test_processor_builds_package_summary_and_dni_search(self):
        summary = build_package_summary(self.package_data, province=None)

        self.assertTrue(summary["package_complete"])
        self.assertEqual(set(summary["subindicators"]), set(SAMPLE_PATTERNS))
        self.assertTrue(all(item["monthly"] for item in summary["subindicators"].values()))

        result = search_by_dni(self.package_data, "94061040", province=None)
        self.assertIsNotNone(result)
        si0204 = next(item for item in result["subindicators"] if item["subindicator_code"] == "si02_04")
        self.assertTrue(si0204["details"]["hierro_preventivo"]["cumple"])

        filtered_result = search_by_dni(self.package_data, "94061040", province=None, subindicator="si02_04")
        self.assertIsNotNone(filtered_result)
        self.assertEqual([item["subindicator_code"] for item in filtered_result["subindicators"]], ["si02_04"])


if __name__ == "__main__":
    unittest.main()
