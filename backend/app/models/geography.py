import uuid
from datetime import datetime

from sqlalchemy import Computed, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import UUIDBase


class Province(UUIDBase):
    __tablename__ = "provinces"
    __table_args__ = (
        Index("ix_provinces_search_vector", "search_vector", postgresql_using="gin"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    description_json: Mapped[list] = mapped_column(
        JSONB, default=list, server_default="[]"
    )
    banner_image: Mapped[str | None] = mapped_column(
        String(500), nullable=True, default=None
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('fr_unaccent', coalesce(name, ''))", persisted=True
        ),
    )

    regions: Mapped[list["Region"]] = relationship(
        back_populates="province", lazy="selectin"
    )


class Region(UUIDBase):
    __tablename__ = "regions"
    __table_args__ = (
        Index("ix_regions_province_id", "province_id"),
        Index("ix_regions_search_vector", "search_vector", postgresql_using="gin"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    province_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("provinces.id", ondelete="RESTRICT"), nullable=False
    )
    description_json: Mapped[list] = mapped_column(
        JSONB, default=list, server_default="[]"
    )
    banner_image: Mapped[str | None] = mapped_column(
        String(500), nullable=True, default=None
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('fr_unaccent', coalesce(name, ''))", persisted=True
        ),
    )

    province: Mapped["Province"] = relationship(back_populates="regions")
    communes: Mapped[list["Commune"]] = relationship(
        back_populates="region", lazy="selectin"
    )


class Commune(UUIDBase):
    __tablename__ = "communes"
    __table_args__ = (
        Index("ix_communes_region_id", "region_id"),
        Index("ix_communes_search_vector", "search_vector", postgresql_using="gin"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    region_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("regions.id", ondelete="RESTRICT"), nullable=False
    )
    description_json: Mapped[list] = mapped_column(
        JSONB, default=list, server_default="[]"
    )
    banner_image: Mapped[str | None] = mapped_column(
        String(500), nullable=True, default=None
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('fr_unaccent', coalesce(name, ''))", persisted=True
        ),
    )

    region: Mapped["Region"] = relationship(back_populates="communes")
