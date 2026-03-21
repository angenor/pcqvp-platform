# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Plateforme PCQVP (Publiez Ce Que Vous Payez) - transparence des industries extractives de Madagascar. Monorepo avec backend FastAPI, frontend Nuxt 4, et types partagés.

## Architecture

```
pcqvp-platform/
├── apps/backend/         # FastAPI + SQLAlchemy async + Alembic
│   ├── app/
│   │   ├── main.py       # Point d'entrée FastAPI, montage des routers
│   │   ├── core/         # config (pydantic-settings), database (async engine), security (JWT/bcrypt)
│   │   ├── models/       # SQLAlchemy models (UUIDBase avec TimestampMixin)
│   │   ├── schemas/      # Pydantic v2 schemas
│   │   ├── routers/      # FastAPI routers (auth, geography, admin_geography)
│   │   └── services/     # Business logic layer
│   ├── alembic/          # Migrations DB
│   ├── scripts/          # Scripts utilitaires (seed_admin.py)
│   └── tests/            # pytest + pytest-asyncio + httpx
├── apps/frontend/        # Nuxt 4 + Tailwind CSS 4
│   └── app/
│       ├── pages/        # Routes (admin/*, communes/*, provinces/*, regions/*)
│       ├── components/   # GeographySelector, RichContentEditor/Renderer
│       ├── composables/  # useApi (point d'entrée unique API), useAuth, useGeography
│       ├── layouts/      # admin.vue
│       ├── middleware/    # auth.ts
│       └── types/        # TypeScript types
├── packages/shared/      # Types partagés backend/frontend (auth.ts, geography.ts)
├── specs/                # Spécifications par feature (speckit)
└── docker-compose.yml    # PostgreSQL 16
```

### Key Patterns

- **Backend models** héritent de `UUIDBase` (UUID pk + `created_at` auto) dans `app/models/base.py`
- **Config** chargée via `pydantic-settings` depuis `.env` à la racine (4 niveaux au-dessus de `config.py`)
- **Frontend proxy** : Nuxt proxy `/api` vers `http://localhost:8000` (configuré dans `nuxt.config.ts` nitro.devProxy)
- **Hiérarchie géographique** : Province → Region → Commune (FK avec `ondelete=RESTRICT`, relations `selectin`)
- **Contenu riche** : champs `description_json` en JSONB sur les modèles géographiques
- **Auth** : JWT access + refresh tokens, rôles `admin`/`editor` (StrEnum), verrouillage après échecs
- **Tests** : utilisent une DB séparée `pcqvp_test`, tables créées/détruites à chaque test (conftest.py)

## Commands

### Database
```bash
docker compose up -d                              # Démarrer PostgreSQL
docker compose down                               # Arrêter (données préservées)
```

### Backend (depuis `apps/backend/`, venv activé)
```bash
source .venv/bin/activate
pip install -e ".[dev]"                           # Installer deps (dev inclus)
alembic upgrade head                              # Appliquer migrations
alembic revision --autogenerate -m "description"  # Créer migration
alembic downgrade -1                              # Annuler dernière migration
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000  # Lancer le serveur
pytest                                            # Lancer tous les tests
pytest tests/test_auth.py -v                      # Un fichier de test
pytest tests/test_auth.py::test_name -v           # Un test spécifique
ruff check .                                      # Lint Python
ruff check . --fix                                # Lint + autofix
```

### Frontend (depuis `apps/frontend/`)
```bash
pnpm install
pnpm dev                                          # Dev server (port 3000)
pnpm build                                        # Build production
```

### Health check
- Frontend : http://localhost:3000
- Backend : http://localhost:8000/health

## Code Style & Rules

- **Python** : ruff (target py312, line-length 88, rules E/F/I/UP/W)
- **Frontend** : TypeScript strict, Tailwind CSS 4 (CSS-native config)
- **Dark/light mode obligatoire** : tout composant/page Vue DOIT utiliser les classes Tailwind `dark:`. Color mode via `@nuxtjs/color-mode` avec stratégie `class`.
- **API calls** : utiliser le composable `useApi` comme point d'entrée unique côté frontend

## Parallel Sub-agents Strategy

Use multiple sub-agents in parallel for efficiency (10 max):
- Search frontend + backend simultaneously
- Explore multiple files/folders at the same time
- Run tests + verifications in parallel after modifications

## Active Technologies
- Python 3.12+ (backend), TypeScript strict (frontend) + FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, openpyxl>=3.1.0 (backend) ; Nuxt 4.4+, Tailwind CSS 4, @nuxtjs/color-mode (frontend) (006-account-templates)
- PostgreSQL 16+ via asyncpg, 3 nouvelles tables (006-account-templates)
- Python 3.12+ (backend), TypeScript strict (frontend) + FastAPI 0.135+, SQLAlchemy 2.0.48+ async, Pydantic v2, asyncpg, openpyxl (backend) ; Nuxt 4.4+, Tailwind CSS 4, @nuxtjs/color-mode (frontend) (007-admin-accounts-entry)
- PostgreSQL 16+ via asyncpg ; 5 nouvelles tables (comptes_administratifs, recette_lines, depense_programs, depense_lines, account_change_logs) (007-admin-accounts-entry)

## Recent Changes
- 006-account-templates: Added Python 3.12+ (backend), TypeScript strict (frontend) + FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, openpyxl>=3.1.0 (backend) ; Nuxt 4.4+, Tailwind CSS 4, @nuxtjs/color-mode (frontend)
