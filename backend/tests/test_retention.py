import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from backend.db.retention import BACKEND_DIR, safe_unlink, upload_retention_days


class RetentionHelpersTest(unittest.TestCase):
    def test_upload_retention_days_uses_safe_default(self):
        with patch.dict("os.environ", {"UPLOAD_RETENTION_DAYS": "7"}, clear=False):
            self.assertEqual(upload_retention_days(), 7)

        with patch.dict("os.environ", {"UPLOAD_RETENTION_DAYS": "invalid"}, clear=False):
            self.assertEqual(upload_retention_days(), 7)

        with patch.dict("os.environ", {"UPLOAD_RETENTION_DAYS": "0"}, clear=False):
            self.assertEqual(upload_retention_days(), 1)

    def test_safe_unlink_only_removes_backend_upload_files(self):
        uploads_dir = BACKEND_DIR / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        allowed_file = uploads_dir / f"retention_test_{uuid4().hex}.tmp"
        allowed_file.write_text("temporary", encoding="utf-8")

        external_handle = tempfile.NamedTemporaryFile(delete=False)
        external_path = Path(external_handle.name)
        external_handle.close()

        try:
            self.assertTrue(safe_unlink(allowed_file))
            self.assertFalse(allowed_file.exists())
            self.assertFalse(safe_unlink(external_path))
            self.assertTrue(external_path.exists())
        finally:
            external_path.unlink(missing_ok=True)
            allowed_file.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
