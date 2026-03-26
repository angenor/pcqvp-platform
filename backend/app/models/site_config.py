from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import UUIDBase


class SiteConfiguration(UUIDBase):
    __tablename__ = "site_configurations"

    key: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    value: Mapped[str] = mapped_column(Text, nullable=False, default="")
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
