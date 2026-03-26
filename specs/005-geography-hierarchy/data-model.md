# Data Model: 005-geography-hierarchy

**Date**: 2026-03-20

## Entities

### Province

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK, auto-generated |
| name | String(255) | NOT NULL |
| code | String(20) | NOT NULL, UNIQUE |
| description_json | JSONB | DEFAULT [] |
| created_at | DateTime | server default now() |
| updated_at | DateTime | onupdate now(), nullable |

**Relationships**: One-to-many → Region (back_populates="province")

### Region

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK, auto-generated |
| name | String(255) | NOT NULL |
| code | String(20) | NOT NULL, UNIQUE |
| province_id | UUID | FK → provinces.id, NOT NULL, ON DELETE RESTRICT |
| description_json | JSONB | DEFAULT [] |
| created_at | DateTime | server default now() |
| updated_at | DateTime | onupdate now(), nullable |

**Relationships**:
- Many-to-one → Province (back_populates="regions")
- One-to-many → Commune (back_populates="region")

**Indexes**: index on province_id (filtrage par province)

### Commune

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK, auto-generated |
| name | String(255) | NOT NULL |
| code | String(20) | NOT NULL, UNIQUE |
| region_id | UUID | FK → regions.id, NOT NULL, ON DELETE RESTRICT |
| description_json | JSONB | DEFAULT [] |
| created_at | DateTime | server default now() |
| updated_at | DateTime | onupdate now(), nullable |

**Relationships**: Many-to-one → Region (back_populates="communes")

**Indexes**: index on region_id (filtrage par region)

## JSONB Structure: description_json

Tableau de blocs ordonnes. Chaque bloc est un objet avec un champ `type` et des champs specifiques au type.

```json
[
  { "type": "heading", "content": "Titre de section" },
  { "type": "paragraph", "content": "Texte du paragraphe..." },
  { "type": "image", "url": "https://example.com/photo.jpg", "alt": "Description" }
]
```

**Types de blocs supportes**:
- `heading` : champ `content` (string, obligatoire)
- `paragraph` : champ `content` (string, obligatoire)
- `image` : champ `url` (string, obligatoire), champ `alt` (string, optionnel)

**Validation Pydantic**: Un discriminated union sur le champ `type` valide la structure de chaque bloc.

## Inheritance Pattern

Les trois entites heritent de `UUIDBase` (existant) qui fournit `id` (UUID) et `created_at`. Le champ `updated_at` est ajoute directement sur chaque modele (ou via un mixin `UpdateTimestampMixin`).

## Migration Strategy

Migration Alembic unique creant les 3 tables dans l'ordre : provinces → regions → communes (respect des FK).

Downgrade : drop communes → regions → provinces (ordre inverse).
