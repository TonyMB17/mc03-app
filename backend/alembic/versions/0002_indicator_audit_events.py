"""add indicator audit events

Revision ID: 0002_indicator_audit_events
Revises: 0001_indicator_storage
Create Date: 2026-05-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0002_indicator_audit_events"
down_revision: Union[str, None] = "0001_indicator_storage"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "indicator_audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("indicator_code", sa.String(length=32), nullable=False),
        sa.Column("upload_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("actor", sa.String(length=120), nullable=True),
        sa.Column("actor_role", sa.String(length=64), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["upload_id"], ["indicator_uploads.id"], name=op.f("fk_indicator_audit_events_upload_id_indicator_uploads"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_indicator_audit_events")),
    )
    op.create_index("ix_indicator_audit_events_event_type", "indicator_audit_events", ["event_type"], unique=False)
    op.create_index("ix_indicator_audit_events_indicator_created", "indicator_audit_events", ["indicator_code", "created_at"], unique=False)
    op.create_index("ix_indicator_audit_events_upload", "indicator_audit_events", ["upload_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_indicator_audit_events_upload", table_name="indicator_audit_events")
    op.drop_index("ix_indicator_audit_events_indicator_created", table_name="indicator_audit_events")
    op.drop_index("ix_indicator_audit_events_event_type", table_name="indicator_audit_events")
    op.drop_table("indicator_audit_events")
