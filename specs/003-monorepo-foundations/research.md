# Research: Fondations du monorepo

**Branch**: `003-monorepo-foundations` | **Date**: 2026-03-20

## R1 - Connexion PostgreSQL async (database.py)

**Decision**: Utiliser `create_async_engine` + `async_sessionmaker(class_=AsyncSession, expire_on_commit=False)` de SQLAlchemy 2.0.48+. Dependency injection via un generateur `get_db` qui yield une `AsyncSession`.

**Rationale**: Pattern recommande par la documentation officielle SQLAlchemy 2.0 et FastAPI. `expire_on_commit=False` evite les erreurs d'acces aux attributs apres commit dans un contexte async. `asyncpg` est le driver async le plus performant pour PostgreSQL.

**Alternatives considered**:
- `databases` (abandonné, moins d'intégration SQLAlchemy 2.0)
- `psycopg3` async (viable mais ecosysteme moins mature avec SQLAlchemy)

## R2 - Configuration (config.py)

**Decision**: `pydantic-settings` v2 avec `BaseSettings` lisant un fichier `.env` via `python-dotenv`. La classe Settings expose `DATABASE_URL`, `CORS_ORIGINS`, `BACKEND_HOST`, `BACKEND_PORT`.

**Rationale**: Pattern standard pour FastAPI. Validation de types automatique, valeurs par defaut, documentation implicite des variables.

**Alternatives considered**:
- `environs` (moins integre avec l'ecosysteme Pydantic/FastAPI)
- Variables d'environnement brutes via `os.getenv` (pas de validation)

## R3 - Alembic async

**Decision**: Initialiser avec `alembic init -t async` qui genere un `env.py` preconfigure pour les migrations async. Le `env.py` utilise `async_engine_from_config` + `connection.run_sync(do_run_migrations)`. Le `target_metadata` pointe vers `Base.metadata`.

**Rationale**: Template officiel Alembic pour les drivers async. Le pattern `run_sync` permet de reutiliser la logique de migration synchrone dans un contexte async.

**Alternatives considered**:
- Configuration manuelle du env.py (plus fragile, meme resultat)
- Alembic en pyproject.toml uniquement (possible mais moins courant)

## R4 - Health endpoint

**Decision**: `GET /health` execute `text("SELECT 1")` via une session async. Retourne `{"status": "ok", "db": "connected"}` (HTTP 200) ou `{"status": "ok", "db": "disconnected", "detail": "..."}` (HTTP 503) si la DB est inaccessible.

**Rationale**: Distinction claire entre service up et DB up. HTTP 503 signale un probleme aux outils de monitoring. `text("SELECT 1")` est le test de connectivite le plus leger.

**Alternatives considered**:
- Retourner toujours HTTP 200 avec statut degrade (moins standard)
- Utiliser `connection.execute(select(1))` (equivalent, plus verbeux)

## R5 - pyproject.toml et ruff

**Decision**: Section `[project]` avec les dependances specifiees. Section `[tool.ruff]` avec `target-version = "py312"`, `line-length = 88`. `[tool.ruff.lint]` avec `select = ["E", "F", "I", "UP", "W"]`.

**Rationale**: Ruff remplace flake8, isort, et pyupgrade en un seul outil. Les regles selectionnees couvrent : erreurs (E), pyflakes (F), imports (I), modernisation Python (UP), warnings (W).

**Alternatives considered**:
- flake8 + isort + black (plus lent, meme couverture)
- Ajouter "N" (pep8-naming) des le depart (peut attendre)

## R6 - CORS

**Decision**: `CORSMiddleware` avec `allow_origins` lu depuis la config (variable `CORS_ORIGINS`). En dev : `["http://localhost:3000"]`. En prod : restrictif (seul le domaine de production).

**Rationale**: Conforme a la constitution ("CORS restrictif en production"). La valeur est configurable via variable d'environnement.

**Alternatives considered**:
- `allow_origins=["*"]` en dev (trop permissif meme en dev)
- Pas de CORS + proxy uniquement (le proxy couvre le dev, mais CORS est necessaire pour la prod)

## R7 - Nuxt 4.4+ structure et proxy

**Decision**: Structure `app/` standard (pages, components, composables, layouts, assets). Proxy API via `nitro.devProxy` pour le dev uniquement : `/api/**` -> `http://localhost:8000`. Le composable `useApi` utilise `createUseFetch` (nouveau dans Nuxt 4.4) avec `baseURL: "/api"`.

**Rationale**: `nitro.devProxy` est specifiquement concu pour le dev et n'affecte pas la prod. `createUseFetch` est le pattern officiel Nuxt 4.4 pour creer des composables de fetch personnalises avec typage complet.

**Alternatives considered**:
- `nitro.routeRules` avec proxy (fonctionne aussi en prod, mais inutile pour cette feature)
- `$fetch` brut avec baseURL configurable (moins integre, pas de SSR-friendly)
- `vite.server.proxy` (ignore par Nuxt en faveur de nitro)

## R8 - Tailwind CSS 4

**Decision**: Plugin `@tailwindcss/vite` dans `nuxt.config.ts` sous `vite.plugins`. Point d'entree CSS : `@import "tailwindcss";` dans `app/assets/css/main.css`. Pas de `tailwind.config.js` (configuration CSS-native).

**Rationale**: Tailwind CSS 4 utilise une approche CSS-native. Le plugin Vite est le mode d'integration recommande pour les projets utilisant Vite (comme Nuxt).

**Alternatives considered**:
- `@nuxtjs/tailwindcss` module (pas encore compatible Tailwind 4 CSS-native)
- PostCSS plugin (fonctionne mais le plugin Vite est plus rapide)

## R9 - Docker Compose PostgreSQL

**Decision**: Service `postgres` avec image `postgres:16`, port `5432:5432`, volume nomme `pcqvp_pgdata`, healthcheck via `pg_isready`. Variables : `POSTGRES_USER=pcqvp`, `POSTGRES_PASSWORD` depuis `.env`, `POSTGRES_DB=pcqvp`.

**Rationale**: Les volumes nommes survivent a `docker compose down` (supprime uniquement avec `-v`). Le healthcheck permet aux services dependants d'attendre que PostgreSQL soit pret.

**Alternatives considered**:
- Bind mount pour les donnees (moins portable)
- PostgreSQL 17 (trop recent, 16 est LTS)

## R10 - Environnement virtuel Python

**Decision**: Utiliser un `.venv` local dans `apps/backend/` pour isoler les dependances Python. Le README et le quickstart documentent la creation et l'activation du venv.

**Rationale**: Pratique standard Python. Isole les dependances du projet du systeme. Compatible avec pip et les outils de l'ecosysteme.

**Alternatives considered**:
- Poetry avec son propre venv (ajoute un outil supplementaire)
- uv (plus rapide mais moins repandu)
- Conteneurisation du backend (plus lourd pour le dev)
