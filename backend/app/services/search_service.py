import re

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.compte_administratif import CompteAdministratif, CompteStatus
from app.models.geography import Commune, Province, Region
from app.schemas.search import SearchCompteItem, SearchResponse, SearchResultItem


def _sanitize_query(q: str) -> str:
    q = re.sub(r"[^\w\s'-]", "", q, flags=re.UNICODE)
    return q.strip()


async def search_fulltext(
    db: AsyncSession, query: str, limit: int = 10
) -> SearchResponse:
    sanitized = _sanitize_query(query)
    if len(sanitized) < 2:
        return SearchResponse(results={"collectivites": [], "comptes": []}, total=0)

    ts_query = func.plainto_tsquery("fr_unaccent", sanitized)

    collectivites: list[SearchResultItem] = []

    # Search provinces
    stmt = (
        select(
            Province.id,
            Province.name,
            func.ts_rank(Province.search_vector, ts_query).label("rank"),
        )
        .where(Province.search_vector.op("@@")(ts_query))
        .order_by(text("rank DESC"))
        .limit(limit)
    )
    result = await db.execute(stmt)
    for row in result:
        collectivites.append(
            SearchResultItem(
                id=str(row.id),
                name=row.name,
                type="province",
                parent_name=None,
                url=f"/provinces/{row.id}",
            )
        )

    # Search regions
    stmt = (
        select(
            Region.id,
            Region.name,
            Province.name.label("parent_name"),
            func.ts_rank(Region.search_vector, ts_query).label("rank"),
        )
        .join(Province, Region.province_id == Province.id)
        .where(Region.search_vector.op("@@")(ts_query))
        .order_by(text("rank DESC"))
        .limit(limit)
    )
    result = await db.execute(stmt)
    for row in result:
        collectivites.append(
            SearchResultItem(
                id=str(row.id),
                name=row.name,
                type="region",
                parent_name=row.parent_name,
                url=f"/regions/{row.id}",
            )
        )

    # Search communes
    stmt = (
        select(
            Commune.id,
            Commune.name,
            Region.name.label("parent_name"),
            func.ts_rank(Commune.search_vector, ts_query).label("rank"),
        )
        .join(Region, Commune.region_id == Region.id)
        .where(Commune.search_vector.op("@@")(ts_query))
        .order_by(text("rank DESC"))
        .limit(limit)
    )
    result = await db.execute(stmt)
    for row in result:
        collectivites.append(
            SearchResultItem(
                id=str(row.id),
                name=row.name,
                type="commune",
                parent_name=row.parent_name,
                url=f"/communes/{row.id}",
            )
        )

    # Sort all collectivites and truncate
    collectivites.sort(key=lambda x: x.name)
    collectivites = collectivites[:limit]

    # Search comptes (published only, via commune name)
    comptes: list[SearchCompteItem] = []
    stmt = (
        select(
            CompteAdministratif.id,
            Commune.name.label("commune_name"),
            CompteAdministratif.collectivite_type,
            CompteAdministratif.annee_exercice,
            CompteAdministratif.collectivite_id,
        )
        .join(
            Commune,
            CompteAdministratif.collectivite_id == Commune.id,
        )
        .where(
            CompteAdministratif.status == CompteStatus.published,
            CompteAdministratif.collectivite_type == "commune",
            Commune.search_vector.op("@@")(ts_query),
        )
        .order_by(CompteAdministratif.annee_exercice.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    for row in result:
        comptes.append(
            SearchCompteItem(
                id=str(row.id),
                collectivite_name=row.commune_name,
                collectivite_type=row.collectivite_type,
                annee_exercice=row.annee_exercice,
                url=f"/collectivite/{row.collectivite_id}",
            )
        )

    total = len(collectivites) + len(comptes)
    return SearchResponse(
        results={"collectivites": collectivites, "comptes": comptes},
        total=total,
    )
