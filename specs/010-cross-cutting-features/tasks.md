# Tasks: Fonctionnalites transverses

**Input**: Design documents from `/specs/010-cross-cutting-features/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api-endpoints.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Installer les nouvelles dependances et preparer la configuration

- [x] T001 Ajouter slowapi>=0.1.9, fastapi-mail>=1.4.0, itsdangerous>=2.1.0 dans apps/backend/pyproject.toml et installer
- [x] T002 [P] Ajouter les variables MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_SERVER, MAIL_PORT, FRONTEND_URL dans apps/backend/app/core/config.py (classe Settings)
- [x] T003 [P] Creer le module rate limiting avec slowapi dans apps/backend/app/core/rate_limit.py (limiter instance + handler d'exception)
- [x] T004 [P] Creer les types partages dans packages/shared/types/search.ts (SearchResult, SearchResponse)
- [x] T005 [P] Creer les types partages dans packages/shared/types/newsletter.ts (SubscribeRequest, SubscriberResponse, PaginatedSubscribers)
- [x] T006 [P] Creer les types partages dans packages/shared/types/analytics.ts (DashboardResponse, VisitStats, DownloadStats)
- [x] T007 [P] Creer les types partages dans packages/shared/types/config.ts (SiteConfigResponse)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Migration DB et modeles communs - BLOQUE toutes les user stories

- [x] T008 Creer la migration Alembic : extension unaccent, config fr_unaccent, tables newsletter_subscribers + visit_logs + site_configurations, colonnes search_vector sur provinces/regions/communes avec index GIN, seed globalleaks_url dans site_configurations - dans apps/backend/alembic/versions/
- [x] T009 [P] Creer le modele NewsletterSubscriber dans apps/backend/app/models/newsletter.py (UUIDBase, email unique, status enum, unsubscribe_token, confirmed_at, unsubscribed_at)
- [x] T010 [P] Creer le modele VisitLog dans apps/backend/app/models/visit_log.py (UUIDBase, event_type enum, path, page_type, collectivite_type, collectivite_id, download_format, user_agent, ip_address, index sur created_at/event_type/page_type)
- [x] T011 [P] Creer le modele SiteConfiguration dans apps/backend/app/models/site_config.py (UUIDBase, key unique, value text, updated_at)
- [x] T012 Ajouter les colonnes search_vector (TSVector Computed + GIN index) sur Province, Region, Commune dans apps/backend/app/models/geography.py
- [x] T013 Enregistrer le rate limiter slowapi et le handler d'exception dans apps/backend/app/main.py (app.state.limiter + exception handler)

**Checkpoint**: Base de donnees migree, modeles prets, rate limiter actif

---

## Phase 3: User Story 1 - Recherche full-text (Priority: P1) MVP

**Goal**: Un visiteur peut rechercher des collectivites et comptes via un champ de recherche autocomplete dans le header

**Independent Test**: Saisir "Antananarivo" dans le champ de recherche et verifier que les collectivites correspondantes apparaissent en dropdown, triees par pertinence

### Implementation for User Story 1

- [x] T014 [P] [US1] Creer les schemas Pydantic de recherche dans apps/backend/app/schemas/search.py (SearchQuery, SearchResultItem, SearchResponse avec groupes collectivites/comptes)
- [x] T015 [US1] Implementer le service de recherche full-text dans apps/backend/app/services/search_service.py (requete tsvector sur provinces/regions/communes + jointure comptes_administratifs publies sur commune name + annee_exercice, regroupement par type, tri par pertinence ts_rank)
- [x] T016 [US1] Creer le router GET /api/search dans apps/backend/app/routers/search.py (params q + limit, rate limit 30/min, validation min 2 chars)
- [x] T017 [US1] Monter le router search dans apps/backend/app/main.py
- [x] T018 [P] [US1] Creer le composable useSearch dans apps/frontend/app/composables/useSearch.ts (appel GET /api/search avec debounce)
- [x] T019 [US1] Creer le composant SearchBar.vue dans apps/frontend/app/components/SearchBar.vue (input avec debounce 300ms, dropdown resultats groupes par type max 8-10, lien "voir tous les resultats" pointant vers /recherche?q=..., etat vide/chargement/aucun resultat, dark mode)
- [x] T020 [US1] Creer le layout par defaut dans apps/frontend/app/layouts/default.vue (header avec SearchBar, footer avec NewsletterForm placeholder, slot principal) et y integrer SearchBar dans le header
- [x] T021 [US1] Creer la page de resultats complets dans apps/frontend/app/pages/recherche.vue (resultats pagines groupes par type, query param q, dark mode, layout default)
- [x] T022 [US1] Ecrire les tests pytest pour le service de recherche dans apps/backend/tests/test_search.py (recherche par nom collectivite, recherche compte par commune+annee, recherche accent-insensible, recherche sans resultats, recherche caracteres speciaux)

**Checkpoint**: La recherche full-text fonctionne de bout en bout (backend + frontend)

---

## Phase 4: User Story 2 - Inscription newsletter (Priority: P2)

**Goal**: Un visiteur peut s'inscrire a la newsletter avec double opt-in par email et se desinscrire via un lien

**Independent Test**: Soumettre un email dans le formulaire newsletter, verifier l'inscription en DB et l'envoi de l'email de confirmation, confirmer via le lien, puis se desinscrire

### Implementation for User Story 2

- [x] T023 [P] [US2] Creer les schemas Pydantic newsletter dans apps/backend/app/schemas/newsletter.py (SubscribeRequest, SubscribeResponse, ConfirmResponse)
- [x] T024 [US2] Implementer le service newsletter dans apps/backend/app/services/newsletter_service.py (subscribe avec generation token itsdangerous, confirm avec verification token, unsubscribe, reactivation si desinscrit, envoi email via fastapi-mail + BackgroundTasks)
- [x] T025 [US2] Creer le router newsletter public dans apps/backend/app/routers/newsletter.py (POST /api/newsletter/subscribe rate limit 5/min, GET /api/newsletter/confirm?token=, GET /api/newsletter/unsubscribe?token= avec redirections vers frontend)
- [x] T026 [US2] Monter le router newsletter dans apps/backend/app/main.py
- [x] T027 [P] [US2] Creer le composable useNewsletter dans apps/frontend/app/composables/useNewsletter.ts (appel POST subscribe)
- [x] T028 [US2] Creer le composant NewsletterForm.vue dans apps/frontend/app/components/NewsletterForm.vue (input email + bouton, validation, message succes/erreur/doublon, dark mode)
- [x] T029 [US2] Integrer NewsletterForm dans le footer du layout par defaut dans apps/frontend/app/layouts/default.vue (remplacer le placeholder ajoute en T020)
- [x] T030 [P] [US2] Creer la page de confirmation newsletter dans apps/frontend/app/pages/newsletter/confirmed.vue (message de succes, dark mode)
- [x] T031 [P] [US2] Creer la page de desinscription newsletter dans apps/frontend/app/pages/newsletter/unsubscribed.vue (message de confirmation, dark mode)
- [x] T032 [US2] Ecrire les tests pytest pour le service newsletter dans apps/backend/tests/test_newsletter.py (inscription, double opt-in confirmation, desinscription, reinscription apres desinscription, doublon email, email invalide)

**Checkpoint**: Le cycle complet inscription → confirmation → desinscription fonctionne

---

## Phase 5: User Story 3 - Gestion admin newsletter (Priority: P3)

**Goal**: Un administrateur peut consulter, rechercher, exporter et supprimer les abonnes newsletter

**Independent Test**: Se connecter en admin, acceder a la page newsletter, verifier la liste paginee, exporter en CSV, supprimer un abonne

### Implementation for User Story 3

- [x] T033 [US3] Implementer le service admin newsletter dans apps/backend/app/services/newsletter_service.py (list_subscribers pagine avec filtres status/search, export_csv, delete_subscriber) - ajout de fonctions au service existant
- [x] T034 [US3] Creer le router admin newsletter dans apps/backend/app/routers/admin_newsletter.py (GET /api/admin/newsletter/subscribers pagine, GET /api/admin/newsletter/export CSV, DELETE /api/admin/newsletter/subscribers/{id}, authentification admin requise)
- [x] T035 [US3] Monter le router admin_newsletter dans apps/backend/app/main.py
- [x] T036 [P] [US3] Creer le composable useAdminNewsletter dans apps/frontend/app/composables/useNewsletter.ts (list, export, delete - ajout au composable existant)
- [x] T037 [US3] Creer la page admin newsletter dans apps/frontend/app/pages/admin/newsletter.vue (tableau pagine avec colonnes email/status/date, filtres, boutons export CSV et suppression avec confirmation, dark mode, layout admin + middleware auth)
- [x] T038 [US3] Ajouter le lien Newsletter dans la sidebar admin dans apps/frontend/app/layouts/admin.vue

**Checkpoint**: L'admin peut gerer completement les abonnes newsletter

---

## Phase 6: User Story 4 - Suivi visites et telechargements (Priority: P3)

**Goal**: Les visites et telechargements sont enregistres automatiquement, un dashboard admin affiche les statistiques avec filtrage par periode et purge manuelle

**Independent Test**: Naviguer sur le site public, telecharger un export, puis verifier que le dashboard admin affiche les statistiques correspondantes

### Implementation for User Story 4

- [x] T039 [P] [US4] Creer les schemas Pydantic analytics dans apps/backend/app/schemas/analytics.py (DashboardResponse, VisitStats, DownloadStats, TrendItem, PurgeResponse, DataRetentionInfo)
- [x] T040 [US4] Creer le middleware de suivi des visites dans apps/backend/app/middleware/visit_tracker.py (middleware HTTP filtrant routes publiques, excluant bots par User-Agent, enregistrant via response.background BackgroundTask, creation session DB autonome)
- [x] T041 [US4] Implementer le service analytics dans apps/backend/app/services/analytics_service.py (get_dashboard avec aggregations par page_type/format/periode, get_retention_info retournant purge_eligible=true si donnees > 12 mois, purge_old_records pour suppression > 12 mois)
- [x] T042 [US4] Creer le router admin analytics dans apps/backend/app/routers/admin_analytics.py (GET /api/admin/analytics/dashboard?period=7d|30d|12m, DELETE /api/admin/analytics/purge, authentification admin requise)
- [x] T043 [US4] Monter le middleware visit_tracker et le router admin_analytics dans apps/backend/app/main.py
- [x] T044 [P] [US4] Creer le composable useAnalytics dans apps/frontend/app/composables/useAnalytics.ts (appel GET dashboard, DELETE purge)
- [x] T045 [US4] Creer la page admin analytics dans apps/frontend/app/pages/admin/analytics.vue (statistiques visites par type de page, telechargements par format, tendances sur la periode selectionnee, banniere d'alerte si data_retention.purge_eligible=true avec bouton purge et confirmation, dark mode, layout admin + middleware auth)
- [x] T046 [US4] Ajouter le lien Analytics dans la sidebar admin dans apps/frontend/app/layouts/admin.vue
- [x] T047 [US4] Ecrire les tests pytest pour le service analytics dans apps/backend/tests/test_analytics.py (aggregation par periode, filtrage bots, purge donnees > 12 mois, retention info)

**Checkpoint**: Le suivi automatique et le dashboard admin fonctionnent de bout en bout

---

## Phase 7: User Story 5 - Integration GlobalLeaks (Priority: P4)

**Goal**: Un visiteur peut acceder a GlobalLeaks via un lien dans la navigation et une page dediee, l'admin peut configurer l'URL

**Independent Test**: Cliquer sur le lien "Signaler" dans la navigation, verifier la page d'information, cliquer sur le bouton GlobalLeaks, verifier la redirection. En admin, modifier l'URL et verifier que le lien public est mis a jour.

### Implementation for User Story 5

- [x] T048 [P] [US5] Creer les schemas Pydantic config dans apps/backend/app/schemas/site_config.py (ConfigResponse, ConfigUpdateRequest)
- [x] T049 [US5] Implementer le service config dans apps/backend/app/services/config_service.py (get_config, update_config, get_public_globalleaks_url)
- [x] T050 [US5] Creer le router admin config dans apps/backend/app/routers/admin_config.py (GET/PUT /api/admin/config/{key}, authentification admin requise)
- [x] T051 [P] [US5] Creer le router public config dans apps/backend/app/routers/public_config.py (GET /api/public/config/globalleaks, sans authentification)
- [x] T052 [US5] Monter les routers admin_config et public_config dans apps/backend/app/main.py
- [x] T053 [P] [US5] Creer le composable useSiteConfig dans apps/frontend/app/composables/useSiteConfig.ts (get/update config, get public globalleaks URL)
- [x] T054 [US5] Creer la page publique "Signaler" dans apps/frontend/app/pages/signaler.vue (explication du processus de signalement anonyme, bouton redirection vers GlobalLeaks en nouvel onglet, URL chargee dynamiquement via API, dark mode)
- [x] T055 [US5] Ajouter le lien "Signaler" dans la navigation et/ou le footer du layout par defaut dans apps/frontend/app/layouts/default.vue
- [x] T056 [US5] Creer la page admin configuration dans apps/frontend/app/pages/admin/config.vue (formulaire edition URL GlobalLeaks, dark mode, layout admin + middleware auth)
- [x] T057 [US5] Ajouter le lien Configuration dans la sidebar admin dans apps/frontend/app/layouts/admin.vue

**Checkpoint**: L'integration GlobalLeaks est operationnelle (lien public + config admin)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Ameliorations transverses affectant plusieurs user stories

- [x] T058 Verifier que tous les nouveaux composants frontend supportent le dark mode (classes dark: sur tous les elements interactifs et conteneurs)
- [x] T059 Ajouter les re-exports des types partages dans apps/frontend/app/types/ (search.ts, newsletter.ts, analytics.ts, config.ts)
- [x] T060 Verifier la sanitisation des entrees utilisateur sur tous les endpoints publics (recherche, inscription newsletter) contre les injections
- [x] T061 Executer ruff check sur tous les nouveaux fichiers Python dans apps/backend/
- [ ] T062 Executer ESLint sur tous les nouveaux fichiers TypeScript/Vue dans apps/frontend/
- [x] T063 Validation de bout en bout selon quickstart.md : recherche, inscription newsletter, dashboard analytics, lien GlobalLeaks

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Aucune dependance - demarrage immediat
- **Foundational (Phase 2)**: Depend de Phase 1 (deps installees) - BLOQUE toutes les user stories
- **US1 Recherche (Phase 3)**: Depend de Phase 2 (search_vector sur geography) - MVP
- **US2 Newsletter inscription (Phase 4)**: Depend de Phase 2 (table newsletter_subscribers)
- **US3 Admin newsletter (Phase 5)**: Depend de Phase 4 (US2 doit exister pour avoir des abonnes a gerer)
- **US4 Suivi visites (Phase 6)**: Depend de Phase 2 (table visit_logs) - independant des US1/US2/US3
- **US5 GlobalLeaks (Phase 7)**: Depend de Phase 2 (table site_configurations) - independant des US1/US2/US3/US4
- **Polish (Phase 8)**: Depend de toutes les phases precedentes

### User Story Dependencies

- **US1 (P1)**: Independant - peut demarrer des Phase 2 terminee
- **US2 (P2)**: Independant - peut demarrer des Phase 2 terminee
- **US3 (P3)**: Depend de US2 (necessite le modele et le service newsletter)
- **US4 (P3)**: Independant - peut demarrer des Phase 2 terminee
- **US5 (P4)**: Independant - peut demarrer des Phase 2 terminee

### Within Each User Story

- Schemas Pydantic avant services
- Services avant routers
- Routers avant montage dans main.py
- Composables frontend avant composants/pages
- Composants avant integration dans layouts

### Parallel Opportunities

- Phase 1: T002-T007 en parallele (fichiers differents)
- Phase 2: T009-T011 en parallele (modeles independants)
- Phase 3+: US1, US2, US4, US5 peuvent etre developpes en parallele (US3 attend US2)
- Dans chaque US: schemas + composables frontend en parallele (backend/frontend differents)

---

## Parallel Example: User Story 1

```bash
# Backend schemas + Frontend composable en parallele :
Task: T014 "Creer schemas Pydantic recherche dans apps/backend/app/schemas/search.py"
Task: T018 "Creer composable useSearch dans apps/frontend/app/composables/useSearch.ts"

