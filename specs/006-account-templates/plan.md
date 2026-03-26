# Implementation Plan: Structure standardisee des tableaux de comptes administratifs

**Branch**: `006-account-templates` | **Date**: 2026-03-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-account-templates/spec.md`

## Summary

Implementer la gestion des templates de comptes administratifs standardises des collectivites malgaches. Le systeme permet de definir, importer depuis Excel, consulter et modifier la structure hierarchique des comptes (recettes et depenses) a 3 niveaux avec colonnes calculees. Un script de seed importe la structure officielle (168 comptes recettes, 273 comptes depenses) et un jeu de donnees d'exemple (Andrafiabe 2023). L'interface admin permet la visualisation et l'edition de la structure.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript strict (frontend)
**Primary Dependencies**: FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, openpyxl>=3.1.0 (backend) ; Nuxt 4.4+, Tailwind CSS 4, @nuxtjs/color-mode (frontend)
**Storage**: PostgreSQL 16+ via asyncpg, 3 nouvelles tables
**Testing**: pytest + pytest-asyncio (backend), Vitest (frontend)
**Target Platform**: Web (serveur Linux, navigateurs modernes)
**Project Type**: Web service (monorepo backend + frontend)
**Performance Goals**: Affichage de 289 lignes en <3s, reponses API <500ms
**Constraints**: Templates de 168 a 273 lignes, formules simples (addition/soustraction/division), hierarchie fixe a 3 niveaux
**Scale/Scope**: ~2 templates actifs, ~450 lignes totales, ~17 colonnes, 6 endpoints API, 2 pages frontend

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principe | Requirement | Status | Notes |
|----------|-------------|--------|-------|
| I. Donnees Ouvertes | Structure standardisee malgache a 3 niveaux | PASS | FR-002, FR-003 : hierarchie Niv1/2/3 conforme |
| I. Donnees Ouvertes | Formules transparentes, verifiables, automatiques | PASS | FR-007, FR-008 : formules declaratives + aggregation |
| I. Donnees Ouvertes | API REST structuree et documentee | PASS | 6 endpoints documentes dans contracts/api.md |
| II. Securite | Roles verifies a chaque requete | PASS | Tous endpoints sous require_role("admin", "editor") |
| II. Securite | Entrees validees (Pydantic v2) | PASS | Schemas Pydantic pour toutes les entrees |
| II. Securite | Migrations reversibles | PASS | Migration 003 avec downgrade complet |
| III. Simplicite | Code simple, pas de sur-ingenierie | PASS | Suit les patterns existants (geography), pas d'abstraction prematuree |
| III. Simplicite | Tests chemins critiques | PASS | Tests import, CRUD, hierarchie, formules |
| III. Simplicite | Types partages dans packages/shared | PASS | packages/shared/types/templates.ts |
| Workflow | useApi point d'entree unique frontend | PASS | useTemplates.ts utilise useApi |
| Workflow | Changements API refletes dans types partages | PASS | Schemas backend ↔ types TypeScript synchronises |

**Post-Phase 1 re-check**: PASS - Aucune violation detectee.

## Project Structure

### Documentation (this feature)

```text
specs/006-account-templates/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: research findings
├── data-model.md        # Phase 1: entity definitions
├── quickstart.md        # Phase 1: developer setup guide
├── contracts/
│   └── api.md           # Phase 1: API endpoint contracts
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
apps/backend/
├── app/
│   ├── models/
│   │   └── account_template.py          # AccountTemplate, AccountTemplateLine, AccountTemplateColumn
│   ├── schemas/
│   │   └── account_template.py          # Pydantic schemas (Create/Update/List/Detail)
│   ├── services/
│   │   ├── template_service.py          # CRUD + query logic
│   │   └── seed_templates.py            # Excel import script (openpyxl)
│   ├── routers/
│   │   └── admin_templates.py           # 6 endpoints admin
│   └── data/
│       └── reference/
│           ├── Template_Tableaux_de_Compte_Administratif.xlsx
│           └── COMPTE_ADMINISTRATIF_COMMUNE_ANDRAFIABE_2023.xlsx
├── alembic/
│   └── versions/
│       └── 003_create_account_template_tables.py
└── tests/
    └── test_templates.py

apps/frontend/
├── app/
│   ├── pages/
│   │   └── admin/
│   │       └── templates/
│   │           ├── index.vue            # Liste des templates
│   │           └── [id].vue             # Editeur visuel de structure
│   └── composables/
│       └── useTemplates.ts              # API composable

packages/shared/
└── types/
    └── templates.ts                     # Types partages backend/frontend
```

**Structure Decision**: Monorepo existant avec apps/backend + apps/frontend + packages/shared. Les nouveaux fichiers suivent exactement les patterns etablis par les features geography (005) et auth (004). Aucune nouvelle structure ou abstraction n'est introduite.

## Complexity Tracking

> Aucune violation de constitution detectee. Pas de justification necessaire.
