# Tasks: Fondations du monorepo

**Input**: Design documents from `/specs/003-monorepo-foundations/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/health.md, quickstart.md

**Tests**: Non demandes pour cette feature (pytest et Vitest prevus pour les prochaines features).

**Organization**: Tasks groupees par user story pour permettre une implementation et un test independants.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Peut s'executer en parallele (fichiers differents, pas de dependances)
- **[Story]**: User story associee (US1, US2, US3, US4)
- Chemins exacts dans chaque description

## Phase 1: Setup (Scaffolding du projet)

**Purpose**: Creer la structure de repertoires et les fichiers de configuration de base

- [X] T001 Create .gitignore at root with entries for .env, .venv/, node_modules/, __pycache__/, *.pyc, .nuxt/, .output/
- [X] T002 [P] Create backend project structure: apps/backend/pyproject.toml with [project] dependencies (fastapi>=0.135.0, uvicorn[standard], sqlalchemy[asyncio]>=2.0.48, asyncpg, alembic, pydantic-settings, python-dotenv), [build-system] with hatchling, [tool.ruff] config (target-version="py312", select=["E","F","I","UP","W"]), and empty apps/backend/app/__init__.py + apps/backend/app/core/__init__.py
- [X] T003 [P] Initialize Nuxt 4.4+ frontend project in apps/frontend/ using pnpm dlx nuxi init, then install @tailwindcss/vite as dev dependency with pnpm add -D tailwindcss @tailwindcss/vite

---

## Phase 2: Foundational (Infrastructure bloquante)

**Purpose**: Infrastructure commune necessaire AVANT toute user story

**CRITICAL**: Aucune user story ne peut commencer avant la fin de cette phase

- [X] T004 Create docker-compose.yml at root with PostgreSQL 16 service: image postgres:16, ports 5432:5432, volume nomme pcqvp_pgdata:/var/lib/postgresql/data, healthcheck (pg_isready -U pcqvp -d pcqvp, interval 10s, timeout 5s, retries 5, start_period 30s), env vars from .env (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB)
- [X] T005 [P] Create .env.example at root with all variables: POSTGRES_USER=pcqvp, POSTGRES_PASSWORD=changeme, POSTGRES_DB=pcqvp, DATABASE_URL=postgresql+asyncpg://pcqvp:changeme@localhost:5432/pcqvp, BACKEND_HOST=0.0.0.0, BACKEND_PORT=8000, CORS_ORIGINS=http://localhost:3000
- [X] T006 Implement Pydantic Settings config in apps/backend/app/core/config.py: BaseSettings class with DATABASE_URL (str), BACKEND_HOST (str, default 0.0.0.0), BACKEND_PORT (int, default 8000), CORS_ORIGINS (list[str]), SettingsConfigDict with env_file resolved to monorepo root via Path(__file__).resolve().parents[3] / ".env" (3 levels up: core -> app -> backend -> root), and cached get_settings() function
- [X] T007 Implement async database engine and session factory in apps/backend/app/core/database.py: create_async_engine with pool_pre_ping=True, async_sessionmaker(class_=AsyncSession, expire_on_commit=False), async generator get_db() yielding AsyncSession
- [X] T008 Create FastAPI app entry point in apps/backend/app/main.py: FastAPI instance, CORSMiddleware with allow_origins from settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"]

**Checkpoint**: Backend peut demarrer (uvicorn app.main:app), PostgreSQL tourne via docker compose, frontend peut demarrer (pnpm dev)

---

## Phase 3: User Story 1 - Demarrage de l'environnement de developpement (Priority: P1)

**Goal**: Un developpeur peut cloner, configurer et lancer l'ensemble (DB + backend + frontend) en suivant le README

**Independent Test**: Suivre le README depuis un clone frais, verifier que les 3 composants sont accessibles

### Implementation for User Story 1

- [X] T009 [P] [US1] Configure Tailwind CSS 4 in apps/frontend/: create apps/frontend/app/assets/css/main.css with @import "tailwindcss", add @tailwindcss/vite to vite.plugins and css array in apps/frontend/nuxt.config.ts
- [X] T010 [US1] Create static homepage in apps/frontend/app/pages/index.vue displaying "Plateforme PCQVP" as title with basic Tailwind styling
- [X] T011 [US1] Write README.md at root with: project description, prerequisites (Python 3.12+, Node.js 20+, pnpm, Docker), step-by-step startup instructions (cp .env.example .env, docker compose up -d, backend venv setup + pip install + uvicorn, frontend pnpm install + pnpm dev), verification URLs

**Checkpoint**: Un developpeur peut demarrer les 3 composants en suivant le README. La page affiche "Plateforme PCQVP".

---

## Phase 4: User Story 2+3 - Health Check + Communication frontend-backend (Priority: P1+P2)

**Goal**: GET /health retourne le statut du backend et de la DB. Le frontend communique via proxy + useApi et affiche le statut sur la page d'accueil.

**Independent Test**: curl http://localhost:8000/health retourne {"status":"ok","db":"connected"} (200) ou {"status":"ok","db":"disconnected","detail":"..."} (503). La page d'accueil affiche le statut via /api/health sans erreur CORS.

### Implementation for User Story 2+3

- [X] T012 [US2] Implement GET /health endpoint in apps/backend/app/main.py: inject async engine, execute text("SELECT 1") with asyncio.timeout(2.0), return 200 {"status":"ok","db":"connected"} on success, 503 {"status":"ok","db":"disconnected","detail":"error message"} on failure per contracts/health.md
- [X] T013 [P] [US3] Configure nitro.devProxy in apps/frontend/nuxt.config.ts: proxy /api/** requests to http://localhost:8000 with changeOrigin: true
- [X] T014 [P] [US3] Create useApi composable in apps/frontend/app/composables/useApi.ts using createUseFetch with baseURL "/api" and runtimeConfig fallback
- [X] T015 [US2] [US3] Update apps/frontend/app/pages/index.vue to use useApi composable to call /health through the proxy on mount, display connection indicator (connected/disconnected) below the title, handle error state when backend is unreachable

**Checkpoint**: Le health check backend fonctionne. Le frontend communique via /api/health. Aucune erreur CORS. Message d'erreur clair si backend indisponible.

---

## Phase 5: User Story 4 - Gestion des evolutions de la base de donnees (Priority: P2)

**Goal**: Alembic configure pour les migrations async, capable de creer/appliquer/annuler des migrations

**Independent Test**: alembic revision --autogenerate -m "test" && alembic upgrade head && alembic downgrade -1

### Implementation for User Story 4

- [X] T016 [P] [US4] Create Base declarative model in apps/backend/app/models/__init__.py: DeclarativeBase subclass, to be imported by alembic env.py for target_metadata
- [X] T017 [US4] Initialize Alembic with async template: run alembic init -t async alembic from apps/backend/, update alembic.ini sqlalchemy.url placeholder
- [X] T018 [US4] Configure apps/backend/alembic/env.py: import settings from app.core.config, override sqlalchemy.url at runtime with settings.DATABASE_URL, import Base from app.models for target_metadata, use NullPool for migration engine, ensure async pattern (async_engine_from_config + connection.run_sync)

**Checkpoint**: alembic upgrade head fonctionne. Une migration peut etre creee, appliquee et annulee.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validation finale et nettoyage

- [X] T019 Run complete quickstart.md validation: follow all steps from scratch (docker compose up, venv, pip install, alembic upgrade, uvicorn, pnpm install, pnpm dev), verify all success criteria (SC-001 through SC-005)
- [X] T020 [P] Verify .gitignore completeness: ensure .env, .venv/, node_modules/, __pycache__/, .nuxt/, .output/, alembic/versions/*.pyc are covered, verify no secrets or generated files are tracked

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational - can start immediately after
- **US2+US3 (Phase 4)**: Depends on Foundational + T010 (index.vue exists). US2 backend (T012) can run in parallel with US1.
- **US4 (Phase 5)**: Depends on Foundational - can run in parallel with US1, US2+US3
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Foundational only. Independent.
- **US2+US3 (P1+P2)**: Fusionnees. T012 (health endpoint) independent. T013+T014 (proxy+useApi) paralleles. T015 (index.vue integration) needs T010+T012+T014.
- **US4 (P2)**: Foundational only. Fully independent of other stories.

### Within Each User Story

- Setup infrastructure before code
- Backend before frontend (frontend consumes backend)
- Configuration before implementation
- Commit after each task

### Parallel Opportunities

**Phase 1**: T002 and T003 in parallel (backend + frontend scaffolding)
**Phase 2**: T004 and T005 in parallel (docker-compose + .env.example)
**Phase 3**: T009 parallel with other US1 tasks (different files)
**Phase 4**: T012, T013, T014 all in parallel (backend endpoint + proxy + composable in different files)
**Phase 5**: T016 parallel with Phase 4 tasks (different files)

---

## Parallel Example: Foundational Phase

```bash
# After Setup complete, launch in parallel:
Task T004: "docker-compose.yml with PostgreSQL 16"
Task T005: ".env.example with all variables"

