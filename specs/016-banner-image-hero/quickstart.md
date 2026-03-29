# Quickstart: 016-banner-image-hero

**Date**: 2026-03-28

## Prerequis

- Docker Compose (PostgreSQL 16) en cours
- Backend venv active
- pnpm installe pour le frontend

## Etapes de mise en place

### 1. Backend - Migration DB

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

### 2. Backend - Verification

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Verifier: GET /health
```

### 3. Frontend

```bash
cd frontend
pnpm dev
# Verifier: http://localhost:3000
```

## Test rapide

1. Se connecter au backoffice (`/admin`)
2. Editer une commune ou region
3. Uploader une image banniere via le nouveau champ
4. Sauvegarder
5. Ouvrir la page publique de la collectivite (`/collectivite/{type}-{id}`)
6. Verifier le hero section avec l'image en arriere-plan

## Fichiers cles modifies

### Backend
- `backend/app/models/geography.py` - Ajout champ `banner_image`
- `backend/app/schemas/geography.py` - Schemas Create/Update/Detail
- `backend/app/services/geography.py` - Functions create/update
- `backend/app/services/public_service.py` - Description response
- `backend/alembic/versions/007_*.py` - Migration

### Frontend
- `packages/shared/types/geography.ts` - Types Detail
- `packages/shared/types/public.ts` - PublicDescriptionResponse
- `frontend/app/composables/useGeography.ts` - CRUD functions
- `frontend/app/pages/admin/geography/communes/[id].vue` - Form edit
- `frontend/app/pages/admin/geography/regions/[id]/index.vue` - Form edit
- `frontend/app/pages/admin/geography/provinces/[id]/index.vue` - Form edit
- `frontend/app/pages/collectivite/[type]-[id].vue` - Hero section
- `frontend/app/components/CollectiviteHero.vue` - Nouveau composant
