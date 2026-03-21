from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    q: str = Field(..., min_length=2, max_length=200)
    limit: int = Field(10, ge=1, le=20)


class SearchResultItem(BaseModel):
    id: str
    name: str
    type: str
    parent_name: str | None = None
    url: str


class SearchCompteItem(BaseModel):
    id: str
    collectivite_name: str
    collectivite_type: str
    annee_exercice: int
    url: str


class SearchResponse(BaseModel):
    results: dict[str, list]
    total: int
