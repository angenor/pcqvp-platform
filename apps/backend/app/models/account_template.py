import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import UUIDBase


class TemplateType(enum.StrEnum):
    recette = "recette"
    depense = "depense"


class SectionType(enum.StrEnum):
    fonctionnement = "fonctionnement"
    investissement = "investissement"


class ColumnDataType(enum.StrEnum):
    number = "number"
    text = "text"
    percentage = "percentage"


class AccountTemplate(UUIDBase):
    __tablename__ = "account_templates"
    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_template_name_version"),
        Index("ix_account_templates_type", "type"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[TemplateType] = mapped_column(nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    lines: Mapped[list["AccountTemplateLine"]] = relationship(
        back_populates="template",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    columns: Mapped[list["AccountTemplateColumn"]] = relationship(
        back_populates="template",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class AccountTemplateLine(UUIDBase):
    __tablename__ = "account_template_lines"
    __table_args__ = (
        UniqueConstraint(
            "template_id", "compte_code", name="uq_line_template_code"
        ),
        CheckConstraint("level IN (1, 2, 3)", name="ck_line_level"),
        Index("ix_lines_template_level", "template_id", "level"),
        Index("ix_lines_template_parent", "template_id", "parent_code"),
        Index("ix_lines_template_section", "template_id", "section"),
    )

    template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("account_templates.id", ondelete="CASCADE"), nullable=False
    )
    compte_code: Mapped[str] = mapped_column(String(10), nullable=False)
    intitule: Mapped[str] = mapped_column(String(500), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_code: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )
    section: Mapped[SectionType] = mapped_column(nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    template: Mapped["AccountTemplate"] = relationship(
        back_populates="lines"
    )


class AccountTemplateColumn(UUIDBase):
    __tablename__ = "account_template_columns"
    __table_args__ = (
        UniqueConstraint(
            "template_id", "code", name="uq_column_template_code"
        ),
        Index("ix_columns_template_id", "template_id"),
    )

    template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("account_templates.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    data_type: Mapped[ColumnDataType] = mapped_column(nullable=False)
    is_computed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    formula: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    template: Mapped["AccountTemplate"] = relationship(
        back_populates="columns"
    )
