from datetime import datetime

from pydantic import BaseModel


class ConfigResponse(BaseModel):
    key: str
    value: str
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ConfigUpdateRequest(BaseModel):
    value: str


class GlobalLeaksPublicResponse(BaseModel):
    url: str
