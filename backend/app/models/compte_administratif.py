import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import UUIDBase


class CollectiviteType(enum.StrEnum):
    province = "province"
    region = "region"
    commune = "commune"


class CompteStatus(enum.StrEnum):
    draft = "draft"
    published = "published"


class CompteAdministratif(UUIDBase):
    __tablename__ = "comptes_administratifs"
    __table_args__ = (
        UniqueConstraint(
            "collectivite_type",
            "collectivite_id",
            "annee_exercice",
            name="uq_compte_collectivite_annee",
        ),
        Index(
            "ix_comptes_collectivite",
            "collectivite_type",
            "collectivite_id",
        ),
        Index("ix_comptes_annee", "annee_exercice"),
    )

    collectivite_type: Mapped[CollectiviteType] = mapped_column(nullable=False)
    collectivite_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    annee_exercice: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[CompteStatus] = mapped_column(
        nullable=False, default=CompteStatus.draft
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    recette_lines: Mapped[list["RecetteLine"]] = relationship(
        back_populates="compte_admin",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    depense_programs: Mapped[list["DepenseProgram"]] = relationship(
        back_populates="compte_admin",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    change_logs: Mapped[list["AccountChangeLog"]] = relationship(
        back_populates="compte_admin",
        lazy="noload",
        cascade="all, delete-orphan",
    )


class RecetteLine(UUIDBase):
    __tablename__ = "recette_lines"
    __table_args__ = (
        UniqueConstraint(
            "compte_admin_id",
            "template_line_id",
            name="uq_recette_compte_template",
        ),
    )

    compte_admin_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("comptes_administratifs.id", ondelete="CASCADE"),
        nullable=False,
    )
    template_line_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("account_template_lines.id", ondelete="RESTRICT"),
        nullable=False,
    )
    values: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}"
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    compte_admin: Mapped["CompteAdministratif"] = relationship(
        back_populates="recette_lines"
    )


class DepenseProgram(UUIDBase):
    __tablename__ = "depense_programs"
    __table_args__ = (
        UniqueConstraint(
            "compte_admin_id", "numero", name="uq_programme_compte_numero"
        ),
    )

    compte_admin_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("comptes_administratifs.id", ondelete="CASCADE"),
        nullable=False,
    )
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    intitule: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    compte_admin: Mapped["CompteAdministratif"] = relationship(
        back_populates="depense_programs"
    )
    depense_lines: Mapped[list["DepenseLine"]] = relationship(
        back_populates="programme",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class DepenseLine(UUIDBase):
    __tablename__ = "depense_lines"
    __table_args__ = (
        UniqueConstraint(
            "programme_id",
            "template_line_id",
            name="uq_depense_programme_template",
        ),
    )

    programme_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("depense_programs.id", ondelete="CASCADE"),
        nullable=False,
    )
    template_line_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("account_template_lines.id", ondelete="RESTRICT"),
        nullable=False,
    )
    values: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}"
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    programme: Mapped["DepenseProgram"] = relationship(
        back_populates="depense_lines"
    )


class AccountChangeLog(UUIDBase):
    __tablename__ = "account_change_logs"
    __table_args__ = (
        Index(
            "ix_changelog_compte_date",
            "compte_admin_id",
            "created_at",
        ),
    )

    compte_admin_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("comptes_administratifs.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    change_type: Mapped[str] = mapped_column(String(50), nullable=False)
    detail: Mapped[dict] = mapped_column(JSONB, nullable=False)

    compte_admin: Mapped["CompteAdministratif"] = relationship(
        back_populates="change_logs"
    )
