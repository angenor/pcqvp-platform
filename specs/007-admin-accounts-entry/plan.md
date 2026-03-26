# Implementation Plan: Saisie et stockage des comptes administratifs

**Branch**: `007-admin-accounts-entry` | **Date**: 2026-03-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-admin-accounts-entry/spec.md`

## Summary

Implementer la saisie et le stockage des comptes administratifs des collectivites territoriales malgaches. Le systeme permet de creer un compte pour une collectivite et une annee, de saisir les recettes et depenses (par programme) avec auto-save ligne par ligne, de calculer dynamiquement les recapitulatifs et le tableau d'equilibre, et de publier/depublier les comptes avec journal des modifications.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript strict (frontend)
**Primary Dependencies**: FastAPI 0.135+, SQLAlchemy 2.0.48+ async, Pydantic v2, asyncpg, openpyxl (backend) ; Nuxt 4.4+, Tailwind CSS 4, @nuxtjs/color-mode (frontend)
**Storage**: PostgreSQL 16+ via asyncpg ; 5 nouvelles tables (comptes_administratifs, recette_lines, depense_programs, depense_lines, account_change_logs)
**Testing**: pytest + pytest-asyncio + httpx (backend)
**Target Platform**: Web application (navigateur)
**Project Type**: Web application monorepo (backend API + frontend SPA)
**Performance Goals**: <3s chargement page saisie (289 lignes), <1s navigation onglets, auto-save <500ms par cellule
**Constraints**: Calculs dynamiques cote serveur (jamais persistees), valeurs entieres en Ariary, structure liee aux templates existants (Feature 006)
**Scale/Scope**: ~300 collectivites, ~289 lignes max par tableau, 3+ programmes par compte, ~10 utilisateurs simultanes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0

| Principe | Statut | Justification |
|----------|--------|---------------|
| I. Donnees Ouvertes & Transparence | PASS | Les comptes suivent la structure standardisee malgache (via templates Feature 006), les formules sont calculees dynamiquement et transparentes, la hierarchie geographique est le point d'entree pour creer un compte |
| II. Securite & Confidentialite | PASS | Auth JWT existante reutilisee, roles admin/editor verifies par endpoint (admin seul peut publier), validation Pydantic v2 sur toutes les entrees, migrations reversibles |
| III. Simplicite & Maintenabilite | PASS | Suit les patterns existants (service/router/schema), un module par responsabilite, types partages dans packages/shared, tests sur les calculs critiques |

### Post-Phase 1 (re-evaluation)

| Principe | Statut | Justification |
|----------|--------|---------------|
| I. Donnees Ouvertes & Transparence | PASS | API REST expose les comptes de maniere structuree, recapitulatifs et equilibre calculables via endpoints dedies |
| II. Securite & Confidentialite | PASS | Journal des modifications sur comptes publies (FR-020), collectivite_id valide par lookup avant creation |
| III. Simplicite & Maintenabilite | PASS | 5 tables simples, service de calcul pur (sans effets de bord), pas d'abstraction prematuree - calculs dans un seul fichier service |

## Project Structure

### Documentation (this feature)

```text
specs/007-admin-accounts-entry/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api-endpoints.md
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
apps/backend/
├── alembic/versions/
│   └── 004_create_compte_administratif_tables.py
├── app/
│   ├── models/
│   │   └── compte_administratif.py    # CompteAdministratif, RecetteLine, DepenseProgram, DepenseLine, AccountChangeLog
│   ├── schemas/
│   │   └── compte_administratif.py    # Pydantic schemas (Create, Update, Response, Recap)
│   ├── routers/
│   │   └── admin_comptes.py           # Endpoints CRUD + saisie + recapitulatifs
│   ├── services/
│   │   ├── account_service.py         # Service de calcul (recapitulatifs, equilibre, sommes hierarchiques)
│   │   └── compte_service.py          # CRUD comptes, upsert recettes/depenses, gestion programmes
│   └── tests/
│       └── test_comptes.py            # Tests API + calculs

apps/frontend/
├── app/
│   ├── pages/admin/accounts/
│   │   ├── index.vue                  # Liste des comptes avec filtres
│   │   ├── new.vue                    # Formulaire de creation
│   │   └── [id]/
│   │       ├── recettes.vue           # Saisie des recettes (auto-save)
│   │       ├── depenses.vue           # Saisie depenses par programme (onglets, auto-save)
│   │       └── recap.vue              # Recapitulatifs et equilibre (lecture seule)
│   ├── composables/
│   │   └── useComptes.ts              # Composable API comptes
│   └── components/
│       └── AccountDataTable.vue       # Composant tableau de saisie reutilisable (recettes + depenses)

packages/shared/
└── types/
    └── comptes.ts                     # Types partages CompteAdministratif, RecetteLine, etc.
```

**Structure Decision**: Suit le pattern web-app monorepo existant. Un seul modele Python regroupe les 5 entites. Deux services backend : `compte_service.py` pour le CRUD et `account_service.py` pour les calculs purs. Un composant `AccountDataTable.vue` partage entre recettes et depenses (meme structure de tableau editable, colonnes differentes).

## Complexity Tracking

Aucune violation de constitution detectee.
