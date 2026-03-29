import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

SUPPORTED_BLOCK_TYPES = {
    "header",
    "paragraph",
    "image",
    "table",
    "list",
    "quote",
    "delimiter",
    "embed",
    "checklist",
}


class EditorJSBlock(BaseModel):
    id: str | None = None
    type: str
    data: dict
    tunes: dict | None = None

    @field_validator("type")
    @classmethod
    def validate_block_type(cls, v: str) -> str:
        if v not in SUPPORTED_BLOCK_TYPES:
            raise ValueError(
                f"Type de bloc non supporté: {v}. "
                f"Types acceptés: "
                f"{', '.join(sorted(SUPPORTED_BLOCK_TYPES))}"
            )
        return v


class EditorJSData(BaseModel):
    time: int | None = None
    blocks: list[EditorJSBlock] = []
    version: str | None = None


def _convert_legacy_block(block: dict) -> dict:
    """Convert old format block to EditorJS block."""
    old_type = block.get("type", "paragraph")
    if old_type == "heading":
        return {
            "type": "header",
            "data": {"text": block.get("content", ""), "level": 2},
        }
    elif old_type == "image":
        return {
            "type": "image",
            "data": {
                "file": {"url": block.get("url", "")},
                "caption": block.get("alt", ""),
            },
        }
    else:
        return {
            "type": "paragraph",
            "data": {"text": block.get("content", "")},
        }


def parse_description_json(v: Any) -> EditorJSData | None:
    """Parse description_json, handling both old and new formats."""
    if v is None:
        return None
    if isinstance(v, EditorJSData):
        return v
    if isinstance(v, dict) and "blocks" in v:
        return EditorJSData(**v)
    if isinstance(v, list):
        if not v:
            return None
        blocks = [_convert_legacy_block(b) for b in v]
        return EditorJSData(blocks=blocks)
    return None


# --- Province ---


class ProvinceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    description_json: EditorJSData | None = None
    banner_image: str | None = None


class ProvinceUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    description_json: EditorJSData | None = None
    banner_image: str | None = None


class ProvinceList(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProvinceDetail(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    description_json: EditorJSData | None = None
    banner_image: str | None = None
    regions: list["RegionList"] = []
    created_at: datetime
    updated_at: datetime | None = None

    @field_validator("description_json", mode="before")
    @classmethod
    def parse_desc(cls, v: Any) -> EditorJSData | None:
        return parse_description_json(v)

    model_config = {"from_attributes": True}


# --- Region ---


class RegionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    province_id: uuid.UUID
    description_json: EditorJSData | None = None
    banner_image: str | None = None


class RegionUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    province_id: uuid.UUID
    description_json: EditorJSData | None = None
    banner_image: str | None = None


class RegionList(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    province_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class RegionDetail(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    province_id: uuid.UUID
    description_json: EditorJSData | None = None
    banner_image: str | None = None
    communes: list["CommuneList"] = []
    created_at: datetime
    updated_at: datetime | None = None

    @field_validator("description_json", mode="before")
    @classmethod
    def parse_desc(cls, v: Any) -> EditorJSData | None:
        return parse_description_json(v)

    model_config = {"from_attributes": True}


# --- Commune ---


class CommuneCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    region_id: uuid.UUID
    description_json: EditorJSData | None = None
    banner_image: str | None = None


class CommuneUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    region_id: uuid.UUID
    description_json: EditorJSData | None = None
    banner_image: str | None = None


class CommuneList(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    region_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class CommuneDetail(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    region_id: uuid.UUID
    description_json: EditorJSData | None = None
    banner_image: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    @field_validator("description_json", mode="before")
    @classmethod
    def parse_desc(cls, v: Any) -> EditorJSData | None:
        return parse_description_json(v)

    model_config = {"from_attributes": True}


# --- Pagination ---
class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int


# --- Hierarchy ---


class HierarchyCommuneItem(BaseModel):
    id: uuid.UUID
    name: str
    code: str

    model_config = {"from_attributes": True}


class HierarchyRegion(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    communes: list[HierarchyCommuneItem] = []

    model_config = {"from_attributes": True}


class HierarchyProvince(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    regions: list[HierarchyRegion] = []

    model_config = {"from_attributes": True}
