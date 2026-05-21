"""add users roles and permissions

Revision ID: 0003_users_roles_permissions
Revises: 0002_indicator_audit_events
Create Date: 2026-05-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0003_users_roles_permissions"
down_revision: Union[str, None] = "0002_indicator_audit_events"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "app_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("must_change_password", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_app_users")),
        sa.UniqueConstraint("username", name="uq_app_users_username"),
    )
    op.create_index("ix_app_users_active", "app_users", ["is_active"], unique=False)

    op.create_table(
        "app_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_app_roles")),
        sa.UniqueConstraint("code", name="uq_app_roles_code"),
    )

    op.create_table(
        "app_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_app_permissions")),
        sa.UniqueConstraint("code", name="uq_app_permissions_code"),
    )

    op.create_table(
        "app_user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["app_roles.id"], name=op.f("fk_app_user_roles_role_id_app_roles"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"], name=op.f("fk_app_user_roles_user_id_app_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id", name=op.f("pk_app_user_roles")),
        sa.UniqueConstraint("user_id", "role_id", name="uq_app_user_roles_user_role"),
    )
    op.create_index("ix_app_user_roles_role", "app_user_roles", ["role_id"], unique=False)
    op.create_index("ix_app_user_roles_user", "app_user_roles", ["user_id"], unique=False)

    op.create_table(
        "app_role_permissions",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["app_permissions.id"], name=op.f("fk_app_role_permissions_permission_id_app_permissions"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["app_roles.id"], name=op.f("fk_app_role_permissions_role_id_app_roles"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id", name=op.f("pk_app_role_permissions")),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_app_role_permissions_role_permission"),
    )
    op.create_index("ix_app_role_permissions_permission", "app_role_permissions", ["permission_id"], unique=False)
    op.create_index("ix_app_role_permissions_role", "app_role_permissions", ["role_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_app_role_permissions_role", table_name="app_role_permissions")
    op.drop_index("ix_app_role_permissions_permission", table_name="app_role_permissions")
    op.drop_table("app_role_permissions")
    op.drop_index("ix_app_user_roles_user", table_name="app_user_roles")
    op.drop_index("ix_app_user_roles_role", table_name="app_user_roles")
    op.drop_table("app_user_roles")
    op.drop_table("app_permissions")
    op.drop_table("app_roles")
    op.drop_index("ix_app_users_active", table_name="app_users")
    op.drop_table("app_users")
