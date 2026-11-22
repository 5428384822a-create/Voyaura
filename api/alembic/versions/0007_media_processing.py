"""Add queued media processing state.

Revision ID: 0007_media_processing
Revises: 0006_media_uploads
Create Date: 2026-11-11
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007_media_processing"
down_revision: str | None = "0006_media_uploads"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("media_assets") as batch_op:
        batch_op.add_column(
            sa.Column(
                "scan_status", sa.String(length=20), server_default="not_scanned", nullable=False
            )
        )
        batch_op.add_column(sa.Column("processing_error", sa.String(length=500)))
        batch_op.add_column(sa.Column("thumbnail_mime_type", sa.String(length=100)))
        batch_op.add_column(sa.Column("thumbnail_width", sa.Integer()))
        batch_op.add_column(sa.Column("thumbnail_height", sa.Integer()))
        batch_op.add_column(sa.Column("processed_at", sa.DateTime(timezone=True)))
    with op.batch_alter_table("media_assets") as batch_op:
        batch_op.alter_column("scan_status", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("media_assets") as batch_op:
        batch_op.drop_column("processed_at")
        batch_op.drop_column("thumbnail_height")
        batch_op.drop_column("thumbnail_width")
        batch_op.drop_column("thumbnail_mime_type")
        batch_op.drop_column("processing_error")
        batch_op.drop_column("scan_status")
