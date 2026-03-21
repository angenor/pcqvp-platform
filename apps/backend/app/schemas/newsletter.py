from datetime import datetime

from pydantic import BaseModel, EmailStr


class SubscribeRequest(BaseModel):
    email: EmailStr


class SubscribeResponse(BaseModel):
    message: str


class ConfirmResponse(BaseModel):
    message: str


class SubscriberResponse(BaseModel):
    id: str
    email: str
    status: str
    confirmed_at: datetime | None = None
    unsubscribed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedSubscribers(BaseModel):
    items: list[SubscriberResponse]
    total: int
    page: int
    per_page: int
