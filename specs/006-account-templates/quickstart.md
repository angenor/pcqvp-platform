# Quickstart: 006-account-templates

**Branch**: `006-account-templates`

## Prerequis

- PostgreSQL 16+ en cours d'execution (`docker compose up -d`)
- Python 3.12+ avec venv active dans `apps/backend/`
- Node.js + pnpm dans `apps/frontend/`

## Backend

```bash
cd apps/backend
source .venv/bin/activate

# Installer la nouvelle dependance
pip install -e ".[dev]"

# Appliquer la migration
alembic upgrade head

# Importer la structure de reference
python -m app.services.seed_templates

# Lancer le serveur
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Verifier
curl http://localhost:8000/api/admin/templates
```

## Frontend

```bash
cd apps/frontend
pnpm install
pnpm dev

# Acceder a l'admin : http://localhost:3000/admin/templates
```

## Tests

```bash
# Backend
cd apps/backend
pytest tests/test_templates.py -v

# Frontend (quand les tests sont ajoutes)
cd apps/frontend
pnpm test
```

## Fichiers cles

| Fichier | Role |
|---------|------|
| `apps/backend/app/models/account_template.py` | Modeles SQLAlchemy |
| `apps/backend/app/schemas/account_template.py` | Schemas Pydantic |
| `apps/backend/app/services/template_service.py` | Logique metier CRUD |
| `apps/backend/app/services/seed_templates.py` | Import Excel → DB |
| `apps/backend/app/routers/admin_templates.py` | Endpoints API admin |
| `apps/backend/alembic/versions/003_create_account_template_tables.py` | Migration |
| `apps/frontend/app/pages/admin/templates/index.vue` | Liste templates admin |
| `apps/frontend/app/pages/admin/templates/[id].vue` | Editeur de template |
| `apps/frontend/app/composables/useTemplates.ts` | API composable |
| `packages/shared/types/templates.ts` | Types partages |
