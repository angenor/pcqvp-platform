import uuid

from sqlalchemy import BigInteger, Boolean, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import UUIDBase


class GeodataVersion(UUIDBase):
    __tablename__ = "geodata_versions"
    __table_args__ = (
        Index(
            "uq_geodata_version_one_active",
            "is_active",
            unique=True,
            postgresql_where=text("is_active IS TRUE"),
        ),
        Index(
            "ix_geodata_versions_active_lookup",
            "is_active",
            postgresql_where=text("is_active IS TRUE"),
        ),
        Index(
            "ix_geodata_versions_created_at",
            text("created_at DESC"),
        ),
        Index(
            "ix_geodata_versions_created_by",
            "created_by_user_id",
            text("created_at DESC"),
        ),
    )

    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    processed_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    features_count: Mapped[int] = mapped_column(Integer, nullable=False)
    region_names: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="'[]'::jsonb"
    )
    geojson_processed: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    warnings: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="'[]'::jsonb"
    )
