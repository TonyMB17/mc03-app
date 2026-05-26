"""Retention cleanup for inactive indicator uploads."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .session import BACKEND_DIR
from .models import IndicatorActiveUpload, IndicatorUpload


DEFAULT_UPLOAD_RETENTION_DAYS = 7
INACTIVE_UPLOAD_STATUSES = {"superseded", "failed"}
REMOVABLE_FILE_DIRS = (BACKEND_DIR / "uploads", BACKEND_DIR / "processed_uploads")


def upload_retention_days() -> int:
    raw_value = os.getenv("UPLOAD_RETENTION_DAYS", str(DEFAULT_UPLOAD_RETENTION_DAYS))
    try:
        return max(1, int(raw_value))
    except ValueError:
        return DEFAULT_UPLOAD_RETENTION_DAYS


def cleanup_inactive_uploads(
    db: Session,
    retention_days: int | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    days = retention_days if retention_days is not None else upload_retention_days()
    current_time = now or datetime.now(timezone.utc)
    cutoff = current_time - timedelta(days=days)
    active_upload_ids = set(db.execute(select(IndicatorActiveUpload.upload_id)).scalars().all())

    statement = select(IndicatorUpload).where(
        IndicatorUpload.status.in_(INACTIVE_UPLOAD_STATUSES),
        IndicatorUpload.updated_at < cutoff,
    )
    if active_upload_ids:
        statement = statement.where(IndicatorUpload.id.not_in(active_upload_ids))

    uploads = db.execute(statement).scalars().all()
    if not uploads:
        return {"retention_days": days, "deleted_uploads": [], "deleted_files": []}

    deleted_uploads = [str(upload.id) for upload in uploads]
    deleted_files: list[str] = []
    for upload in uploads:
        deleted_files.extend(delete_upload_files(upload))

    db.execute(delete(IndicatorUpload).where(IndicatorUpload.id.in_([upload.id for upload in uploads])))
    db.commit()
    return {"retention_days": days, "deleted_uploads": deleted_uploads, "deleted_files": deleted_files}


def delete_upload_files(upload: IndicatorUpload) -> list[str]:
    deleted: list[str] = []
    for file_path in candidate_file_paths(upload):
        if safe_unlink(file_path):
            deleted.append(str(file_path))
    return deleted


def candidate_file_paths(upload: IndicatorUpload) -> set[Path]:
    candidates: set[Path] = set()
    if upload.stored_file_path:
        candidates.add(Path(upload.stored_file_path))
    for payload in (upload.validation_summary or {}, upload.processing_summary or {}):
        for key in ("stored_file_path", "processed_path", "active_file"):
            value = payload.get(key)
            if value:
                candidates.add(Path(str(value)))
    return candidates


def safe_unlink(path: Path) -> bool:
    try:
        resolved_path = path.resolve()
    except OSError:
        return False

    allowed = False
    for directory in REMOVABLE_FILE_DIRS:
        try:
            if resolved_path.is_relative_to(directory.resolve()):
                allowed = True
                break
        except OSError:
            continue

    if not allowed or not resolved_path.is_file():
        return False

    try:
        resolved_path.unlink()
        return True
    except OSError:
        return False


__all__ = ["cleanup_inactive_uploads", "upload_retention_days"]
