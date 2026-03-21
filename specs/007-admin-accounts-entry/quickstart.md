# Quickstart: Saisie et stockage des comptes administratifs

**Date**: 2026-03-21 | **Branch**: `007-admin-accounts-entry`

## Prerequis

- Docker (PostgreSQL 16) en cours d'execution
- Backend venv active avec deps installees
- Frontend pnpm install effectue
- Feature 006 (templates) deja deployee (migration 003 + seed des templates)
- Feature 005 (geographie) deja deployee (communes existantes en base)
- Au moins un utilisateur admin cree (via `scripts/seed_admin.py`)

## Demarrage rapide

### 1. Appliquer la migration

```bash
cd apps/backend
source .venv/bin/activate
alembic upgrade head
```

### 2. Verifier les templates existants

```bash
# Les templates recettes et depenses doivent etre presents
curl -s http://localhost:8000/api/admin/templates \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

### 3. Creer un compte administratif

```bash
# Creer un compte pour Andrafiabe 2023
curl -X POST http://localhost:8000/api/admin/comptes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"collectivite_type": "commune", "collectivite_id": "<UUID_ANDRAFIABE>", "annee_exercice": 2023}'
```

### 4. Saisir une ligne de recette

```bash
# Auto-save une ligne de recette (compte 7080)
curl -X PUT http://localhost:8000/api/admin/comptes/<COMPTE_ID>/recettes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template_line_id": "<UUID_LINE_7080>", "values": {"budget_primitif": 1017922, "budget_additionnel": 0, "modifications": 0, "or_admis": 1017922, "recouvrement": 0}}'
```

### 5. Consulter les recapitulatifs

```bash
# Recap recettes
curl -s http://localhost:8000/api/admin/comptes/<COMPTE_ID>/recapitulatifs/recettes \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

# Equilibre
curl -s http://localhost:8000/api/admin/comptes/<COMPTE_ID>/recapitulatifs/equilibre \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

### 6. Lancer les tests

```bash
cd apps/backend
pytest tests/test_comptes.py -v
```

### 7. Frontend

```bash
cd apps/frontend
pnpm dev
# Naviguer vers http://localhost:3000/admin/accounts
```

## Fichiers cles a modifier

| Fichier | Description |
|---------|-------------|
| `apps/backend/app/models/compte_administratif.py` | Modeles SQLAlchemy (5 entites) |
| `apps/backend/app/schemas/compte_administratif.py` | Schemas Pydantic v2 |
| `apps/backend/app/services/compte_service.py` | CRUD comptes, upsert lignes, gestion programmes |
| `apps/backend/app/services/account_service.py` | Calculs dynamiques (recapitulatifs, equilibre, sommes) |
| `apps/backend/app/routers/admin_comptes.py` | 13 endpoints API |
| `apps/backend/alembic/versions/004_*.py` | Migration (5 tables + enums) |
| `apps/backend/tests/test_comptes.py` | Tests API et calculs |
| `apps/frontend/app/composables/useComptes.ts` | Composable API frontend |
| `apps/frontend/app/components/AccountDataTable.vue` | Tableau de saisie reutilisable |
| `apps/frontend/app/pages/admin/accounts/*.vue` | Pages admin (5 fichiers) |
| `packages/shared/types/comptes.ts` | Types partages |
