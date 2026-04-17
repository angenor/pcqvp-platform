import uuid

from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import UUIDBase


class AuditLog(UUIDBase):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index(
            "ix_audit_logs_action_created",
            "action",
            text("created_at DESC"),
        ),
        Index(
            "ix_audit_logs_actor_created",
            "actor_user_id",
            text("created_at DESC"),
        ),
    )

    actor_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    target_type: Mapped[str] = mapped_column(String(100), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    payload: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}"
    )
