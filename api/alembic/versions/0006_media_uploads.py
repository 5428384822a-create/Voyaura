"""Add secure media upload lifecycle fields.

Revision ID: 0006_media_uploads
Revises: 0005_memory_mutations
Create Date: 2026-11-11
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_media_uploads"
down_revision: str | None = "0005_memory_mutations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("media_assets") as batch_op:
        batch_op.add_column(sa.Column("client_request_id", sa.Uuid(), nullable=True))
        batch_op.add_column(
            sa.Column("visibility", sa.String(length=20), server_default="private", nullable=False)
        )
        batch_op.add_column(
            sa.Column("upload_status", sa.String(length=20), server_default="ready", nullable=False)
        )
        batch_op.add_column(
            sa.Column(
                "exif_status", sa.String(length=24), server_default="not_applicable", nullable=False
            )
        )
        batch_op.add_column(sa.Column("failure_code", sa.String(length=64)))
        batch_op.add_column(
            sa.Column("upload_expires_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=True))
    with op.batch_alter_table("media_assets") as batch_op:
        batch_op.create_unique_constraint("uq_media_asset_client_request", ["client_request_id"])
        batch_op.alter_column("visibility", server_default=None)
        batch_op.alter_column("upload_status", server_default=None)
        batch_op.alter_column("exif_status", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("media_assets") as batch_op:
        batch_op.drop_constraint("uq_media_asset_client_request", type_="unique")
        batch_op.drop_column("uploaded_at")
        batch_op.drop_column("upload_expires_at")
        batch_op.drop_column("failure_code")
        batch_op.drop_column("exif_status")
        batch_op.drop_column("upload_status")
        batch_op.drop_column("visibility")
        batch_op.drop_column("client_request_id")
