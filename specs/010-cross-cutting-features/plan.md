# Implementation Plan: Fonctionnalites transverses

**Branch**: `010-cross-cutting-features` | **Date**: 2026-03-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/010-cross-cutting-features/spec.md`

## Summary

Ajouter 4 fonctionnalites transverses a la plateforme PCQVP : recherche full-text PostgreSQL (tsvector + unaccent + GIN) sur collectivites et comptes, inscription/gestion newsletter avec double opt-in par email, suivi des visites et telechargements avec dashboard admin, et preparation de l'integration GlobalLeaks (lien + page + configuration admin).

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript strict (frontend)
**Primary Dependencies**: FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, Nuxt 4.4+, Tailwind CSS 4 + slowapi (rate limiting), fastapi-mail (emails), itsdangerous (token signing)
**Storage**: PostgreSQL 16+ via asyncpg ; 3 nouvelles tables (newsletter_subscribers, visit_logs, site_configurations) + colonnes search_vector sur tables geography
**Testing**: pytest + pytest-asyncio + httpx (backend)
**Target Platform**: Web (serveur Linux, navigateurs modernes)
**Project Type**: Web application (monorepo backend + frontend)
**Performance Goals**: Recherche < 1s pour 95% des requetes, inscription newsletter < 30s, dashboard admin < 3s
**Constraints**: Rate limiting par IP (30/min recherche, 5/min newsletter), retention visit_logs 12 mois
**Scale/Scope**: ~1800 collectivites (6 provinces, 23 regions, ~1700 communes) + comptes publies

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principe | Statut | Notes |
|----------|--------|-------|
| I. Donnees Ouvertes & Transparence | PASS | La recherche ameliore l'acces aux donnees. Les comptes restent publics. |
| II. Securite & Confidentialite | PASS | Rate limiting sur endpoints publics, validation Pydantic, tokens signes pour newsletter, pas d'exposition de donnees sensibles. |
| III. Simplicite & Maintenabilite | PASS | Utilisation des capacites natives PostgreSQL (FTS), pas de moteur externe. Dependencies minimales (slowapi, fastapi-mail, itsdangerous). Middleware standard Starlette pour le logging. |
| Architecture monorepo | PASS | Pas de nouveau projet, ajout dans apps/backend et apps/frontend existants. |
| Types partages | PASS | Nouveaux types dans packages/shared (search, newsletter, analytics, config). |
| useApi comme point d'entree | PASS | Tous les nouveaux composables utiliseront useApi. |
| Migrations reversibles | PASS | Alembic avec down migration (drop tables, drop extensions). |

**Post-Phase 1 re-check**: PASS - Le data model est simple (3 tables standalone + colonnes generees). Pas d'abstraction prematuree. Les contracts API suivent les patterns existants.

## Project Structure

### Documentation (this feature)

```text
specs/010-cross-cutting-features/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: research findings
├── data-model.md        # Phase 1: data model design
├── quickstart.md        # Phase 1: setup guide
├── contracts/
│   └── api-endpoints.md # Phase 1: API contracts
└── tasks.md             # Phase 2: task breakdown (via /speckit.tasks)
```

### Source Code (repository root)

```text
apps/backend/
├── app/
│   ├── core/
│   │   ├── config.py            # + MAIL_*, FRONTEND_URL settings
│   │   └── rate_limit.py        # NEW: slowapi limiter setup
│   ├── models/
│   │   ├── geography.py         # + search_vector columns
│   │   ├── newsletter.py        # NEW: NewsletterSubscriber
│   │   ├── visit_log.py         # NEW: VisitLog
│   │   └── site_config.py       # NEW: SiteConfiguration
│   ├── schemas/
│   │   ├── search.py            # NEW: SearchResponse
│   │   ├── newsletter.py        # NEW: SubscribeRequest, SubscriberResponse
│   │   ├── analytics.py         # NEW: DashboardResponse
│   │   └── site_config.py       # NEW: ConfigResponse
│   ├── routers/
│   │   ├── search.py            # NEW: GET /api/search
│   │   ├── newsletter.py        # NEW: POST subscribe, GET confirm/unsubscribe
│   │   ├── admin_newsletter.py  # NEW: GET/DELETE subscribers, GET export
│   │   ├── admin_analytics.py   # NEW: GET dashboard, DELETE purge
│   │   └── admin_config.py      # NEW: GET/PUT config
│   ├── services/
│   │   ├── search_service.py    # NEW: full-text search logic
│   │   ├── newsletter_service.py # NEW: subscribe/confirm/unsubscribe
│   │   ├── analytics_service.py # NEW: dashboard aggregation, purge
│   │   └── config_service.py    # NEW: site config CRUD
│   ├── middleware/
│   │   └── visit_tracker.py     # NEW: visit logging middleware
│   └── main.py                  # + mount new routers, middleware
├── alembic/
│   └── versions/
│       └── xxx_add_cross_cutting.py  # NEW: migration

apps/frontend/
├── app/
│   ├── components/
│   │   ├── SearchBar.vue              # NEW: dropdown autocomplete
│   │   ├── NewsletterForm.vue         # NEW: email subscription form
│   │   └── admin/
│   │       ├── AnalyticsDashboard.vue # NEW: charts + stats
│   │       └── SubscribersList.vue    # NEW: admin subscriber list
│   ├── composables/
│   │   ├── useSearch.ts               # NEW: search API calls
│   │   ├── useNewsletter.ts           # NEW: subscribe API
│   │   ├── useAnalytics.ts            # NEW: dashboard API
│   │   └── useSiteConfig.ts           # NEW: config API
│   ├── pages/
│   │   ├── signaler.vue               # NEW: GlobalLeaks info page
│   │   ├── newsletter/
│   │   │   ├── confirmed.vue          # NEW: confirmation success
│   │   │   └── unsubscribed.vue       # NEW: unsubscribe success
│   │   └── admin/
│   │       ├── newsletter.vue         # NEW: subscriber management
│   │       ├── analytics.vue          # NEW: visit dashboard
│   │       └── config.vue             # NEW: site configuration
│   └── layouts/
│       └── default.vue                # + SearchBar in header, NewsletterForm in footer

packages/shared/
├── types/
│   ├── search.ts                      # NEW: SearchResult types
│   ├── newsletter.ts                  # NEW: Subscriber types
│   ├── analytics.ts                   # NEW: Dashboard types
│   └── config.ts                      # NEW: SiteConfig types
```

**Structure Decision**: Extension du monorepo existant avec les memes patterns (routers/services/schemas cote backend, composables/pages/components cote frontend, types partages dans packages/shared).

## Complexity Tracking

Aucune violation de la constitution detectee. Pas de justification necessaire.
