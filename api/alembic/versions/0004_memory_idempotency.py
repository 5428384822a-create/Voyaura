"""Add memory idempotency key.

Revision ID: 0004_memory_idempotency
Revises: 0003_check_in_source
Create Date: 2026-11-11
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_memory_idempotency"
down_revision: str | None = "0003_check_in_source"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("city_memories") as batch_op:
        batch_op.add_column(sa.Column("client_request_id", sa.Uuid(), nullable=True))
        batch_op.create_unique_constraint(
            "uq_city_memory_user_request", ["user_id", "client_request_id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("city_memories") as batch_op:
        batch_op.drop_constraint("uq_city_memory_user_request", type_="unique")
        batch_op.drop_column("client_request_id")
