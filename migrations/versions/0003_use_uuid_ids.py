"""Use UUID for all primary and foreign keys

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-01 00:00:00.000000
"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop tables in dependency order
    op.drop_table("user_claims")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_table("claims")
    op.drop_table("roles")

    # Recreate with UUID primary/foreign keys
    op.create_table(
        "roles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("description"),
    )

    op.create_table(
        "claims",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "user_claims",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("claim_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "claim_id"),
    )

    # Re-seed default roles with Python-generated UUIDs
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "INSERT INTO roles (id, description) VALUES "
            "(:id1, 'admin'), (:id2, 'manager'), (:id3, 'user'), (:id4, 'guest')"
        ),
        {
            "id1": str(uuid.uuid4()),
            "id2": str(uuid.uuid4()),
            "id3": str(uuid.uuid4()),
            "id4": str(uuid.uuid4()),
        },
    )


def downgrade() -> None:
    op.drop_table("user_claims")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_table("claims")
    op.drop_table("roles")

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("description", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("description"),
    )

    op.create_table(
        "claims",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("description", sa.String(length=200), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "user_claims",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("claim_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "claim_id"),
    )

    op.execute(
        "INSERT INTO roles (description) VALUES "
        "('admin'), ('manager'), ('user'), ('guest')"
    )
