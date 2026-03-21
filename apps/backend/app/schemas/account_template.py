import uuid
from datetime import datetime

from pydantic import BaseModel, Field

# --- Line ---


class TemplateLineCreate(BaseModel):
    compte_code: str = Field(min_length=1, max_length=10)
    intitule: str = Field(min_length=1, max_length=500)
    level: int = Field(ge=1, le=3)
    parent_code: str | None = None
    section: str = Field(pattern="^(fonctionnement|investissement)$")
    sort_order: int


class TemplateLineUpdate(BaseModel):
    id: uuid.UUID
    compte_code: str = Field(min_length=1, max_length=10)
    intitule: str = Field(min_length=1, max_length=500)
    level: int = Field(ge=1, le=3)
    parent_code: str | None = None
    section: str = Field(pattern="^(fonctionnement|investissement)$")
    sort_order: int


class TemplateLineResponse(BaseModel):
    id: uuid.UUID
    compte_code: str
    intitule: str
    level: int
    parent_code: str | None
    section: str
    sort_order: int

    model_config = {"from_attributes": True}


# --- Column ---


class TemplateColumnUpdate(BaseModel):
    id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=50)
    data_type: str = Field(pattern="^(number|text|percentage)$")
    is_computed: bool = False
    formula: str | None = None
    sort_order: int


class TemplateColumnResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    data_type: str
    is_computed: bool
    formula: str | None
    sort_order: int

    model_config = {"from_attributes": True}


# --- Template ---


class TemplateListItem(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    version: int
    is_active: bool
    lines_count: int = 0
    columns_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class TemplateDetail(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None
    lines: list[TemplateLineResponse] = []
    columns: list[TemplateColumnResponse] = []

    model_config = {"from_attributes": True}


class TemplateListResponse(BaseModel):
    items: list[TemplateListItem]
    total: int
