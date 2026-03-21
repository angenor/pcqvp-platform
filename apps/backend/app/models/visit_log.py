import enum
import uuid

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import UUIDBase


class EventType(enum.StrEnum):
    page_view = "page_view"
    download = "download"


class VisitLog(UUIDBase):
    __tablename__ = "visit_logs"
    __table_args__ = (
        Index("ix_visit_logs_created_at", "created_at"),
        Index("ix_visit_logs_event_type", "event_type"),
        Index("ix_visit_logs_page_type", "page_type"),
    )

    event_type: Mapped[str] = mapped_column(String(20), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    page_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    collectivite_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    collectivite_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    download_format: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
