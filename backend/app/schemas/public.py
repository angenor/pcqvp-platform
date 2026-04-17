import uuid

from pydantic import BaseModel

from app.schemas.collectivity_document import CollectivityDocumentRead


class PublicAnneesResponse(BaseModel):
    annees: list[int]


class PublicDescriptionResponse(BaseModel):
    name: str
    type: str
    description_json: list[dict] | dict | None = []
    banner_image: str | None = None
    documents: list[CollectivityDocumentRead] = []


class PublicTemplateColumn(BaseModel):
    code: str
    name: str
    is_computed: bool


class PublicLineData(BaseModel):
    template_line_id: str
    compte_code: str
    intitule: str
    level: int
    section: str
    values: dict
    computed: dict
    children: list["PublicLineData"] = []


class PublicSection(BaseModel):
    section: str
    lines: list[PublicLineData]


class PublicCompteInfo(BaseModel):
    id: uuid.UUID
    collectivite_type: str
    collectivite_id: uuid.UUID
    collectivite_name: str
    annee_exercice: int
    status: str


class PublicProgramme(BaseModel):
    id: str
    numero: int
    intitule: str
    sections: list[PublicSection]


class PublicCompteResponse(BaseModel):
    compte: PublicCompteInfo
    recettes: dict
    depenses: dict
    recapitulatifs: dict
    equilibre: dict


class PublicParentDocument(BaseModel):
    type: str
    id: uuid.UUID
    name: str
    annees: list[int]
    documents: list[CollectivityDocumentRead] = []


class PublicDocumentsLiesResponse(BaseModel):
    parents: list[PublicParentDocument]
