import unittest

from backend.automation.cloud_source import FILE_TARGETS, parse_cloud_datetime, targets_for_indicators


class CloudAutomationConfigTest(unittest.TestCase):
    def test_targets_include_required_indicators(self):
        keys = {target.key for target in FILE_TARGETS}

        self.assertEqual(
            keys,
            {"si02_01", "si02_02", "si02_03", "si02_04", "mc02", "mc03"},
        )

    def test_targets_can_filter_by_indicator(self):
        targets = targets_for_indicators(["si02"])

        self.assertEqual({target.key for target in targets}, {"si02_01", "si02_02", "si02_03", "si02_04"})

    def test_parse_cloud_datetime(self):
        parsed = parse_cloud_datetime("2026-05-18 15:44:01")

        self.assertEqual(parsed.year, 2026)
        self.assertEqual(parsed.month, 5)
        self.assertEqual(parsed.day, 18)


if __name__ == "__main__":
    unittest.main()
