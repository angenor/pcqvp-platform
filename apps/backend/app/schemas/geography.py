import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HeadingBlock(BaseModel):
    type: Literal["heading"] = "heading"
    content: str


class ParagraphBlock(BaseModel):
    type: Literal["paragraph"] = "paragraph"
    content: str


class ImageBlock(BaseModel):
    type: Literal["image"] = "image"
    url: str
    alt: str | None = None


RichContentBlock = HeadingBlock | ParagraphBlock | ImageBlock


# --- Province ---


class ProvinceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    description_json: list[RichContentBlock] = []


class ProvinceUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    description_json: list[RichContentBlock] = []


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
    description_json: list[RichContentBlock]
    regions: list["RegionList"] = []
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# --- Region ---


class RegionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    province_id: uuid.UUID
    description_json: list[RichContentBlock] = []


class RegionUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    province_id: uuid.UUID
    description_json: list[RichContentBlock] = []


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
    description_json: list[RichContentBlock]
    communes: list["CommuneList"] = []
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# --- Commune ---


class CommuneCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    region_id: uuid.UUID
    description_json: list[RichContentBlock] = []


class CommuneUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=20)
    region_id: uuid.UUID
    description_json: list[RichContentBlock] = []


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
    description_json: list[RichContentBlock]
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
