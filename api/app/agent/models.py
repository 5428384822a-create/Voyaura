import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models import utcnow


class AgentRun(Base):
    __tablename__ = "agent_runs"
    __table_args__ = (
        UniqueConstraint("user_id", "client_request_id", name="uq_agent_run_user_request"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    client_request_id: Mapped[uuid.UUID] = mapped_column()
    input_hash: Mapped[str] = mapped_column(String(64))
    kind: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(40), default="running")
    revision: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(String(160))
    request_snapshot: Mapped[dict] = mapped_column(JSON)
    result_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    events: Mapped[list] = mapped_column(JSON, default=list)
    confirmation_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    content_digest: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confirmation_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SavedArtifact(Base):
    __tablename__ = "agent_artifacts"
    __table_args__ = (UniqueConstraint("run_id", name="uq_agent_artifact_run"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_runs.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(16))
    title: Mapped[str] = mapped_column(String(160))
    content: Mapped[dict] = mapped_column(JSON)
    content_digest: Mapped[str] = mapped_column(String(64))
    acknowledgement: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
