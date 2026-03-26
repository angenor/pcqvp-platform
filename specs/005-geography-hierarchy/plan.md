# Implementation Plan: Gestion de la hierarchie geographique

**Branch**: `005-geography-hierarchy` | **Date**: 2026-03-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-geography-hierarchy/spec.md`

## Summary

Implementer la hierarchie geographique de Madagascar (Province > Region > Commune) avec :
- Modeles SQLAlchemy + migration Alembic (3 tables avec JSONB pour contenu riche)
- API REST publique (consultation) et admin (CRUD protege avec pagination)
- Selecteur chaine a 4 niveaux sur la page d'accueil (Province* > Region* > Commune > Annee*)
- Pages admin avec listes paginées, recherche et editeur de contenu riche en blocs
- Types partages dans packages/shared

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript strict (frontend)
**Primary Dependencies**: FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, Nuxt 4.4+, Tailwind CSS 4, @nuxtjs/color-mode
**Storage**: PostgreSQL 16+ via asyncpg, JSONB pour le contenu riche
**Testing**: pytest + pytest-asyncio (backend), Vitest (frontend)
**Target Platform**: Web application (serveur Linux + navigateur)
**Project Type**: Monorepo web-service (apps/backend + apps/frontend + packages/shared)
**Performance Goals**: <1s pour le chargement des options du selecteur, <200ms pour les reponses API
**Constraints**: Dark/light mode obligatoire sur toutes les pages, async-first, migrations reversibles
**Scale**: ~6 provinces, ~23 regions, ~1500 communes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0 Check

| Principe | Exigence | Statut |
|----------|----------|--------|
| I. Donnees Ouvertes | Hierarchie geographique = point d'entree principal | PASS - C'est exactement cette feature |
| I. Donnees Ouvertes | API REST structuree et documentee | PASS - Contrats API definis dans contracts/api.md |
| II. Securite | Roles verifies a chaque requete protegee | PASS - Utilisation de require_role() existant |
| II. Securite | Entrees validees (Pydantic + TS) | PASS - Schemas Pydantic pour tous les endpoints |
| II. Securite | Migrations reversibles | PASS - Downgrade prevu dans la migration |
| III. Simplicite | Code simple, pas de sur-ingenierie | PASS - Patterns existants reutilises |
| III. Simplicite | Types partages dans packages/shared | PASS - geography.ts prevu |
| Workflow | useApi point d'entree unique | PASS - Tous les appels via useApi |
| Workflow | Migrations via Alembic | PASS - Migration 002 prevue |

### Post-Phase 1 Check

| Principe | Exigence | Statut |
|----------|----------|--------|
| I. Donnees Ouvertes | Hierarchie = point d'entree | PASS - Selecteur sur page d'accueil |
| II. Securite | Validation entrees | PASS - Pydantic discriminated union pour blocs JSONB |
| III. Simplicite | Pas d'abstraction prematuree | PASS - Editeur custom leger, pas de lib externe |
| III. Simplicite | Responsabilite unique par module | PASS - geography.py par couche (model/schema/router/service) |

Aucune violation. Pas de Complexity Tracking necessaire.

## Project Structure

### Documentation (this feature)

```text
specs/005-geography-hierarchy/
├── plan.md
├── spec.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api.md
├── checklists/
│   └── requirements.md
└── tasks.md              (Phase 2 - /speckit.tasks)
```

### Source Code (repository root)

```text
apps/backend/app/
├── models/
│   ├── base.py                    # existant (UUIDBase, TimestampMixin)
│   ├── user.py                    # existant
│   └── geography.py               # NOUVEAU: Province, Region, Commune
├── schemas/
│   ├── auth.py                    # existant
│   └── geography.py               # NOUVEAU: schemas Pydantic + blocs JSONB
├── routers/
│   ├── auth.py                    # existant
│   ├── geography.py               # NOUVEAU: routes publiques GET
│   └── admin_geography.py         # NOUVEAU: routes admin CRUD + listes paginees
├── services/
│   ├── auth.py                    # existant
│   └── geography.py               # NOUVEAU: logique metier CRUD + integrite
├── core/                          # existant (config, database, security)
└── main.py                        # existant (ajouter inclusion des nouveaux routers)

apps/backend/alembic/versions/
└── 002_create_geography_tables.py # NOUVEAU: migration

apps/frontend/app/
├── components/
│   ├── GeographySelector.vue      # NOUVEAU: selecteur 4 niveaux chaines
│   ├── RichContentEditor.vue      # NOUVEAU: editeur de blocs
│   └── RichContentRenderer.vue    # NOUVEAU: rendu public du contenu riche
├── composables/
│   ├── useAuth.ts                 # existant
│   ├── useApi.ts                  # existant
│   └── useGeography.ts            # NOUVEAU: API calls geographie
├── pages/
│   ├── index.vue                  # MODIFIE: integrer GeographySelector
│   └── admin/
│       ├── index.vue              # existant
│       └── geography/
│           ├── provinces/
│           │   ├── index.vue      # NOUVEAU: liste admin provinces
│           │   └── [id].vue       # NOUVEAU: edition province
│           ├── regions/
│           │   ├── index.vue      # NOUVEAU: liste admin regions
│           │   └── [id].vue       # NOUVEAU: edition region
│           └── communes/
│               ├── index.vue      # NOUVEAU: liste admin communes
│               └── [id].vue       # NOUVEAU: edition commune
├── layouts/
│   └── admin.vue                  # MODIFIE: ajouter lien navigation "Geographie"
└── types/
    ├── auth.ts                    # existant
    └── geography.ts               # NOUVEAU: types locaux (re-export shared)

packages/shared/types/
├── auth.ts                        # existant
└── geography.ts                   # NOUVEAU: types partages

apps/backend/tests/
├── conftest.py                    # existant
├── test_auth.py                   # existant
└── test_geography.py              # NOUVEAU: tests API geographie
```

**Structure Decision**: Monorepo existant avec apps/backend + apps/frontend + packages/shared. Les nouveaux fichiers suivent exactement les patterns etablis par la feature 004 (un fichier par couche : model, schema, router, service). Les 3 entites geographiques partagent le meme fichier par couche car elles sont etroitement liees.
