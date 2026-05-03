import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class GeodataWarning(BaseModel):
    code: Literal[
        "FEATURE_COUNT_OUT_OF_RANGE",
        "REGION_NOT_IN_DATABASE",
        "DUPLICATE_NAME_DROPPED",
        "FEATURE_TOO_SMALL_DROPPED",
        "GEOMETRY_FIXED",
    ]
    message: str
    details: dict[str, Any] | None = None


class GeodataAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: EmailStr


class GeodataUploadResponse(BaseModel):
    version_id: uuid.UUID
    uploaded_at: datetime
    original_filename: str
    original_size_bytes: int
    processed_size_bytes: int
    features_count: int
    region_names: list[str]
    warnings: list[GeodataWarning]
    is_active: Literal[False] = False
    notes: str | None = None


class GeodataJobAccepted(BaseModel):
    job_id: uuid.UUID
    status: Literal["pending", "running"]
    submitted_at: datetime


class GeodataJobStatus(BaseModel):
    job_id: uuid.UUID
    status: Literal["pending", "running", "done", "failed"]
    submitted_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    version_id: uuid.UUID | None = None
    error_message: str | None = None


class GeodataVersionListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    created_by: GeodataAuthor
    original_filename: str
    original_size_bytes: int
    processed_size_bytes: int
    features_count: int
    is_active: bool
    has_warnings: bool
    notes: str | None = None


class GeodataVersionDetail(GeodataVersionListItem):
    region_names: list[str] = Field(default_factory=list)
    warnings: list[GeodataWarning] = Field(default_factory=list)
    geojson_processed: dict[str, Any]


class GeodataVersionList(BaseModel):
    items: list[GeodataVersionListItem]
    total: int


class GeodataActivateResponse(GeodataVersionDetail):
    pass


class GeodataErrorResponse(BaseModel):
    detail: str
    code: str | None = None
