# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Plateforme PCQVP (Publiez Ce Que Vous Payez) - transparence des industries extractives de Madagascar. Monorepo avec backend FastAPI, frontend Nuxt 4, et types partagés.

## Architecture

```
pcqvp-platform-new-version/
├── backend/              # FastAPI + SQLAlchemy async + Alembic
│   ├── app/
│   │   ├── main.py       # Point d'entrée FastAPI, montage des routers
│   │   ├── core/         # config (pydantic-settings), database (async engine), security (JWT/bcrypt), rate_limit
│   │   ├── models/       # SQLAlchemy models (UUIDBase avec UUID pk + created_at auto)
│   │   ├── schemas/      # Pydantic v2 schemas
│   │   ├── routers/      # FastAPI routers (auth, geography, admin_*, public_*, search, upload, users)
│   │   ├── services/     # Business logic layer
│   │   └── middleware/    # visit_tracker.py
│   ├── alembic/          # Migrations DB (5 versions)
│   ├── scripts/          # seed_admin.py
│   └── tests/            # pytest + pytest-asyncio + httpx
├── frontend/             # Nuxt 4 + Tailwind CSS 4
│   └── app/
│       ├── pages/        # Routes (admin/*, communes/*, provinces/*, regions/*, recherche, signaler)
│       ├── components/   # AccountTable, GeographySelector, RichContentEditor/Renderer, etc.
│       ├── composables/  # useApi (point d'entrée unique API), useAuth, useGeography, useComptes...
│       ├── layouts/      # admin.vue (sidebar), default.vue
│       ├── middleware/    # auth.ts (route protection)
│       ├── plugins/      # fontawesome.ts
│       └── types/        # TypeScript interfaces
├── packages/shared/      # Types partagés (auth, geography, comptes, config, etc.)
├── specs/                # Spécifications par feature (speckit, 002-012)
└── docker-compose.yml    # PostgreSQL 16
```

### Key Patterns

- **Backend models** héritent de `UUIDBase` (UUID pk + `created_at` auto) dans `app/models/base.py`
- **Config** chargée via `pydantic-settings` depuis `.env` situé dans le **dossier parent** du repo (`parents[4]` depuis `config.py`)
- **Frontend proxy** : Nuxt proxy `/api/**` et `/uploads/**` vers `http://localhost:8000` (configuré dans `nuxt.config.ts` routeRules)
- **Hiérarchie géographique** : Province -> Region -> Commune (FK avec `ondelete=RESTRICT`, relations `selectin`)
- **Contenu riche** : champs `description_json` en JSONB, édition via EditorJS + plugins, rendu via `RichContentRenderer`
- **Auth** : JWT access (30min) + refresh tokens (7j), rôles `admin`/`editor` (StrEnum), verrouillage après échecs
- **Tests** : DB séparée `pcqvp_test`, tables créées/détruites à chaque test (conftest.py)
- **Design** : dark/light mode obligatoire (`@nuxtjs/color-mode` stratégie `class`), FontAwesome icons, Google Fonts (Barlow Condensed, Inter, JetBrains Mono)

## Commands

### Database
```bash
docker compose up -d                              # Démarrer PostgreSQL
docker compose down                               # Arrêter (données préservées)
docker compose down -v                            # Arrêter + supprimer données
```

### Backend (depuis `backend/`, venv activé)
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

### Frontend (depuis `frontend/`)
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
- **Frontend** : TypeScript strict, Tailwind CSS 4 (CSS-native config via `@tailwindcss/vite`)
- **Dark/light mode obligatoire** : tout composant/page Vue DOIT utiliser les classes Tailwind `dark:`. Color mode via `@nuxtjs/color-mode` avec stratégie `class`.
- **API calls** : utiliser le composable `useApi` comme point d'entrée unique côté frontend

## Tech Stack

- **Backend** : Python 3.12+, FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, Pydantic v2, Alembic, openpyxl, python-docx, slowapi, fastapi-mail, itsdangerous
- **Frontend** : Nuxt 4.4+, Vue 3.5+, Tailwind CSS 4, @nuxtjs/color-mode, @editorjs/editorjs + plugins, @fortawesome/vue-fontawesome
- **Database** : PostgreSQL 16+ via asyncpg
- **Infra** : Docker Compose (PostgreSQL), pnpm (frontend)

## Parallel Sub-agents Strategy

Use multiple sub-agents in parallel for efficiency (10 max):
- Search frontend + backend simultaneously
- Explore multiple files/folders at the same time
- Run tests + verifications in parallel after modifications

## Active Technologies
- Python 3.12 (backend), TypeScript (frontend) + FastAPI, SQLAlchemy 2.0 async, Nuxt 4, Vue 3.5, Tailwind CSS 4 (014-region-admin-accounts)
- PostgreSQL 16 via asyncpg (014-region-admin-accounts)

## Recent Changes
- 014-region-admin-accounts: Added Python 3.12 (backend), TypeScript (frontend) + FastAPI, SQLAlchemy 2.0 async, Nuxt 4, Vue 3.5, Tailwind CSS 4
