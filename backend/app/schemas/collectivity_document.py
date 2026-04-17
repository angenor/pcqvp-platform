import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

ALLOWED_DOCUMENT_MIME_TYPES: tuple[str, ...] = (
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

MAX_DOCUMENT_SIZE_BYTES: int = 20 * 1024 * 1024

ParentType = Literal["province", "region", "commune"]


class CollectivityDocumentCreate(BaseModel):
    parent_type: ParentType
    parent_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    file_path: str = Field(min_length=1, max_length=500)
    file_mime: str = Field(min_length=1, max_length=127)
    file_size_bytes: int = Field(ge=1, le=MAX_DOCUMENT_SIZE_BYTES)

    @field_validator("title")
    @classmethod
    def _strip_title(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("title must not be empty")
        return trimmed

    @field_validator("file_mime")
    @classmethod
    def _validate_mime(cls, v: str) -> str:
        if v not in ALLOWED_DOCUMENT_MIME_TYPES:
            raise ValueError(
                "file_mime non autorise. Types acceptes : PDF, DOC, DOCX, XLS, XLSX"
            )
        return v


class CollectivityDocumentUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)

    @field_validator("title")
    @classmethod
    def _strip_title(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("title must not be empty")
        return trimmed


class CollectivityDocumentFileReplace(BaseModel):
    file_path: str = Field(min_length=1, max_length=500)
    file_mime: str = Field(min_length=1, max_length=127)
    file_size_bytes: int = Field(ge=1, le=MAX_DOCUMENT_SIZE_BYTES)

    @field_validator("file_mime")
    @classmethod
    def _validate_mime(cls, v: str) -> str:
        if v not in ALLOWED_DOCUMENT_MIME_TYPES:
            raise ValueError(
                "file_mime non autorise. Types acceptes : PDF, DOC, DOCX, XLS, XLSX"
            )
        return v


class CollectivityDocumentsReorder(BaseModel):
    parent_type: ParentType
    parent_id: uuid.UUID
    ordered_ids: list[uuid.UUID] = Field(min_length=1)


class CollectivityDocumentRead(BaseModel):
    id: uuid.UUID
    parent_type: ParentType
    parent_id: uuid.UUID
    title: str
    file_path: str
    file_mime: str
    file_size_bytes: int
    position: int
    download_url: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
