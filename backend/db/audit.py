"""Audit and upload-history helpers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID as PythonUUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from .models import IndicatorActiveUpload, IndicatorAuditEvent, IndicatorUpload


def jsonable(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [jsonable(item) for item in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except (TypeError, ValueError):
            return str(value)
    return value


def record_audit_event(
    db: Session,
    indicator_code: str,
    event_type: str,
    actor: str | None = None,
    actor_role: str | None = None,
    upload_id: PythonUUID | None = None,
    message: str | None = None,
    details: dict[str, Any] | None = None,
) -> IndicatorAuditEvent:
    event = IndicatorAuditEvent(
        indicator_code=indicator_code,
        upload_id=upload_id,
        event_type=event_type,
        actor=actor,
        actor_role=actor_role,
        message=message,
        details=jsonable(details or {}),
    )
    db.add(event)
    db.flush()
    return event


def upload_item(upload: IndicatorUpload, active_upload_id: PythonUUID | None, active_activated_by: str | None = None) -> dict[str, Any]:
    return {
        "id": str(upload.id),
        "indicator_code": upload.indicator_code,
        "status": upload.status,
        "is_active": bool(active_upload_id and upload.id == active_upload_id),
        "original_filename": upload.original_filename,
        "stored_file_path": upload.stored_file_path,
        "file_hash": upload.file_hash,
        "cutoff_date": upload.cutoff_date,
        "uploaded_by": upload.uploaded_by,
        "activated_at": upload.activated_at,
        "activated_by": active_activated_by,
        "rows_total": upload.rows_total,
        "columns_total": upload.columns_total,
        "loaded_columns": upload.loaded_columns,
        "storage_format": upload.storage_format,
        "source_preserved": upload.source_preserved,
        "error_message": upload.error_message,
        "created_at": upload.created_at,
        "updated_at": upload.updated_at,
        "processing_summary": upload.processing_summary or {},
        "validation_summary": upload.validation_summary or {},
    }


def list_upload_history(db: Session, indicator_code: str | None = None, limit: int = 30) -> list[dict[str, Any]]:
    statement = select(IndicatorUpload).order_by(desc(IndicatorUpload.created_at)).limit(limit)
    if indicator_code:
        statement = statement.where(IndicatorUpload.indicator_code == indicator_code)
    uploads = db.execute(statement).scalars().all()
    active_refs = {item.indicator_code: item for item in db.execute(select(IndicatorActiveUpload)).scalars().all()}
    return [
        upload_item(
            upload,
            active_refs.get(upload.indicator_code).upload_id if upload.indicator_code in active_refs else None,
            active_refs.get(upload.indicator_code).activated_by if upload.indicator_code in active_refs else None,
        )
        for upload in uploads
    ]


def audit_event_item(event: IndicatorAuditEvent) -> dict[str, Any]:
    return {
        "id": str(event.id),
        "indicator_code": event.indicator_code,
        "upload_id": str(event.upload_id) if event.upload_id else None,
        "event_type": event.event_type,
        "actor": event.actor,
        "actor_role": event.actor_role,
        "message": event.message,
        "details": event.details or {},
        "created_at": event.created_at,
    }


def list_audit_events(
    db: Session,
    indicator_code: str | None = None,
    upload_id: PythonUUID | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    statement = select(IndicatorAuditEvent).order_by(desc(IndicatorAuditEvent.created_at)).limit(limit)
    if indicator_code:
        statement = statement.where(IndicatorAuditEvent.indicator_code == indicator_code)
    if upload_id:
        statement = statement.where(IndicatorAuditEvent.upload_id == upload_id)
    return [audit_event_item(event) for event in db.execute(statement).scalars().all()]


__all__ = ["list_audit_events", "list_upload_history", "record_audit_event"]
