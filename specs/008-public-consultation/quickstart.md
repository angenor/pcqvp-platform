# Quickstart: 008-public-consultation

## Prerequis

- Docker compose running (PostgreSQL 16)
- Backend venv active avec deps installees
- Frontend pnpm install done
- Features 005 (geography), 006 (templates), 007 (accounts) deployees
- Au moins un compte administratif avec status "published" en base

## Backend

```bash
cd apps/backend
source .venv/bin/activate

# Installer la nouvelle dependance
pip install python-docx>=1.1.0
pip install -e ".[dev]"

# Lancer le serveur
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Tester les endpoints publics
curl http://localhost:8000/api/public/collectivites/commune/{id}/annees
curl http://localhost:8000/api/public/collectivites/commune/{id}/description
curl "http://localhost:8000/api/public/collectivites/commune/{id}/comptes?annee=2023"
curl "http://localhost:8000/api/public/collectivites/commune/{id}/comptes/2023/export?format=xlsx" -o test.xlsx

# Lancer les tests
pytest tests/test_public_comptes.py -v
```

## Frontend

```bash
cd apps/frontend
pnpm dev

# Pages a tester
# http://localhost:3000/                           → Landing page
# http://localhost:3000/collectivite/commune-{id}  → Page de resultats
```

## Fichiers crees/modifies

### Backend (apps/backend/)
- `app/routers/public_comptes.py` — NOUVEAU : router public
- `app/services/public_service.py` — NOUVEAU : service lecture publique
- `app/services/export_service.py` — NOUVEAU : generation Excel/Word
- `app/schemas/public.py` — NOUVEAU : schemas reponse publics
- `app/main.py` — MODIFIE : montage du nouveau router
- `pyproject.toml` — MODIFIE : ajout python-docx
- `tests/test_public_comptes.py` — NOUVEAU : tests endpoints publics

### Frontend (apps/frontend/)
- `app/pages/index.vue` — MODIFIE : landing page publique
- `app/pages/collectivite/[type]-[id].vue` — NOUVEAU : page de resultats
- `app/components/AccountTable.vue` — NOUVEAU : tableau depliable
- `app/components/RecapTable.vue` — NOUVEAU : tableaux recapitulatifs
- `app/components/EquilibreTable.vue` — NOUVEAU : tableau d'equilibre
- `app/components/GeographySelector.vue` — MODIFIE : prop navigation flexible
- `app/composables/usePublicComptes.ts` — NOUVEAU : composable API publique
- `app/types/comptes.ts` — MODIFIE : types publics

### Types partages (packages/shared/)
- `types/public.ts` — NOUVEAU : types reponse API publique
