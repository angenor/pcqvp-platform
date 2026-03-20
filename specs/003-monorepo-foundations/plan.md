# Implementation Plan: Fondations du monorepo

**Branch**: `003-monorepo-foundations` | **Date**: 2026-03-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-monorepo-foundations/spec.md`

## Summary

Mettre en place la structure monorepo avec un backend FastAPI async (SQLAlchemy 2.0 + asyncpg + Alembic), un frontend Nuxt 4.4+ (Tailwind CSS 4 via @tailwindcss/vite), et une infrastructure Docker Compose (PostgreSQL 16). Le tout connecte via un endpoint `GET /health` consomme par la page d'accueil du frontend.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript strict (frontend)
**Primary Dependencies**: FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, Alembic, Pydantic Settings, Uvicorn (backend) ; Nuxt 4.4+, @tailwindcss/vite (frontend)
**Storage**: PostgreSQL 16 (Docker Compose, volume persistant)
**Testing**: Non configure dans cette feature (pytest et Vitest prevus pour les prochaines features)
**Target Platform**: Web (environnement de developpement local)
**Project Type**: Web application (monorepo)
**Performance Goals**: Health check < 2s, page d'accueil < 3s
**Constraints**: Dev uniquement, pas d'auth, pas de modeles metier, .venv local pour le backend Python
**Scale/Scope**: Setup initial pour un developpeur

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0

| Principe | Statut | Justification |
|----------|--------|---------------|
| I. Donnees Ouvertes & Transparence | N/A | Pas de donnees metier dans cette feature |
| II. Securite - CORS restrictif en prod | PASS | CORS configure via variable d'environnement, restrictif par defaut |
| II. Securite - Secrets non exposes | PASS | .env.example avec valeurs placeholder, .env dans .gitignore |
| II. Securite - Migrations reversibles | PASS | Alembic configure avec template async, downgrade supporte |
| III. Simplicite - Code simple | PASS | Architecture minimale : 2 fichiers core (config, database) + main |
| III. Simplicite - Responsabilite unique | PASS | Separation claire : config.py, database.py, main.py |
| III. Simplicite - useApi point d'entree unique | PASS | createUseFetch dans composables/useApi.ts |
| III. Simplicite - Ruff lint | PASS | Configure dans pyproject.toml |
| III. Simplicite - packages/shared | DEFERRED | Pas de types partages dans cette feature |

### Post-Phase 1

| Principe | Statut | Justification |
|----------|--------|---------------|
| Tous les principes pre-Phase 0 | PASS | Inchanges |
| Structure backend (constitution) | PASS | `app/main.py`, `app/core/` conforme |
| Structure frontend (constitution) | PASS | `app/pages/`, `app/composables/` conforme Nuxt 4 |

## Project Structure

### Documentation (this feature)

```text
specs/003-monorepo-foundations/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── health.md
├── checklists/
│   └── requirements.md
└── tasks.md             # (genere par /speckit.tasks)
```

### Source Code (repository root)

```text
apps/
├── backend/
│   ├── .venv/                        # Environnement virtuel Python (gitignore)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app, CORS, /health endpoint
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Pydantic BaseSettings
│   │   │   └── database.py           # async engine, session factory, get_db
│   │   └── models/
│   │       └── __init__.py           # DeclarativeBase (target_metadata Alembic)
│   ├── alembic/
│   │   ├── env.py                    # Config async (template async)
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── alembic.ini
│   └── pyproject.toml                # [project] + [tool.ruff]
└── frontend/
    ├── app/
    │   ├── pages/
    │   │   └── index.vue             # "Plateforme PCQVP" + health status
    │   ├── composables/
    │   │   └── useApi.ts             # createUseFetch({ baseURL: "/api" })
    │   └── assets/
    │       └── css/
    │           └── main.css          # @import "tailwindcss"
    ├── nuxt.config.ts                # devProxy + @tailwindcss/vite
    ├── package.json
    └── pnpm-lock.yaml

docker-compose.yml                    # PostgreSQL 16
.env.example                          # Variables documentees
.gitignore                            # .env, .venv/, node_modules/
README.md                             # Instructions de demarrage
```

**Structure Decision**: Architecture monorepo avec `apps/backend` et `apps/frontend` conforme a la constitution. Le `.venv` est local a `apps/backend/` pour isoler les dependances Python. `packages/shared/` sera cree dans une feature ulterieure quand des types partages seront necessaires.

## Complexity Tracking

| Principe defere | Justification | Prevu pour |
|-----------------|---------------|------------|
| III. Tests (pytest/Vitest) | Pas de logique metier a tester dans les fondations. Setup des outils de test prevu quand du code testable existera. | Feature suivante |
| III. ESLint TypeScript | Le frontend ne contient qu'une page statique + composable. ESLint sera configure quand le frontend aura du code applicatif significatif. | Feature suivante |
| III. packages/shared | Pas de types partages entre backend et frontend dans cette feature. | Quand des types partages seront necessaires |
