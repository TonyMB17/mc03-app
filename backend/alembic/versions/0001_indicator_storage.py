"""create indicator storage tables

Revision ID: 0001_indicator_storage
Revises: 
Create Date: 2026-05-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_indicator_storage"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "indicator_uploads",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("indicator_code", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("stored_file_path", sa.Text(), nullable=True),
        sa.Column("file_hash", sa.String(length=128), nullable=True),
        sa.Column("cutoff_date", sa.Date(), nullable=True),
        sa.Column("uploaded_by", sa.String(length=120), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rows_total", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("columns_total", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("loaded_columns", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("storage_format", sa.String(length=64), nullable=True),
        sa.Column("source_preserved", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("validation_summary", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("processing_summary", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_indicator_uploads")),
    )
    op.create_index(op.f("ix_indicator_uploads_file_hash"), "indicator_uploads", ["file_hash"], unique=False)
    op.create_index(op.f("ix_indicator_uploads_indicator_code"), "indicator_uploads", ["indicator_code"], unique=False)
    op.create_index(op.f("ix_indicator_uploads_status"), "indicator_uploads", ["status"], unique=False)

    op.create_table(
        "indicator_active_uploads",
        sa.Column("indicator_code", sa.String(length=32), nullable=False),
        sa.Column("upload_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("activated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("activated_by", sa.String(length=120), nullable=True),
        sa.ForeignKeyConstraint(["upload_id"], ["indicator_uploads.id"], name=op.f("fk_indicator_active_uploads_upload_id_indicator_uploads"), ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("indicator_code", name=op.f("pk_indicator_active_uploads")),
        sa.UniqueConstraint("upload_id", name=op.f("uq_indicator_active_uploads_upload_id")),
    )

    op.create_table(
        "indicator_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("upload_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("indicator_code", sa.String(length=32), nullable=False),
        sa.Column("dni", sa.String(length=32), nullable=True),
        sa.Column("cnv", sa.String(length=32), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("first_names", sa.String(length=160), nullable=True),
        sa.Column("paternal_surname", sa.String(length=120), nullable=True),
        sa.Column("maternal_surname", sa.String(length=120), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("province", sa.String(length=120), nullable=True),
        sa.Column("district", sa.String(length=120), nullable=True),
        sa.Column("microred", sa.String(length=160), nullable=True),
        sa.Column("facility_code", sa.String(length=32), nullable=True),
        sa.Column("facility", sa.String(length=255), nullable=True),
        sa.Column("period_key", sa.String(length=32), nullable=True),
        sa.Column("period_label", sa.String(length=80), nullable=True),
        sa.Column("period_year", sa.Integer(), nullable=True),
        sa.Column("period_month", sa.Integer(), nullable=True),
        sa.Column("denominator", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("package_complete", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("clinical_alerts", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("personal_data", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("raw_selected_data", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["upload_id"], ["indicator_uploads.id"], name=op.f("fk_indicator_records_upload_id_indicator_uploads"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_indicator_records")),
    )
    op.create_index("ix_indicator_records_indicator_cnv", "indicator_records", ["indicator_code", "cnv"], unique=False)
    op.create_index("ix_indicator_records_indicator_dni", "indicator_records", ["indicator_code", "dni"], unique=False)
    op.create_index("ix_indicator_records_upload_cnv", "indicator_records", ["upload_id", "cnv"], unique=False)
    op.create_index("ix_indicator_records_upload_dni", "indicator_records", ["upload_id", "dni"], unique=False)
    op.create_index("ix_indicator_records_upload_period", "indicator_records", ["upload_id", "period_key"], unique=False)
    op.create_index("ix_indicator_records_upload_province", "indicator_records", ["upload_id", "province"], unique=False)

    op.create_table(
        "component_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("upload_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("indicator_code", sa.String(length=32), nullable=False),
        sa.Column("component_key", sa.String(length=80), nullable=False),
        sa.Column("component_label", sa.String(length=160), nullable=True),
        sa.Column("component_group", sa.String(length=80), nullable=True),
        sa.Column("complies", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("result_text", sa.String(length=160), nullable=True),
        sa.Column("attention_date", sa.Date(), nullable=True),
        sa.Column("attention_age_days", sa.Integer(), nullable=True),
        sa.Column("code", sa.String(length=80), nullable=True),
        sa.Column("lab", sa.String(length=80), nullable=True),
        sa.Column("lot", sa.String(length=160), nullable=True),
        sa.Column("attention_facility", sa.String(length=255), nullable=True),
        sa.Column("professional", sa.String(length=255), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["record_id"], ["indicator_records.id"], name=op.f("fk_component_results_record_id_indicator_records"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["upload_id"], ["indicator_uploads.id"], name=op.f("fk_component_results_upload_id_indicator_uploads"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_component_results")),
        sa.UniqueConstraint("record_id", "component_key", name="uq_component_results_record_component"),
    )
    op.create_index("ix_component_results_upload_complies", "component_results", ["upload_id", "complies"], unique=False)
    op.create_index("ix_component_results_upload_component", "component_results", ["upload_id", "component_key"], unique=False)
    op.create_index("ix_component_results_upload_status", "component_results", ["upload_id", "status"], unique=False)

    op.create_table(
        "dashboard_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("upload_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("indicator_code", sa.String(length=32), nullable=False),
        sa.Column("province", sa.String(length=120), nullable=False),
        sa.Column("period_key", sa.String(length=32), nullable=False),
        sa.Column("period_label", sa.String(length=80), nullable=True),
        sa.Column("period_year", sa.Integer(), nullable=True),
        sa.Column("period_month", sa.Integer(), nullable=True),
        sa.Column("denominator", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("numerator", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("coverage", sa.Numeric(precision=6, scale=2), server_default=sa.text("0"), nullable=False),
        sa.Column("target_coverage", sa.Numeric(precision=6, scale=2), server_default=sa.text("0"), nullable=False),
        sa.Column("semaphore", sa.String(length=16), nullable=False),
        sa.Column("compliant", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("in_verification_period", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("summary_data", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["upload_id"], ["indicator_uploads.id"], name=op.f("fk_dashboard_summaries_upload_id_indicator_uploads"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_dashboard_summaries")),
        sa.UniqueConstraint("upload_id", "province", "period_key", name="uq_dashboard_summaries_upload_province_period"),
    )
    op.create_index("ix_dashboard_summaries_indicator_period", "dashboard_summaries", ["indicator_code", "period_key"], unique=False)
    op.create_index("ix_dashboard_summaries_upload_province", "dashboard_summaries", ["upload_id", "province"], unique=False)

    op.create_table(
        "indicator_omissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("upload_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("indicator_code", sa.String(length=32), nullable=False),
        sa.Column("province", sa.String(length=120), nullable=True),
        sa.Column("period_key", sa.String(length=32), nullable=True),
        sa.Column("period_label", sa.String(length=80), nullable=True),
        sa.Column("dni", sa.String(length=32), nullable=True),
        sa.Column("cnv", sa.String(length=32), nullable=True),
        sa.Column("patient_name", sa.String(length=255), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("facility", sa.String(length=255), nullable=True),
        sa.Column("components_observed", sa.Text(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("clinical_alerts", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("export_data", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["record_id"], ["indicator_records.id"], name=op.f("fk_indicator_omissions_record_id_indicator_records"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["upload_id"], ["indicator_uploads.id"], name=op.f("fk_indicator_omissions_upload_id_indicator_uploads"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_indicator_omissions")),
        sa.UniqueConstraint("record_id", name="uq_indicator_omissions_record"),
    )
    op.create_index("ix_indicator_omissions_upload_cnv", "indicator_omissions", ["upload_id", "cnv"], unique=False)
    op.create_index("ix_indicator_omissions_upload_dni", "indicator_omissions", ["upload_id", "dni"], unique=False)
    op.create_index("ix_indicator_omissions_upload_period", "indicator_omissions", ["upload_id", "period_key"], unique=False)
    op.create_index("ix_indicator_omissions_upload_province", "indicator_omissions", ["upload_id", "province"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_indicator_omissions_upload_province", table_name="indicator_omissions")
    op.drop_index("ix_indicator_omissions_upload_period", table_name="indicator_omissions")
    op.drop_index("ix_indicator_omissions_upload_dni", table_name="indicator_omissions")
    op.drop_index("ix_indicator_omissions_upload_cnv", table_name="indicator_omissions")
    op.drop_table("indicator_omissions")
    op.drop_index("ix_dashboard_summaries_upload_province", table_name="dashboard_summaries")
    op.drop_index("ix_dashboard_summaries_indicator_period", table_name="dashboard_summaries")
    op.drop_table("dashboard_summaries")
    op.drop_index("ix_component_results_upload_status", table_name="component_results")
    op.drop_index("ix_component_results_upload_component", table_name="component_results")
    op.drop_index("ix_component_results_upload_complies", table_name="component_results")
    op.drop_table("component_results")
    op.drop_index("ix_indicator_records_upload_province", table_name="indicator_records")
    op.drop_index("ix_indicator_records_upload_period", table_name="indicator_records")
    op.drop_index("ix_indicator_records_upload_dni", table_name="indicator_records")
    op.drop_index("ix_indicator_records_upload_cnv", table_name="indicator_records")
    op.drop_index("ix_indicator_records_indicator_dni", table_name="indicator_records")
    op.drop_index("ix_indicator_records_indicator_cnv", table_name="indicator_records")
    op.drop_table("indicator_records")
    op.drop_table("indicator_active_uploads")
    op.drop_index(op.f("ix_indicator_uploads_status"), table_name="indicator_uploads")
    op.drop_index(op.f("ix_indicator_uploads_indicator_code"), table_name="indicator_uploads")
    op.drop_index(op.f("ix_indicator_uploads_file_hash"), table_name="indicator_uploads")
    op.drop_table("indicator_uploads")
