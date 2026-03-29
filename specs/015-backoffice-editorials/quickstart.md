# Quickstart: Section Éditoriaux du Backoffice

**Feature**: 015-backoffice-editorials
**Date**: 2026-03-27

## Prérequis

- PostgreSQL 16 running via Docker (`docker compose up -d`)
- Python 3.12+ avec venv activé
- pnpm installé pour le frontend

## Setup rapide

### 1. Backend

```bash
cd backend
source .venv/bin/activate

# Appliquer la nouvelle migration
alembic upgrade head

# Lancer le serveur
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

### 3. Vérification

- Backend health : http://localhost:8000/health
- Frontend : http://localhost:3000
- Admin : http://localhost:3000/admin/editorial (nécessite authentification admin/editor)
- API publique : http://localhost:8000/api/editorial

## Fichiers créés/modifiés

### Nouveaux fichiers

| Fichier | Description |
|---------|-------------|
| `backend/app/models/editorial.py` | Modèles SQLAlchemy (EditorialContent, ContactInfo, ResourceLink) |
| `backend/app/schemas/editorial.py` | Schémas Pydantic (validation + sérialisation) |
| `backend/app/services/editorial.py` | Logique métier CRUD |
| `backend/app/routers/admin_editorial.py` | Endpoints admin protégés |
| `backend/app/routers/public_editorial.py` | Endpoint public lecture seule |
| `backend/alembic/versions/006_create_editorial_tables.py` | Migration DB |
| `backend/tests/test_editorial.py` | Tests API |
| `frontend/app/pages/admin/editorial.vue` | Page admin avec onglets |
| `frontend/app/composables/useEditorial.ts` | Composable API |
| `packages/shared/types/editorial.ts` | Types TypeScript partagés |

### Fichiers modifiés

| Fichier | Modification |
|---------|-------------|
| `backend/app/main.py` | Enregistrement des 2 nouveaux routers |
| `frontend/app/components/admin/AdminSidebar.vue` | Ajout item menu "Éditoriaux" |
| `frontend/app/pages/index.vue` | Hero section + corps dynamiques |
| `frontend/app/layouts/default.vue` | Footer dynamique |

## Tests

```bash
cd backend
pytest tests/test_editorial.py -v
```
