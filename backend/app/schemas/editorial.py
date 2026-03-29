import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.geography import EditorJSData

# --- Hero ---


class HeroUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    subtitle: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=500)
    image: str | None = Field(None, max_length=500)


class HeroFieldAdmin(BaseModel):
    value: str
    updated_at: datetime | None = None


class HeroContentAdmin(BaseModel):
    title: HeroFieldAdmin
    subtitle: HeroFieldAdmin
    description: HeroFieldAdmin
    image: HeroFieldAdmin


class HeroContentPublic(BaseModel):
    title: str
    subtitle: str
    description: str
    image: str | None = None


# --- Body ---


class BodyUpdate(BaseModel):
    content_json: EditorJSData


class BodyContentAdmin(BaseModel):
    content_json: dict | None = None
    updated_at: datetime | None = None


class BodyContentPublic(BaseModel):
    content_json: dict | None = None


# --- Footer About ---


class FooterAboutUpdate(BaseModel):
    content_json: EditorJSData


class FooterAboutContentAdmin(BaseModel):
    content_json: dict | None = None
    updated_at: datetime | None = None


class FooterAboutContentPublic(BaseModel):
    content_json: dict | None = None


# --- Contact ---


class ContactInfoUpdate(BaseModel):
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    address: str | None = Field(None, max_length=500)


class ContactInfoResponse(BaseModel):
    id: uuid.UUID | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ContactInfoPublic(BaseModel):
    email: str | None = None
    phone: str | None = None
    address: str | None = None


# --- Resource Links ---


class ResourceLinkCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., min_length=1, max_length=500)
    sort_order: int = Field(..., ge=0)


class ResourceLinkUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    url: str | None = Field(None, min_length=1, max_length=500)
    sort_order: int | None = Field(None, ge=0)


class ResourceLinkResponse(BaseModel):
    id: uuid.UUID
    title: str
    url: str
    sort_order: int
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ResourceLinkPublic(BaseModel):
    id: uuid.UUID
    title: str
    url: str
    sort_order: int

    model_config = {"from_attributes": True}


class ResourceReorder(BaseModel):
    order: list[uuid.UUID]


# --- Footer Composite ---


class FooterContentAdmin(BaseModel):
    about: FooterAboutContentAdmin
    contact: ContactInfoResponse
    resources: list[ResourceLinkResponse]


class FooterContentPublic(BaseModel):
    about: FooterAboutContentPublic
    contact: ContactInfoPublic
    resources: list[ResourceLinkPublic]


# --- Full Editorial Responses ---


class EditorialAdminResponse(BaseModel):
    hero: HeroContentAdmin
    body: BodyContentAdmin
    footer: FooterContentAdmin


class EditorialPublicResponse(BaseModel):
    hero: HeroContentPublic
    body: BodyContentPublic
    footer: FooterContentPublic
