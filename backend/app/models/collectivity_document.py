import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.models.base import UUIDBase


class CollectivityDocument(UUIDBase):
    __tablename__ = "collectivity_documents"
    __table_args__ = (
        CheckConstraint(
            "((province_id IS NOT NULL)::int + (region_id IS NOT NULL)::int "
            "+ (commune_id IS NOT NULL)::int) = 1",
            name="ck_collectivity_documents_parent_exclusive",
        ),
        Index(
            "ix_collectivity_documents_province_position",
            "province_id",
            "position",
            postgresql_where=text("province_id IS NOT NULL"),
        ),
        Index(
            "ix_collectivity_documents_region_position",
            "region_id",
            "position",
            postgresql_where=text("region_id IS NOT NULL"),
        ),
        Index(
            "ix_collectivity_documents_commune_position",
            "commune_id",
            "position",
            postgresql_where=text("commune_id IS NOT NULL"),
        ),
    )

    province_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("provinces.id", ondelete="CASCADE"), nullable=True
    )
    region_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("regions.id", ondelete="CASCADE"), nullable=True
    )
    commune_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("communes.id", ondelete="CASCADE"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_mime: Mapped[str] = mapped_column(String(127), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    position: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    province: Mapped["Province | None"] = relationship(  # noqa: F821
        "Province", lazy="selectin"
    )
    region: Mapped["Region | None"] = relationship(  # noqa: F821
        "Region", lazy="selectin"
    )
    commune: Mapped["Commune | None"] = relationship(  # noqa: F821
        "Commune", lazy="selectin"
    )

    @validates("province_id", "region_id", "commune_id")
    def _validate_parent_exclusive(self, key: str, value):
        """Ensure exactly one FK is set at the ORM level.

        Why: fail fast before hitting the DB CHECK constraint.
        How to apply: runs on every assignment of any FK field.
        """
        other_keys = {"province_id", "region_id", "commune_id"} - {key}
        if value is not None:
            for other in other_keys:
                if getattr(self, other, None) is not None:
                    raise ValueError(
                        "collectivity_document: exactly one of "
                        "province_id/region_id/commune_id must be set"
                    )
        return value

    @property
    def parent_type(self) -> str:
        if self.province_id is not None:
            return "province"
        if self.region_id is not None:
            return "region"
        return "commune"

    @property
    def parent_id(self) -> uuid.UUID:
        return self.province_id or self.region_id or self.commune_id  # type: ignore[return-value]
