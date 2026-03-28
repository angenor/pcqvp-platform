# Implementation Plan: Section Éditoriaux du Backoffice

**Branch**: `015-backoffice-editorials` | **Date**: 2026-03-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/015-backoffice-editorials/spec.md`

## Summary

Ajouter une section "Éditoriaux" dans le backoffice permettant aux administrateurs/éditeurs de gérer dynamiquement le contenu de la page d'accueil (hero section, corps de page en contenu riche, footer). Le backend expose des endpoints CRUD pour le contenu éditorial, le frontend propose une page admin avec onglets et met à jour dynamiquement la page d'accueil et le footer.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 async, Pydantic v2, Nuxt 4, Vue 3.5, EditorJS, Tailwind CSS 4
**Storage**: PostgreSQL 16 via asyncpg
**Testing**: pytest + pytest-asyncio + httpx (backend)
**Target Platform**: Web (serveur Linux, navigateurs modernes)
**Project Type**: Web application (monorepo backend + frontend + shared types)
**Performance Goals**: Temps de réponse API < 200ms, affichage instantané du contenu éditorial
**Constraints**: Dark/light mode obligatoire, rôles admin/editor existants
**Scale/Scope**: 1 nouvelle page admin, 3 onglets, ~7 sections éditoriables, 3 nouveaux modèles DB

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution non définie (template vide). Aucun gate à valider. Passage direct.

## Project Structure

### Documentation (this feature)

```text
specs/015-backoffice-editorials/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contracts)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   └── editorial.py          # EditorialContent, ContactInfo, ResourceLink models
│   ├── schemas/
│   │   └── editorial.py          # Pydantic schemas (Create, Update, Response)
│   ├── services/
│   │   └── editorial.py          # Business logic CRUD
│   ├── routers/
│   │   ├── admin_editorial.py    # Admin CRUD endpoints
│   │   └── public_editorial.py   # Public read-only endpoint
│   └── main.py                   # Register new routers
├── alembic/
│   └── versions/
│       └── 006_create_editorial_tables.py
└── tests/
    └── test_editorial.py

frontend/
└── app/
    ├── pages/
    │   └── admin/
    │       └── editorial.vue     # Page admin avec onglets
    ├── composables/
    │   └── useEditorial.ts       # Composable API éditorial
    ├── components/
    │   └── admin/
    │       └── AdminSidebar.vue  # Ajout menu item "Éditoriaux"
    ├── layouts/
    │   └── default.vue           # Footer dynamique
    └── pages/
        └── index.vue             # Hero + corps dynamiques

packages/shared/
└── types/
    └── editorial.ts              # Types partagés
```

**Structure Decision**: Monorepo existant (backend + frontend + shared). Nouveaux fichiers ajoutés dans les dossiers existants selon les conventions du projet.

## Complexity Tracking

Aucune violation de constitution à justifier.
