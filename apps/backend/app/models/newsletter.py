import enum
from datetime import datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import UUIDBase


class SubscriberStatus(enum.StrEnum):
    en_attente = "en_attente"
    actif = "actif"
    desinscrit = "desinscrit"


class NewsletterSubscriber(UUIDBase):
    __tablename__ = "newsletter_subscribers"
    __table_args__ = (Index("ix_newsletter_subscribers_status", "status"),)

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    status: Mapped[SubscriberStatus] = mapped_column(
        String(20), nullable=False, default=SubscriberStatus.en_attente
    )
    unsubscribe_token: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    unsubscribed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
