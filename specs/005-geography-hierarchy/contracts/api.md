# API Contracts: 005-geography-hierarchy

**Date**: 2026-03-20
**Base URL**: `/api`

## Public Endpoints (no auth required)

### GET /api/provinces

Liste toutes les provinces.

**Response** `200`:
```json
[
  {
    "id": "uuid",
    "name": "Antananarivo",
    "code": "ANT",
    "created_at": "2026-01-01T00:00:00Z"
  }
]
```

### GET /api/provinces/{id}

Detail d'une province avec ses regions.

**Response** `200`:
```json
{
  "id": "uuid",
  "name": "Antananarivo",
  "code": "ANT",
  "description_json": [
    { "type": "heading", "content": "Presentation" },
    { "type": "paragraph", "content": "..." }
  ],
  "regions": [
    { "id": "uuid", "name": "Analamanga", "code": "ANA" }
  ],
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-15T00:00:00Z"
}
```

**Response** `404`: `{ "detail": "Province not found" }`

### GET /api/regions

Liste des regions, filtrable par province.

**Query params**: `province_id` (UUID, optionnel)

**Response** `200`:
```json
[
  {
    "id": "uuid",
    "name": "Analamanga",
    "code": "ANA",
    "province_id": "uuid",
    "created_at": "2026-01-01T00:00:00Z"
  }
]
```

### GET /api/regions/{id}

Detail d'une region avec ses communes.

**Response** `200`:
```json
{
  "id": "uuid",
  "name": "Analamanga",
  "code": "ANA",
  "province_id": "uuid",
  "description_json": [...],
  "communes": [
    { "id": "uuid", "name": "Antananarivo Renivohitra", "code": "ANT-R" }
  ],
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-15T00:00:00Z"
}
```

**Response** `404`: `{ "detail": "Region not found" }`

### GET /api/communes

Liste des communes, filtrable par region.

**Query params**: `region_id` (UUID, optionnel)

**Response** `200`:
```json
[
  {
    "id": "uuid",
    "name": "Antananarivo Renivohitra",
    "code": "ANT-R",
    "region_id": "uuid",
    "created_at": "2026-01-01T00:00:00Z"
  }
]
```

### GET /api/communes/{id}

Detail d'une commune.

**Response** `200`:
```json
{
  "id": "uuid",
  "name": "Antananarivo Renivohitra",
  "code": "ANT-R",
  "region_id": "uuid",
  "description_json": [...],
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-15T00:00:00Z"
}
```

**Response** `404`: `{ "detail": "Commune not found" }`

### GET /api/geography/hierarchy

Arbre complet Province > Region > Commune.

**Response** `200`:
```json
[
  {
    "id": "uuid",
    "name": "Antananarivo",
    "code": "ANT",
    "regions": [
      {
        "id": "uuid",
        "name": "Analamanga",
        "code": "ANA",
        "communes": [
          { "id": "uuid", "name": "Antananarivo Renivohitra", "code": "ANT-R" }
        ]
      }
    ]
  }
]
```

## Admin Endpoints (auth required: admin or editor)

All admin endpoints require `Authorization: Bearer <token>` header.
Role check: `admin` or `editor`.

### POST /api/admin/provinces

**Request**:
```json
{
  "name": "Antananarivo",
  "code": "ANT",
  "description_json": []
}
```

**Response** `201`: Province object (same as GET detail, without regions)
**Response** `409`: `{ "detail": "A province with code 'ANT' already exists" }`
**Response** `422`: Validation error

### PUT /api/admin/provinces/{id}

**Request**:
```json
{
  "name": "Antananarivo (updated)",
  "code": "ANT",
  "description_json": [...]
}
```

**Response** `200`: Updated province object
**Response** `404`: `{ "detail": "Province not found" }`
**Response** `409`: `{ "detail": "A province with code 'XXX' already exists" }`

### DELETE /api/admin/provinces/{id}

**Response** `204`: No content
**Response** `404`: `{ "detail": "Province not found" }`
**Response** `409`: `{ "detail": "Cannot delete province: it has 5 region(s)" }`

### POST /api/admin/regions

**Request**:
```json
{
  "name": "Analamanga",
  "code": "ANA",
  "province_id": "uuid",
  "description_json": []
}
```

**Response** `201`: Region object
**Response** `409`: Code duplicate
**Response** `422`: Validation error

### PUT /api/admin/regions/{id}

**Request**: Same fields as POST (province_id can be changed)
**Response** `200`: Updated region object

### DELETE /api/admin/regions/{id}

**Response** `204`: No content
**Response** `409`: `{ "detail": "Cannot delete region: it has 12 commune(s)" }`

### POST /api/admin/communes

**Request**:
```json
{
  "name": "Antananarivo Renivohitra",
  "code": "ANT-R",
  "region_id": "uuid",
  "description_json": []
}
```

**Response** `201`: Commune object

### PUT /api/admin/communes/{id}

**Request**: Same fields as POST
**Response** `200`: Updated commune object

### DELETE /api/admin/communes/{id}

**Response** `204`: No content

## Admin List Endpoints (paginated)

### GET /api/admin/provinces

**Query params**: `search` (string, opt), `skip` (int, default 0), `limit` (int, default 20)

**Response** `200`:
```json
{
  "items": [{ "id": "uuid", "name": "...", "code": "...", "created_at": "..." }],
  "total": 6
}
```

### GET /api/admin/regions

**Query params**: `province_id` (UUID, opt), `search` (string, opt), `skip` (int, default 0), `limit` (int, default 20)

**Response** `200`:
```json
{
  "items": [...],
  "total": 23
}
```

### GET /api/admin/communes

**Query params**: `region_id` (UUID, opt), `search` (string, opt), `skip` (int, default 0), `limit` (int, default 20)

**Response** `200`:
```json
{
  "items": [...],
  "total": 1500
}
```

## Shared Types (packages/shared)

```typescript
// geography.ts

interface RichContentBlock {
  type: 'heading' | 'paragraph' | 'image'
  content?: string
  url?: string
  alt?: string
}

interface ProvinceListItem {
  id: string
  name: string
  code: string
  created_at: string
}

interface ProvinceDetail extends ProvinceListItem {
  description_json: RichContentBlock[]
  regions: RegionListItem[]
  updated_at: string | null
}

interface RegionListItem {
  id: string
  name: string
  code: string
  province_id: string
  created_at: string
}

interface RegionDetail extends RegionListItem {
  description_json: RichContentBlock[]
  communes: CommuneListItem[]
  updated_at: string | null
}

interface CommuneListItem {
  id: string
  name: string
  code: string
  region_id: string
  created_at: string
}

interface CommuneDetail extends CommuneListItem {
  description_json: RichContentBlock[]
  updated_at: string | null
}

interface PaginatedResponse<T> {
  items: T[]
  total: number
}

interface HierarchyProvince {
  id: string
  name: string
  code: string
  regions: HierarchyRegion[]
}

interface HierarchyRegion {
  id: string
  name: string
  code: string
  communes: HierarchyCommuneItem[]
}

interface HierarchyCommuneItem {
  id: string
  name: string
  code: string
}
```
