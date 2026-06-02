import tempfile
import unittest
from pathlib import Path

from backend import main


class UploadCleanupTest(unittest.TestCase):
    def test_cleanup_removes_only_managed_upload_files(self):
        upload_file = main.UPLOADS_DIR / "cleanup_test_upload.xlsx"
        processed_file = main.PROCESSED_UPLOADS_DIR / "cleanup_test_processed.pkl"
        upload_file.parent.mkdir(parents=True, exist_ok=True)
        processed_file.parent.mkdir(parents=True, exist_ok=True)
        upload_file.write_bytes(b"upload")
        processed_file.write_bytes(b"processed")

        with tempfile.NamedTemporaryFile(delete=False) as outside_file:
            outside_path = Path(outside_file.name)
            outside_file.write(b"keep")

        try:
            main._cleanup_pending_upload_files(
                {
                    "path": str(upload_file),
                    "paths": [str(upload_file), str(outside_path)],
                    "processed_path": str(processed_file),
                }
            )

            self.assertFalse(upload_file.exists())
            self.assertFalse(processed_file.exists())
            self.assertTrue(outside_path.exists())
        finally:
            main._delete_file_quietly(upload_file)
            main._delete_file_quietly(processed_file)
            main._delete_file_quietly(outside_path)


if __name__ == "__main__":
    unittest.main()
