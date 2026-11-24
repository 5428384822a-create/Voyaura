"""Add city visit source.

Revision ID: 0003_check_in_source
Revises: 0002_city_memories
Create Date: 2026-11-11
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_check_in_source"
down_revision: str | None = "0002_city_memories"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("city_visits") as batch_op:
        batch_op.add_column(
            sa.Column(
                "check_in_source", sa.String(length=20), nullable=False, server_default="device"
            )
        )
    # Flush the ADD first: existing rows must receive the temporary default
    # before SQLite recreates the table without a server default.
    with op.batch_alter_table("city_visits") as batch_op:
        batch_op.alter_column("check_in_source", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("city_visits") as batch_op:
        batch_op.drop_column("check_in_source")
