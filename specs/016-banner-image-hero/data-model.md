# Data Model: 016-banner-image-hero

**Date**: 2026-03-28

## Entity Changes

### Province (table: `provinces`)

| Field | Type | Nullable | Default | Notes |
|-------|------|----------|---------|-------|
| banner_image | String(500) | Yes | NULL | New field. Chemin relatif vers l'image (ex: `/uploads/images/{uuid}.jpg`) |

*Existing fields unchanged: id, name, code, description_json, updated_at, search_vector, created_at*

### Region (table: `regions`)

| Field | Type | Nullable | Default | Notes |
|-------|------|----------|---------|-------|
| banner_image | String(500) | Yes | NULL | New field. Chemin relatif vers l'image |

*Existing fields unchanged: id, name, code, province_id, description_json, updated_at, search_vector, created_at*

### Commune (table: `communes`)

| Field | Type | Nullable | Default | Notes |
|-------|------|----------|---------|-------|
| banner_image | String(500) | Yes | NULL | New field. Chemin relatif vers l'image |

*Existing fields unchanged: id, name, code, region_id, description_json, updated_at, search_vector, created_at*

## Relationships

Aucune nouvelle relation. Le champ `banner_image` est un attribut scalaire (string URL) et non une FK.

## Validation Rules

- `banner_image` : optionnel, string, max 500 caracteres
- Format attendu : chemin relatif commencant par `/uploads/images/` (non enforce en DB, valide cote application)
- Valeur `null` ou chaine vide = pas de banniere

## State Transitions

- `null` → URL string : ajout d'une banniere (upload + save)
- URL string → autre URL string : remplacement de banniere
- URL string → `null` : suppression de banniere

## Migration

**File**: `backend/alembic/versions/007_add_banner_image.py`

**Upgrade**: `ALTER TABLE {provinces,regions,communes} ADD COLUMN banner_image VARCHAR(500) NULL`

**Downgrade**: `ALTER TABLE {provinces,regions,communes} DROP COLUMN banner_image`

Pas de migration de donnees necessaire (champ nullable, valeur initiale NULL).
