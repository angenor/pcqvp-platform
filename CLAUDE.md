# pcqvp-platform Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-20

## Active Technologies
- Python 3.12+ (backend), TypeScript strict (frontend) + FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, python-jose[cryptography], passlib[bcrypt] (backend) ; Nuxt 4.4+, @tailwindcss/vite, @nuxtjs/color-mode (frontend) (004-auth-roles)
- PostgreSQL 16+ via asyncpg (004-auth-roles)
- Python 3.12+ (backend), TypeScript strict (frontend) + FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, Nuxt 4.4+, Tailwind CSS 4, @nuxtjs/color-mode (005-geography-hierarchy)
- PostgreSQL 16+ via asyncpg, JSONB pour le contenu riche (005-geography-hierarchy)

- Python 3.12+ (backend), TypeScript strict (frontend) + FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, Alembic, Pydantic Settings, Uvicorn (backend) ; Nuxt 4.4+, @tailwindcss/vite (frontend) (003-monorepo-foundations)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.12+ (backend), TypeScript strict (frontend): Follow standard conventions

## Recent Changes
- 005-geography-hierarchy: Added Python 3.12+ (backend), TypeScript strict (frontend) + FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, Nuxt 4.4+, Tailwind CSS 4, @nuxtjs/color-mode
- 004-auth-roles: Added Python 3.12+ (backend), TypeScript strict (frontend) + FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, python-jose[cryptography], passlib[bcrypt] (backend) ; Nuxt 4.4+, @tailwindcss/vite, @nuxtjs/color-mode (frontend)

- 003-monorepo-foundations: Added Python 3.12+ (backend), TypeScript strict (frontend) + FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, Alembic, Pydantic Settings, Uvicorn (backend) ; Nuxt 4.4+, @tailwindcss/vite (frontend)

<!-- MANUAL ADDITIONS START -->
## Frontend Rules

- Toute page ou composant Vue créé DOIT être compatible dark/light mode (classes Tailwind `dark:` obligatoires). Utiliser `@nuxtjs/color-mode` avec la stratégie `class`.
<!-- MANUAL ADDITIONS END -->

## Parallel Sub-agents Strategy

Use multiple sub-agents in parallel for efficiency(10 max):
- Search frontend + backend simultaneously
- Explore multiple files/folders at the same time
- Run tests + verifications in parallel after modifications
