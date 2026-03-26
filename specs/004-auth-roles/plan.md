# Implementation Plan: Authentification et gestion des rôles

**Branch**: `004-auth-roles` | **Date**: 2026-03-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-auth-roles/spec.md`

## Summary

Implémenter l'authentification JWT avec refresh tokens et le contrôle d'accès par rôles (admin/éditeur) pour la plateforme PCQVP. Le backend expose 4 endpoints auth via FastAPI avec hashage bcrypt et verrouillage brute force. Le frontend fournit une page de connexion, un layout admin avec dark/light mode, et un middleware de protection des routes.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript strict (frontend)
**Primary Dependencies**: FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, python-jose[cryptography], passlib[bcrypt] (backend) ; Nuxt 4.4+, @tailwindcss/vite, @nuxtjs/color-mode (frontend)
**Storage**: PostgreSQL 16+ via asyncpg
**Testing**: pytest + httpx (backend), Vitest (frontend)
**Target Platform**: Linux server (Docker)
**Project Type**: Web application (monorepo)
**Performance Goals**: Standard web app (< 500ms auth endpoints)
**Constraints**: JWT access token 30min, refresh token 7 jours, verrouillage après 5 échecs pendant 15min
**Scale/Scope**: Plateforme admin interne, < 100 utilisateurs

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principe | Statut | Détail |
|----------|--------|--------|
| JWT avec refresh tokens | OK | Access token 30min + refresh token 7 jours |
| Mots de passe hashés avec bcrypt | OK | passlib[bcrypt] |
| Entrées validées (Pydantic v2 backend, TypeScript frontend) | OK | Schemas Pydantic pour tous les endpoints |
| Rôles vérifiés à chaque requête protégée | OK | Dépendances FastAPI get_current_user, require_role |
| CORS restrictif en production | OK | Déjà configuré dans main.py |
| Pas de secrets dans logs/réponses/code | OK | Tokens/passwords jamais exposés |
| Migrations réversibles | OK | Alembic downgrade prévu |
| Code simple et lisible | OK | Pas de sur-ingénierie |
| Responsabilité unique par module | OK | Séparation router/service/model/schema |
| Pas d'abstraction prématurée | OK | Accès direct DB dans services |
| Tests chemins critiques (pytest/Vitest) | OK | Tests auth backend prévus |
| Linting ruff/ESLint | OK | Déjà configuré |
| useApi point d'entrée unique API | OK | Composable useApi prévu |

**Résultat** : Aucune violation. Gate passée.

## Project Structure

### Documentation (this feature)

```text
specs/004-auth-roles/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── auth-api.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/backend/
├── app/
│   ├── core/
│   │   ├── config.py          # (modifier) Ajouter JWT_SECRET, JWT_ALGORITHM, etc.
│   │   ├── database.py        # (existant)
│   │   └── security.py        # (nouveau) JWT encode/decode, password hash/verify
│   ├── models/
│   │   ├── __init__.py        # (existant)
│   │   ├── base.py            # (nouveau) Base déclarative SQLAlchemy
│   │   └── user.py            # (nouveau) Modèle User
│   ├── schemas/
│   │   ├── __init__.py        # (nouveau)
│   │   └── auth.py            # (nouveau) Schemas Pydantic auth
│   ├── routers/
│   │   ├── __init__.py        # (nouveau)
│   │   └── auth.py            # (nouveau) Endpoints /api/auth/*
│   ├── services/
│   │   ├── __init__.py        # (nouveau)
│   │   └── auth.py            # (nouveau) Logique métier auth
│   └── main.py                # (modifier) Inclure router auth
├── alembic/
│   └── versions/
│       └── xxxx_create_users_table.py  # (nouveau) Migration users
├── scripts/
│   └── seed_admin.py          # (nouveau) Script seed admin initial
└── tests/
    ├── __init__.py             # (nouveau)
    ├── conftest.py             # (nouveau) Fixtures pytest
    └── test_auth.py            # (nouveau) Tests endpoints auth

apps/frontend/
└── app/
    ├── pages/
    │   └── admin/
    │       ├── login.vue       # (nouveau) Page connexion
    │       └── index.vue       # (nouveau) Dashboard placeholder
    ├── composables/
    │   ├── useApi.ts           # (nouveau) Client API centralisé
    │   └── useAuth.ts          # (nouveau) State auth + login/logout/refresh
    ├── middleware/
    │   └── auth.ts             # (nouveau) Protection routes /admin/*
    └── layouts/
        └── admin.vue           # (nouveau) Layout sidebar + header + dark/light mode
```

**Structure Decision** : Structure existante du monorepo respectée. Backend suit la convention constitution : `app/core/`, `app/models/`, `app/schemas/`, `app/routers/`, `app/services/`. Frontend suit Nuxt 4 : tout dans `app/`. Le composable `useApi` centralise les appels API conformément à la constitution.

## Complexity Tracking

Aucune violation de constitution, pas de justification nécessaire.
