# API Contract Changes: 016-banner-image-hero

**Date**: 2026-03-28

## Modified Endpoints

### 1. PUT /api/admin/provinces/{province_id}

**Schema change** (ProvinceUpdate): add `banner_image: str | None` (optional field)

Request body (additions only):
```json
{
  "banner_image": "/uploads/images/abc123.jpg"
}
```

Response (ProvinceDetail) additions:
```json
{
  "banner_image": "/uploads/images/abc123.jpg"
}
```

### 2. POST /api/admin/provinces

**Schema change** (ProvinceCreate): add `banner_image: str | None` (optional field)

Same pattern as PUT.

### 3. PUT /api/admin/regions/{region_id}

**Schema change** (RegionUpdate): add `banner_image: str | None` (optional field)

### 4. POST /api/admin/regions

**Schema change** (RegionCreate): add `banner_image: str | None` (optional field)

### 5. PUT /api/admin/communes/{commune_id}

**Schema change** (CommuneUpdate): add `banner_image: str | None` (optional field)

### 6. POST /api/admin/communes

**Schema change** (CommuneCreate): add `banner_image: str | None` (optional field)

### 7. GET /api/public/collectivites/{ctype}/{cid}/description

**Response change** (PublicDescriptionResponse): add `banner_image: str | null`

Current response:
```json
{
  "name": "Antananarivo",
  "type": "commune",
  "description_json": [...]
}
```

New response:
```json
{
  "name": "Antananarivo",
  "type": "commune",
  "description_json": [...],
  "banner_image": "/uploads/images/abc123.jpg"
}
```

`banner_image` sera `null` si aucune banniere n'est definie.

## Endpoints inchanges

- `POST /api/admin/upload/image` : reutilise tel quel pour l'upload des bannieres
- `GET /api/admin/provinces`, `GET /api/admin/regions`, `GET /api/admin/communes` : les schemas List ne changent pas
- `DELETE` endpoints : inchanges

## Types frontend a modifier

### packages/shared/types/geography.ts

```typescript
// Ajouter banner_image aux interfaces Detail
interface ProvinceDetail { banner_image: string | null; /* ...existing */ }
interface RegionDetail { banner_image: string | null; /* ...existing */ }
interface CommuneDetail { banner_image: string | null; /* ...existing */ }
```

### packages/shared/types/public.ts

```typescript
interface PublicDescriptionResponse {
  name: string
  type: CollectiviteType
  description_json: { type: string; content?: string; url?: string; alt?: string }[]
  banner_image: string | null  // NEW
}
```

## Backward Compatibility

Tous les changements sont additifs (nouveaux champs optionnels/nullable). Aucun breaking change.
