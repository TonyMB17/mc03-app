"""SQLAlchemy models for processed indicator storage."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID as PythonUUID
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class IndicatorUpload(TimestampMixin, Base):
    __tablename__ = "indicator_uploads"

    id: Mapped[PythonUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    indicator_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=True)
    stored_file_path: Mapped[str] = mapped_column(Text, nullable=True)
    file_hash: Mapped[str] = mapped_column(String(128), nullable=True, index=True)
    cutoff_date: Mapped[date] = mapped_column(Date, nullable=True)
    uploaded_by: Mapped[str] = mapped_column(String(120), nullable=True)
    activated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    rows_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    columns_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    loaded_columns: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    storage_format: Mapped[str] = mapped_column(String(64), nullable=True)
    source_preserved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    validation_summary: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    processing_summary: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    active_reference: Mapped["IndicatorActiveUpload"] = relationship(back_populates="upload")
    records: Mapped[list["IndicatorRecord"]] = relationship(back_populates="upload", cascade="all, delete-orphan")
    component_results: Mapped[list["ComponentResult"]] = relationship(back_populates="upload", cascade="all, delete-orphan")
    dashboard_summaries: Mapped[list["DashboardSummary"]] = relationship(back_populates="upload", cascade="all, delete-orphan")
    omissions: Mapped[list["IndicatorOmission"]] = relationship(back_populates="upload", cascade="all, delete-orphan")
    audit_events: Mapped[list["IndicatorAuditEvent"]] = relationship(back_populates="upload", cascade="all, delete-orphan")


class IndicatorActiveUpload(Base):
    __tablename__ = "indicator_active_uploads"

    indicator_code: Mapped[str] = mapped_column(String(32), primary_key=True)
    upload_id: Mapped[PythonUUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("indicator_uploads.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    activated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    activated_by: Mapped[str] = mapped_column(String(120), nullable=True)

    upload: Mapped[IndicatorUpload] = relationship(back_populates="active_reference")


class IndicatorRecord(TimestampMixin, Base):
    __tablename__ = "indicator_records"
    __table_args__ = (
        Index("ix_indicator_records_upload_dni", "upload_id", "dni"),
        Index("ix_indicator_records_upload_cnv", "upload_id", "cnv"),
        Index("ix_indicator_records_indicator_dni", "indicator_code", "dni"),
        Index("ix_indicator_records_indicator_cnv", "indicator_code", "cnv"),
        Index("ix_indicator_records_upload_period", "upload_id", "period_key"),
        Index("ix_indicator_records_upload_province", "upload_id", "province"),
    )

    id: Mapped[PythonUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    upload_id: Mapped[PythonUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("indicator_uploads.id", ondelete="CASCADE"), nullable=False)
    indicator_code: Mapped[str] = mapped_column(String(32), nullable=False)
    dni: Mapped[str] = mapped_column(String(32), nullable=True)
    cnv: Mapped[str] = mapped_column(String(32), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    first_names: Mapped[str] = mapped_column(String(160), nullable=True)
    paternal_surname: Mapped[str] = mapped_column(String(120), nullable=True)
    maternal_surname: Mapped[str] = mapped_column(String(120), nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=True)
    province: Mapped[str] = mapped_column(String(120), nullable=True)
    district: Mapped[str] = mapped_column(String(120), nullable=True)
    microred: Mapped[str] = mapped_column(String(160), nullable=True)
    facility_code: Mapped[str] = mapped_column(String(32), nullable=True)
    facility: Mapped[str] = mapped_column(String(255), nullable=True)
    period_key: Mapped[str] = mapped_column(String(32), nullable=True)
    period_label: Mapped[str] = mapped_column(String(80), nullable=True)
    period_year: Mapped[int] = mapped_column(Integer, nullable=True)
    period_month: Mapped[int] = mapped_column(Integer, nullable=True)
    denominator: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    package_complete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    clinical_alerts: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    personal_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    raw_selected_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    upload: Mapped[IndicatorUpload] = relationship(back_populates="records")
    component_results: Mapped[list["ComponentResult"]] = relationship(back_populates="record", cascade="all, delete-orphan")
    omission: Mapped["IndicatorOmission"] = relationship(back_populates="record", cascade="all, delete-orphan")


class ComponentResult(TimestampMixin, Base):
    __tablename__ = "component_results"
    __table_args__ = (
        UniqueConstraint("record_id", "component_key", name="uq_component_results_record_component"),
        Index("ix_component_results_upload_component", "upload_id", "component_key"),
        Index("ix_component_results_upload_status", "upload_id", "status"),
        Index("ix_component_results_upload_complies", "upload_id", "complies"),
    )

    id: Mapped[PythonUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    upload_id: Mapped[PythonUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("indicator_uploads.id", ondelete="CASCADE"), nullable=False)
    record_id: Mapped[PythonUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("indicator_records.id", ondelete="CASCADE"), nullable=False)
    indicator_code: Mapped[str] = mapped_column(String(32), nullable=False)
    component_key: Mapped[str] = mapped_column(String(80), nullable=False)
    component_label: Mapped[str] = mapped_column(String(160), nullable=True)
    component_group: Mapped[str] = mapped_column(String(80), nullable=True)
    complies: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="pending")
    message: Mapped[str] = mapped_column(Text, nullable=True)
    result_text: Mapped[str] = mapped_column(String(160), nullable=True)
    attention_date: Mapped[date] = mapped_column(Date, nullable=True)
    attention_age_days: Mapped[int] = mapped_column(Integer, nullable=True)
    code: Mapped[str] = mapped_column(String(80), nullable=True)
    lab: Mapped[str] = mapped_column(String(80), nullable=True)
    lot: Mapped[str] = mapped_column(String(160), nullable=True)
    attention_facility: Mapped[str] = mapped_column(String(255), nullable=True)
    professional: Mapped[str] = mapped_column(String(255), nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    upload: Mapped[IndicatorUpload] = relationship(back_populates="component_results")
    record: Mapped[IndicatorRecord] = relationship(back_populates="component_results")


class DashboardSummary(TimestampMixin, Base):
    __tablename__ = "dashboard_summaries"
    __table_args__ = (
        UniqueConstraint("upload_id", "province", "period_key", name="uq_dashboard_summaries_upload_province_period"),
        Index("ix_dashboard_summaries_indicator_period", "indicator_code", "period_key"),
        Index("ix_dashboard_summaries_upload_province", "upload_id", "province"),
    )

    id: Mapped[PythonUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    upload_id: Mapped[PythonUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("indicator_uploads.id", ondelete="CASCADE"), nullable=False)
    indicator_code: Mapped[str] = mapped_column(String(32), nullable=False)
    province: Mapped[str] = mapped_column(String(120), nullable=False)
    period_key: Mapped[str] = mapped_column(String(32), nullable=False)
    period_label: Mapped[str] = mapped_column(String(80), nullable=True)
    period_year: Mapped[int] = mapped_column(Integer, nullable=True)
    period_month: Mapped[int] = mapped_column(Integer, nullable=True)
    denominator: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    numerator: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    coverage: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False, default=0)
    target_coverage: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False, default=0)
    semaphore: Mapped[str] = mapped_column(String(16), nullable=False, default="red")
    compliant: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    in_verification_period: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    summary_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    upload: Mapped[IndicatorUpload] = relationship(back_populates="dashboard_summaries")


class IndicatorOmission(TimestampMixin, Base):
    __tablename__ = "indicator_omissions"
    __table_args__ = (
        UniqueConstraint("record_id", name="uq_indicator_omissions_record"),
        Index("ix_indicator_omissions_upload_period", "upload_id", "period_key"),
        Index("ix_indicator_omissions_upload_province", "upload_id", "province"),
        Index("ix_indicator_omissions_upload_dni", "upload_id", "dni"),
        Index("ix_indicator_omissions_upload_cnv", "upload_id", "cnv"),
    )

    id: Mapped[PythonUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    upload_id: Mapped[PythonUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("indicator_uploads.id", ondelete="CASCADE"), nullable=False)
    record_id: Mapped[PythonUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("indicator_records.id", ondelete="CASCADE"), nullable=False)
    indicator_code: Mapped[str] = mapped_column(String(32), nullable=False)
    province: Mapped[str] = mapped_column(String(120), nullable=True)
    period_key: Mapped[str] = mapped_column(String(32), nullable=True)
    period_label: Mapped[str] = mapped_column(String(80), nullable=True)
    dni: Mapped[str] = mapped_column(String(32), nullable=True)
    cnv: Mapped[str] = mapped_column(String(32), nullable=True)
    patient_name: Mapped[str] = mapped_column(String(255), nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=True)
    facility: Mapped[str] = mapped_column(String(255), nullable=True)
    components_observed: Mapped[str] = mapped_column(Text, nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    clinical_alerts: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    export_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    upload: Mapped[IndicatorUpload] = relationship(back_populates="omissions")
    record: Mapped[IndicatorRecord] = relationship(back_populates="omission")


class IndicatorAuditEvent(Base):
    __tablename__ = "indicator_audit_events"
    __table_args__ = (
        Index("ix_indicator_audit_events_indicator_created", "indicator_code", "created_at"),
        Index("ix_indicator_audit_events_upload", "upload_id"),
        Index("ix_indicator_audit_events_event_type", "event_type"),
    )

    id: Mapped[PythonUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    indicator_code: Mapped[str] = mapped_column(String(32), nullable=False)
    upload_id: Mapped[PythonUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("indicator_uploads.id", ondelete="CASCADE"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    actor: Mapped[str] = mapped_column(String(120), nullable=True)
    actor_role: Mapped[str] = mapped_column(String(64), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    upload: Mapped[IndicatorUpload] = relationship(back_populates="audit_events")


__all__ = [
    "Base",
    "ComponentResult",
    "DashboardSummary",
    "IndicatorActiveUpload",
    "IndicatorAuditEvent",
    "IndicatorOmission",
    "IndicatorRecord",
    "IndicatorUpload",
]
