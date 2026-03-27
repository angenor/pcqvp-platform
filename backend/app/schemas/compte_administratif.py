import uuid
from datetime import datetime

from pydantic import BaseModel, Field

# --- Compte ---


class CompteCreate(BaseModel):
    collectivite_type: str = Field(pattern="^(province|region|commune)$")
    collectivite_id: uuid.UUID
    annee_exercice: int = Field(ge=1900, le=2100)


class CompteUpdate(BaseModel):
    collectivite_type: str | None = Field(default=None, pattern="^(province|region|commune)$")
    collectivite_id: uuid.UUID | None = None
    annee_exercice: int | None = Field(default=None, ge=1900, le=2100)


class CompteListItem(BaseModel):
    id: uuid.UUID
    collectivite_type: str
    collectivite_id: uuid.UUID
    collectivite_name: str = ""
    annee_exercice: int
    status: str
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class CompteListResponse(BaseModel):
    items: list[CompteListItem]
    total: int


# --- Programme ---


class DepenseProgramCreate(BaseModel):
    intitule: str = Field(min_length=1, max_length=255)


class DepenseProgramUpdate(BaseModel):
    intitule: str = Field(min_length=1, max_length=255)


class DepenseProgramResponse(BaseModel):
    id: uuid.UUID
    numero: int
    intitule: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# --- Recette ---


class RecetteLineUpsert(BaseModel):
    template_line_id: uuid.UUID
    values: dict = Field(default_factory=dict)


class RecetteLineResponse(BaseModel):
    id: uuid.UUID
    template_line_id: uuid.UUID
    values: dict
    computed: dict = Field(default_factory=dict)

    model_config = {"from_attributes": True}


# --- Depense ---


class DepenseLineUpsert(BaseModel):
    template_line_id: uuid.UUID
    values: dict = Field(default_factory=dict)


class DepenseLineResponse(BaseModel):
    id: uuid.UUID
    template_line_id: uuid.UUID
    values: dict
    computed: dict = Field(default_factory=dict)

    model_config = {"from_attributes": True}


# --- Status ---


class StatusUpdate(BaseModel):
    status: str = Field(pattern="^(draft|published)$")


class StatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# --- Changelog ---


class ChangeLogEntry(BaseModel):
    id: uuid.UUID
    user_email: str = ""
    change_type: str
    detail: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class ChangeLogResponse(BaseModel):
    items: list[ChangeLogEntry]
    total: int


# --- Recapitulatifs ---


class RecapRecettesResponse(BaseModel):
    sections: list[dict]


class RecapDepensesResponse(BaseModel):
    sections: list[dict]
    programmes: list[DepenseProgramResponse]


class EquilibreResponse(BaseModel):
    fonctionnement: dict
    investissement: dict
    resultat_definitif: float


# --- Detail complet ---


class CompteDetail(BaseModel):
    id: uuid.UUID
    collectivite_type: str
    collectivite_id: uuid.UUID
    collectivite_name: str = ""
    annee_exercice: int
    status: str
    created_by: uuid.UUID
    programmes: list[DepenseProgramResponse] = []
    recettes: dict | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
