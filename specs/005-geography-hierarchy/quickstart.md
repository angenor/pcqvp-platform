# Quickstart: 005-geography-hierarchy

## Prerequis

- Python 3.12+ avec venv
- Node.js 20+
- PostgreSQL 16+ en cours d'execution
- Feature 004-auth-roles implementee (modeles User, auth endpoints)

## Backend

```bash
cd apps/backend

# Activer le venv existant
source .venv/bin/activate

# Installer les dependances (si nouvelles)
pip install -e ".[dev]"

# Appliquer la migration geographie
alembic upgrade head

# Lancer le serveur
uvicorn app.main:app --reload --port 8000
```

## Frontend

```bash
cd apps/frontend

# Installer les dependances
npm install

# Lancer le serveur de dev
npm run dev
```

## Verification rapide

1. **Backend API** : `curl http://localhost:8000/api/provinces` → `[]` (liste vide)
2. **Admin CRUD** : Se connecter via `/admin/login`, aller a `/admin/geography/provinces`
3. **Selecteur public** : Page d'accueil `/` → selecteur a 4 niveaux visible

## Fichiers cles de cette feature

### Backend
- `app/models/geography.py` - Modeles Province, Region, Commune
- `app/schemas/geography.py` - Schemas Pydantic (validation + serialisation)
- `app/routers/geography.py` - Routes publiques (GET)
- `app/routers/admin_geography.py` - Routes admin (POST/PUT/DELETE + listes paginees)
- `app/services/geography.py` - Logique metier (CRUD, integrite referentielle)
- `alembic/versions/002_create_geography_tables.py` - Migration

### Frontend
- `app/components/GeographySelector.vue` - Selecteur 4 niveaux chaines
- `app/components/RichContentEditor.vue` - Editeur de blocs (heading/paragraph/image)
- `app/components/RichContentRenderer.vue` - Rendu public du contenu riche
- `app/pages/admin/geography/provinces/index.vue` - Liste admin provinces
- `app/pages/admin/geography/provinces/[id].vue` - Edition province
- `app/pages/admin/geography/regions/index.vue` - Liste admin regions
- `app/pages/admin/geography/regions/[id].vue` - Edition region
- `app/pages/admin/geography/communes/index.vue` - Liste admin communes
- `app/pages/admin/geography/communes/[id].vue` - Edition commune
- `app/composables/useGeography.ts` - Composable API geographie

### Shared
- `packages/shared/types/geography.ts` - Types TypeScript partages