# Puis sequentiellement :
Task: T015 "Service recherche full-text" (depend de T014)
Task: T016 "Router GET /api/search" (depend de T015)
Task: T019 "Composant SearchBar.vue" (depend de T018)
Task: T020 "Creation layout default + integration SearchBar" (depend de T019)
Task: T021 "Page resultats complets /recherche" (depend de T018)
Task: T022 "Tests pytest search" (depend de T015)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (migration + modeles)
3. Complete Phase 3: US1 Recherche full-text
4. **STOP and VALIDATE**: Tester la recherche de bout en bout
5. Deployer/demo si pret

### Incremental Delivery

1. Setup + Foundational → Infrastructure prete
2. US1 Recherche → Tester → Deploy (MVP!)
3. US2 Newsletter inscription → Tester → Deploy
4. US3 Admin newsletter → Tester → Deploy
5. US4 Suivi visites → Tester → Deploy
6. US5 GlobalLeaks → Tester → Deploy
7. Polish → Validation finale

### Parallel Team Strategy

Avec plusieurs developpeurs apres Phase 2 :
- Dev A : US1 (Recherche) + US3 (Admin newsletter apres US2)
- Dev B : US2 (Newsletter inscription) puis US5 (GlobalLeaks)
- Dev C : US4 (Suivi visites)

---

## Notes

- [P] tasks = fichiers differents, pas de dependances
- [Story] label = tracabilite vers la user story source
- Chaque user story est independamment completable et testable (sauf US3 qui depend de US2)
- Commiter apres chaque tache ou groupe logique
- S'arreter a tout checkpoint pour valider la story independamment
