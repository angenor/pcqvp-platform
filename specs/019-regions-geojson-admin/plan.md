# Implementation Plan: Carte interactive Madagascar — GeoJSON administrable depuis le back-office

**Branch**: `019-regions-geojson-admin` | **Date**: 2026-05-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/019-regions-geojson-admin/spec.md`

## Summary

Permettre à un administrateur de téléverser un GeoJSON régional (jusqu'à 50 Mo, ex. export Overpass Turbo de 22 Mo) depuis le back-office. Un pipeline backend filtre les features `admin_level=4`, déduplique par nom, normalise via une table de correspondance, génère un `region_code` stable, simplifie les géométries (Visvalingam-weighted) et réduit la précision à 4 décimales pour produire un GeoJSON < 1 Mo. Les versions sont historisées en JSONB dans une table dédiée (au plus 1 active, quota 50, purge LRU des inactives). Un endpoint public sert la version active avec ETag et `Cache-Control: public, max-age=3600`. La carte d'accueil (`MadagascarMap.vue`) consomme cet endpoint au lieu du package figé `@amcharts/amcharts5-geodata`. Les uploads > 5 s basculent en tâche asynchrone (FastAPI `BackgroundTasks` + statut polling). Toutes les opérations admin sont restreintes au rôle `admin` et tracées via `AuditLog`.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x (frontend)
**Primary Dependencies (backend)**: FastAPI 0.135+, SQLAlchemy 2.0 async, asyncpg, Pydantic v2, Alembic, slowapi, **shapely>=2.0** (nouveau), **simplification>=0.7** (nouveau, Visvalingam-weighted), **ijson>=3.2** (nouveau, parsing streaming pour fichiers > 10 Mo)
**Primary Dependencies (frontend)**: Nuxt 4.4+, Vue 3.5+, Tailwind CSS 4, `@amcharts/amcharts5` (déjà présent — réutilisé pour rendu, pas pour geodata), `@nuxtjs/color-mode`. Le package `@amcharts/amcharts5-geodata` reste installé mais n'est plus chargé par `MadagascarMap.vue`.
**Storage**: PostgreSQL 16 via asyncpg ; GeoJSON traité stocké en colonne JSONB (transactions, versionning natif, pas de fichier sur disque). Fichier source brut NON persisté (cf. clarification spec).
**Testing**: pytest + pytest-asyncio + httpx (backend) ; Vitest (composable) + Playwright E2E (parcours admin + carte d'accueil)
**Target Platform**: serveur Linux + navigateur moderne (dark/light, responsive)
**Project Type**: Web application monorepo (backend FastAPI + frontend Nuxt + packages/shared)
**Performance Goals**:
- Pipeline 22 Mo → < 1 Mo : ≤ 30 s (SC-003), ratio compression ≥ 95 %
- Endpoint public : < 200 ms p95 sur version active déjà en cache PG ; carte d'accueil rendue < 2 s 3G simulé (SC-002)
- Activation atomique : < 200 ms (verrou `SELECT ... FOR UPDATE` sur la table de versions)

**Constraints**:
- Bascule synchrone → asynchrone à 5 s (FR-009) : seuil mesuré sur le parse + filtrage initial ; au-delà, `BackgroundTasks` + polling
- Charge mémoire backend : streaming `ijson` pour le parse initial (éviter ~150-200 Mo RAM sur fichier 22 Mo)
- Bundle frontend : pas de croissance > 50 Ko (critère non-régression)
- `MadagascarMap.vue` : reste sous 320 lignes (255 actuellement)
- Rate limiting upload : 10/h/admin via `slowapi`

**Scale/Scope**:
- Volume : ~2-5 uploads / an en régime nominal ; pic possible 10/h
- Stockage : ≤ 50 versions × ≤ 1 Mo JSONB ≈ 50 Mo en base, négligeable
- Utilisateurs : 1-5 admins ; visiteurs anonymes (carte d'accueil) : trafic existant de la plateforme

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

La constitution `.specify/memory/constitution.md` est un template non ratifié (placeholders `[PRINCIPLE_*]`). Aucun principe contraignant n'est codifié pour le projet. Les conventions appliquées proviennent du `CLAUDE.md` du repo et des règles globales (rules/common, rules/python, rules/typescript) :

- **Immutabilité, fichiers < 800 lignes, fonctions < 50 lignes, tests ≥ 80 %, pas de secrets en dur, validation aux frontières** — respectés par conception (voir Phase 1).
- **Pattern repository / service** : aligné avec `services/*.py` existants (audit_log, compte_service, geography, etc.).
- **Code review obligatoire** post-implémentation (déclencher l'agent `code-reviewer`).

**Statut gate** : PASS (aucun principe ratifié à enfreindre, conventions standard du repo respectées).

## Project Structure

### Documentation (this feature)

```text
specs/019-regions-geojson-admin/
├── spec.md                       # Spec fonctionnelle (clarifiée)
├── plan.md                       # Ce fichier
├── research.md                   # Phase 0 — décisions techniques
├── data-model.md                 # Phase 1 — modèle SQLAlchemy + invariants
├── quickstart.md                 # Phase 1 — parcours dev local
├── contracts/                    # Phase 1 — contrats API
│   ├── admin-geodata.openapi.yaml
│   ├── public-geography-geojson.openapi.yaml
│   └── README.md
├── checklists/
│   └── requirements.md           # Spec quality
└── tasks.md                      # Phase 2 — produit par /speckit.tasks
```

### Source Code (repository root)

Application web monorepo existante. Ajouts/modifications ciblés :

```text
backend/
├── app/
│   ├── models/
│   │   └── geodata_version.py            # NOUVEAU — modèle GeodataVersion (UUIDBase + JSONB)
│   ├── schemas/
│   │   └── geodata.py                    # NOUVEAU — Pydantic v2 (UploadResponse, VersionListItem, JobStatus, etc.)
│   ├── services/
│   │   ├── geodata_pipeline.py           # NOUVEAU — pipeline pur (parse → filter → dedup → normalize → simplify)
│   │   ├── geodata_service.py            # NOUVEAU — orchestration DB (versions, activation, purge LRU)
│   │   └── geodata_jobs.py               # NOUVEAU — registre in-memory des tâches asynchrones (statut polling)
│   ├── routers/
│   │   ├── admin_geodata.py              # NOUVEAU — POST /upload, GET /versions, GET /versions/{id}, POST /activate, DELETE
│   │   └── geography.py                  # MODIFIÉ — ajout GET /api/geography/regions/geojson (ETag, 304)
│   ├── core/
│   │   └── config.py                     # MODIFIÉ — GEODATA_SIMPLIFY_RATIO, GEODATA_MAX_VERSIONS, GEODATA_RATE_LIMIT, GEODATA_NAME_ALIASES
│   └── main.py                           # MODIFIÉ — include_router(admin_geodata_router)
├── alembic/versions/
│   ├── 009_create_geodata_versions.py    # NOUVEAU — table + index partiel unique sur is_active
│   └── 010_seed_geodata_initial.py       # NOUVEAU — seed des 23 régions (GeoJSON pré-traité)
├── pyproject.toml                        # MODIFIÉ — +shapely, +simplification, +ijson
└── tests/
    ├── unit/test_geodata_pipeline.py     # NOUVEAU
    ├── integration/test_admin_geodata.py # NOUVEAU
    └── integration/test_public_geojson.py # NOUVEAU

frontend/
├── app/
│   ├── pages/admin/geodata/
│   │   └── regions/index.vue             # NOUVEAU — page liste + actions
│   ├── components/geodata/
│   │   ├── UploadVersionModal.vue        # NOUVEAU — drag&drop, progression, polling
│   │   ├── PreviewVersionModal.vue       # NOUVEAU — mini-carte amCharts
│   │   ├── ActivateVersionModal.vue      # NOUVEAU — confirmation
│   │   └── VersionTable.vue              # NOUVEAU — tableau historique
│   ├── composables/
│   │   └── useGeodataAdmin.ts            # NOUVEAU — uploadVersion, listVersions, activateVersion, deleteVersion, previewVersion, pollJob
│   ├── components/
│   │   └── MadagascarMap.vue             # MODIFIÉ — fetch endpoint public, suppression mapping figé, fallback erreur
│   ├── layouts/
│   │   └── admin.vue                     # MODIFIÉ — ajout lien sidebar « Géodonnées » sous Géographie
│   └── types/
│       └── geodata.ts                    # NOUVEAU — interfaces GeodataVersion, JobStatus, etc.
└── tests/
    ├── unit/useGeodataAdmin.spec.ts      # NOUVEAU
    └── e2e/geodata-admin.spec.ts         # NOUVEAU

packages/shared/
└── src/types/geodata.ts                  # NOUVEAU — types partagés (UploadResponse, JobStatus)

docs/admin/
└── geodata-management.md                 # NOUVEAU — procédure Overpass + upload + rollback
```

**Structure Decision**: Web application monorepo (existant). Ajout d'un domaine `geodata` isolé côté backend (modèle / schema / service / router) et côté frontend (page / components / composable), respectant le pattern actuel des autres domaines (editorial, comptes, collectivity_documents, etc.). Aucun nouveau projet ni service standalone. Le seed initial 23 régions est livré comme JSON statique dans la migration Alembic afin que la fonctionnalité soit utilisable dès la première instance.

## Complexity Tracking

> Constitution sans principes ratifiés — aucune dérogation à justifier.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| (aucune) | — | — |

## Phase 0 — Research

Voir [`research.md`](./research.md) pour les décisions techniques détaillées :
- Choix de `shapely` + `simplification` (Visvalingam-weighted) vs alternatives (`topojson`, `geopandas`, `mapshaper-cli`).
- Choix de FastAPI `BackgroundTasks` vs Celery/Dramatiq pour l'asynchrone.
- Stratégie ETag (UUID `version_id` weak ETag).
- Streaming `ijson` pour le filtrage initial (mémoire).
- Génération du `region_code` (slugify Unicode NFD → ASCII kebab-case).
- Gestion atomique de l'invariant `is_active` unique (index partiel + `SELECT FOR UPDATE`).

## Phase 1 — Design & Contracts

- [`data-model.md`](./data-model.md) : entités `GeodataVersion`, `GeodataJob` (in-memory), réutilisation `AuditLog`.
- [`contracts/admin-geodata.openapi.yaml`](./contracts/admin-geodata.openapi.yaml) : endpoints admin.
- [`contracts/public-geography-geojson.openapi.yaml`](./contracts/public-geography-geojson.openapi.yaml) : endpoint public + ETag/304.
- [`quickstart.md`](./quickstart.md) : steps dev local (migration, seed, premier upload, vérification carte).

## Re-evaluation Constitution Check (post-Phase 1)

**Statut gate post-design** : PASS. Le design respecte :
- Fichiers ciblés < 400 lignes (pipeline divisé en fonctions pures < 50 lignes).
- Aucun secret hardcodé (paramètres via `core/config.py`).
- Validation aux frontières (Pydantic + MIME / extension / taille avant pipeline).
- Audit log + rate limit + auth admin sur toutes les opérations sensibles.
- Pas de mutation : pipeline retourne toujours de nouvelles structures.
- Pas de pattern exotique introduit.
