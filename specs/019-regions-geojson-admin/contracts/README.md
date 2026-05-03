# API Contracts — feature 019-regions-geojson-admin

| Fichier | Audience | Description |
|---------|----------|-------------|
| [`admin-geodata.openapi.yaml`](./admin-geodata.openapi.yaml) | admin uniquement (JWT bearer + role `admin`) | Upload, polling de tache, listing, preview, activation, suppression des versions GeoJSON regionales |
| [`public-geography-geojson.openapi.yaml`](./public-geography-geojson.openapi.yaml) | public (anonyme) | Service du GeoJSON de la version active avec ETag + Cache-Control |

## Conventions

- Auth admin via JWT bearer (header `Authorization: Bearer <token>`), reutilise le mecanisme existant de la plateforme (`app/core/security.py`).
- Errors : `ErrorResponse { detail, code? }` aligne avec FastAPI standard et avec `HTTPException` actuellement levee dans les autres routers.
- Timestamps : ISO 8601 (`format: date-time`).
- UUID : forme canonique 8-4-4-4-12.
- Rate limit : `429` retourne par slowapi via dependance `Depends(limiter.limit("10/hour"))` sur `POST /upload`.

## Validation

Les contracts servent de source de verite pour :
1. La generation des schemas Pydantic (`app/schemas/geodata.py`).
2. Les tests d'integration (`tests/integration/test_admin_geodata.py`, `test_public_geojson.py`).
3. Le typage TypeScript cote frontend (`frontend/app/types/geodata.ts` et `packages/shared/src/types/geodata.ts`).

Tout ecart entre l'implementation et ces contracts doit etre rapporte comme un bug ou une mise a jour explicite du contract.
