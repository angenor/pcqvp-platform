import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

SUPPORTED_BLOCK_TYPES = {"header", "paragraph", "image", "table", "list"}


class EditorJSBlock(BaseModel):
    id: str | None = None
    type: str
    data: dict

    @field_validator("type")
    @classmethod
    def validate_block_type(cls, v: str) -> str:
        if v not in SUPPORTED_BLOCK_TYPES:
            raise ValueError(
                f"Type de bloc non supporté: {v}. "
                f"Types acceptés: {', '.join(sorted(SUPPORTED_BLOCK_TYPES))}"
            )
        return v


class EditorJSData(BaseModel):
    time: int | None = None
    blocks: list[EditorJSBlock] = []
    version: str | None = None


# --- Province ---


class ProvinceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    description_json: EditorJSData | None = None


class ProvinceUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    description_json: EditorJSData | None = None


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
    regions: list["RegionList"] = []
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# --- Region ---


class RegionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    province_id: uuid.UUID
    description_json: EditorJSData | None = None


class RegionUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    province_id: uuid.UUID
    description_json: EditorJSData | None = None


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
    communes: list["CommuneList"] = []
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# --- Commune ---


class CommuneCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    region_id: uuid.UUID
    description_json: EditorJSData | None = None


class CommuneUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    region_id: uuid.UUID
    description_json: EditorJSData | None = None


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
    created_at: datetime
    updated_at: datetime | None = None

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