# Then sequential:
Task T006: "config.py" (needs .env.example pattern)
Task T007: "database.py" (needs config.py)
Task T008: "main.py" (needs config.py)
```

## Parallel Example: After Foundational

```bash
# US1 and US4 can start in parallel:
# Stream A (US1):
Task T009: "Tailwind CSS 4 setup"
Task T010: "index.vue static page"
Task T011: "README.md"

# Stream B (US4):
Task T016: "Base declarative model"
Task T017: "Alembic init async"
Task T018: "env.py async config"

# Then US2+US3 (needs T010 + T012):
Task T012: "GET /health endpoint" (parallel with T013, T014)
Task T013: "nitro.devProxy config"
Task T014: "useApi composable"
Task T015: "index.vue integration" (needs T012+T013+T014)
```

---

## Implementation Strategy

### MVP First (US1 + US2+US3)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T008)
3. Complete Phase 3: US1 - Environnement (T009-T011)
4. Complete Phase 4: US2+US3 - Health Check + Communication (T012-T015)
5. **STOP and VALIDATE**: Backend health fonctionne, page d'accueil affiche titre + statut via useApi

### Incremental Delivery

1. Setup + Foundational → Infrastructure prete
2. US1 → Environnement demarre, README exploitable → **MVP!**
3. US2+US3 → Health check + communication via proxy + useApi
4. US4 → Migrations Alembic operationnelles
5. Polish → Validation complete

---

## Notes

- [P] tasks = fichiers differents, pas de dependances
- [Story] label = tracabilite vers la user story de la spec
- Pas de tests unitaires/integration dans cette feature (prevu pour les prochaines)
- Chaque phase est un increment fonctionnel testable
- Commit apres chaque tache ou groupe logique
- Le .venv doit etre cree dans apps/backend/ (pas a la racine)
