# Implementation Plan: Image banniere hero section collectivites

**Branch**: `016-banner-image-hero` | **Date**: 2026-03-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/016-banner-image-hero/spec.md`

## Summary

Ajouter un champ `banner_image` (String, nullable) aux modeles Province, Region et Commune pour permettre l'association d'une image banniere via le backoffice. Cote public, afficher un hero section full-bleed (~250-300px) avec l'image en fond et le nom/type superposes lorsque la banniere est definie. Le hero remplace le bloc titre actuel ; la description riche reste affichee apres.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 async, Pydantic v2, Nuxt 4, Vue 3.5, Tailwind CSS 4
**Storage**: PostgreSQL 16 via asyncpg
**Testing**: pytest + pytest-asyncio + httpx (backend)
**Target Platform**: Web (serveur Linux + navigateur)
**Project Type**: Web application (monorepo backend + frontend + shared types)
**Performance Goals**: Standard web app - hero image chargee immediatement sans lazy-loading excessif
**Constraints**: Image max 5Mo, formats JPEG/PNG/WebP/GIF (contraintes existantes)
**Scale/Scope**: ~20 provinces, ~100 regions, ~1500 communes potentielles

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution non configuree (template par defaut). Aucun gate actif. Passage libre.

## Project Structure

### Documentation (this feature)

```text
specs/016-banner-image-hero/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output - decisions techniques
├── data-model.md        # Phase 1 output - schema des entites
├── quickstart.md        # Phase 1 output - guide de demarrage
├── contracts/           # Phase 1 output - contrats API
│   └── api-changes.md   # Changements d'endpoints
├── checklists/
│   └── requirements.md  # Checklist qualite spec
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   └── geography.py          # Ajout champ banner_image sur Province, Region, Commune
│   ├── schemas/
│   │   └── geography.py          # Ajout banner_image aux schemas Create/Update/Detail
│   ├── services/
│   │   ├── geography.py          # Passage banner_image dans create/update
│   │   └── public_service.py     # Inclusion banner_image dans description response
│   └── routers/
│       ├── admin_geography.py    # Inchange (schemas geres automatiquement)
│       └── public_comptes.py     # Inchange (service gere la serialisation)
├── alembic/
│   └── versions/
│       └── 007_add_banner_image.py  # Migration ajout colonne

frontend/
├── app/
│   ├── components/
│   │   └── CollectiviteHero.vue     # Nouveau composant hero section
│   ├── pages/
│   │   ├── admin/geography/
│   │   │   ├── communes/[id].vue    # Ajout champ upload banniere
│   │   │   ├── regions/[id]/index.vue  # Ajout champ upload banniere
│   │   │   └── provinces/[id]/index.vue  # Ajout champ upload banniere
│   │   └── collectivite/
│   │       └── [type]-[id].vue      # Integration hero section conditionnel
│   └── composables/
│       └── useGeography.ts          # Ajout banner_image aux params CRUD

packages/shared/
└── types/
    ├── geography.ts                 # banner_image dans Detail interfaces
    └── public.ts                    # banner_image dans PublicDescriptionResponse
```

**Structure Decision**: Monorepo existant avec backend/, frontend/, packages/shared/. Aucun nouveau dossier structurel. Un seul nouveau composant (`CollectiviteHero.vue`).

## Complexity Tracking

Aucune violation de constitution a justifier.
