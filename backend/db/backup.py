"""Create PostgreSQL backups with pg_dump."""

from __future__ import annotations

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from sqlalchemy.engine import make_url

try:
    from .session import BACKEND_DIR, database_url
except ImportError:
    from session import BACKEND_DIR, database_url


BACKUP_DIR = BACKEND_DIR / "backups"


def pg_dump_command() -> str:
    configured_path = os.getenv("PG_DUMP_PATH")
    if configured_path:
        path = Path(configured_path)
        if path.exists():
            return str(path)
        raise RuntimeError(f"PG_DUMP_PATH no existe: {configured_path}")

    detected_path = shutil.which("pg_dump")
    if detected_path is None:
        raise RuntimeError(
            "pg_dump no esta disponible en el PATH. "
            "Instala PostgreSQL client tools, agrega pg_dump al PATH o configura PG_DUMP_PATH."
        )
    return detected_path


def backup_retention_days() -> int:
    raw_value = os.getenv("BACKUP_RETENTION_DAYS", "30")
    try:
        return max(1, int(raw_value))
    except ValueError:
        return 30


def pg_dump_url() -> str:
    url = make_url(database_url()).set(drivername="postgresql")
    return url.render_as_string(hide_password=False)


def create_backup(output_dir: Path = BACKUP_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"indicator_tracking_{timestamp}.dump"
    subprocess.run(
        [pg_dump_command(), "--format=custom", "--file", str(output_file), pg_dump_url()],
        check=True,
    )
    prune_old_backups(output_dir)
    return output_file


def prune_old_backups(output_dir: Path = BACKUP_DIR, retention_days: int | None = None) -> list[Path]:
    if not output_dir.exists():
        return []

    days = retention_days if retention_days is not None else backup_retention_days()
    cutoff_timestamp = datetime.now().timestamp() - (days * 24 * 60 * 60)
    removed: list[Path] = []

    for backup_file in output_dir.glob("indicator_tracking_*.dump"):
        if backup_file.is_file() and backup_file.stat().st_mtime < cutoff_timestamp:
            backup_file.unlink()
            removed.append(backup_file)

    return removed


def main() -> None:
    output_file = create_backup()
    print(output_file)


if __name__ == "__main__":
    main()
