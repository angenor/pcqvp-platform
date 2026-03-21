# Implementation Plan: Interface publique de consultation

**Branch**: `008-public-consultation` | **Date**: 2026-03-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-public-consultation/spec.md`

## Summary

Interface publique permettant a tout visiteur de consulter les comptes administratifs publies des collectivites territoriales malgaches. Backend : 3 endpoints publics (sans auth) + 1 endpoint d'export. Frontend : landing page avec GeographySelector, page de resultats avec tableaux depliables a 3 niveaux, recapitulatifs, equilibre, et exports Excel/Word.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript strict (frontend)
**Primary Dependencies**: FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, openpyxl>=3.1.0, python-docx>=1.1.0 (backend) ; Nuxt 4.4+, Tailwind CSS 4, @nuxtjs/color-mode (frontend)
**Storage**: PostgreSQL 16+ via asyncpg ; aucune nouvelle table (lecture seule des tables existantes Features 006/007)
**Testing**: pytest + pytest-asyncio + httpx (backend)
**Target Platform**: Web (serveur Linux, navigateur desktop + mobile)
**Project Type**: Web application (monorepo backend + frontend)
**Performance Goals**: Chargement tableaux < 3s pour 289 lignes, page d'accueil < 1s
**Constraints**: Mobile-first responsive, dark/light mode, SEO meta dynamiques
**Scale/Scope**: ~1500 collectivites, ~5 annees par collectivite, ~289 lignes max par tableau

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0

| Principe | Statut | Detail |
|----------|--------|--------|
| I. Donnees Ouvertes & Transparence | PASS | Feature dediee a l'acces public aux donnees. Exports Excel/Word (formats ouverts). Hierarchie geographique comme point d'entree. Formules transparentes et calculees automatiquement. |
| II. Securite & Confidentialite | PASS | Endpoints publics ne retournent que les comptes publies. Aucune donnee sensible exposee. Pas d'auth necessaire pour la consultation. Validation Pydantic sur les inputs (type, id, annee). |
| III. Simplicite & Maintenabilite | PASS | Reutilisation des services existants (account_service, compte_service). Types partages dans packages/shared. Composable useApi comme point d'entree. Pas d'abstraction prematuree. |
| Contraintes Techniques | PASS | Monorepo respecte. Stack identique (FastAPI, Nuxt 4, Tailwind CSS 4). Export via openpyxl (existant) + python-docx (ajout). |
| Workflow de Developpement | PASS | Branche dediee. Types partages. Backend/frontend testables independamment. |

### Post-Phase 1 (re-evaluation)

| Principe | Statut | Detail |
|----------|--------|--------|
| I. Donnees Ouvertes | PASS | API publique structuree avec 4 endpoints. Exports multi-feuilles reproduisant le document officiel. |
| II. Securite | PASS | Filtre status="published" applique dans le service, pas seulement dans le router. Aucune information de brouillon accessible. |
| III. Simplicite | PASS | 1 nouveau router, 2 nouveaux services (public + export), reutilisation maximale. Frontend : 3 composants tableau + 1 composable + 2 pages. |

## Project Structure

### Documentation (this feature)

```text
specs/008-public-consultation/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── public-api.md    # API contracts
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
apps/backend/
├── app/
│   ├── main.py                          # MODIFIE: montage public_comptes_router
│   ├── routers/
│   │   └── public_comptes.py            # NOUVEAU: endpoints publics
│   ├── services/
│   │   ├── public_service.py            # NOUVEAU: lecture comptes publies
│   │   ├── export_service.py            # NOUVEAU: generation Excel/Word
│   │   ├── account_service.py           # EXISTANT: calculs (reutilise)
│   │   └── compte_service.py            # EXISTANT: chargement (reutilise)
│   └── schemas/
│       └── public.py                    # NOUVEAU: schemas reponse publics
├── tests/
│   └── test_public_comptes.py           # NOUVEAU: tests endpoints publics
└── pyproject.toml                       # MODIFIE: ajout python-docx

apps/frontend/
├── app/
│   ├── pages/
│   │   ├── index.vue                    # MODIFIE: landing page publique
│   │   └── collectivite/
│   │       └── [type]-[id].vue          # NOUVEAU: page de resultats
│   ├── components/
│   │   ├── AccountTable.vue             # NOUVEAU: tableau depliable 3 niveaux
│   │   ├── RecapTable.vue               # NOUVEAU: recapitulatifs recettes + depenses
│   │   ├── EquilibreTable.vue           # NOUVEAU: tableau d'equilibre
│   │   └── GeographySelector.vue        # MODIFIE: prop navigation flexible
│   ├── composables/
│   │   └── usePublicComptes.ts          # NOUVEAU: appels API publique
│   └── types/
│       └── comptes.ts                   # MODIFIE: types reponse publique

packages/shared/
└── types/
    └── public.ts                        # NOUVEAU: types partages API publique
```

**Structure Decision**: Web application monorepo existante. Backend : nouveau router + 2 services + 1 schema. Frontend : 2 pages + 3 composants + 1 composable. Aucune nouvelle table DB.
