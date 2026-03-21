# Tasks: Interface publique de consultation

**Input**: Design documents from `/specs/008-public-consultation/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/public-api.md, quickstart.md

**Tests**: Non explicitement demandes dans la spec. Pas de taches de tests generees.

**Organization**: Tasks groupees par user story pour permettre l'implementation et le test independant de chaque story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Peut tourner en parallele (fichiers differents, pas de dependances)
- **[Story]**: User story concernee (US1, US2, US3, US4, US5)
- Chemins exacts inclus dans les descriptions

## Path Conventions

- **Backend**: `apps/backend/app/`
- **Frontend**: `apps/frontend/app/`
- **Types partages**: `packages/shared/types/`

---

## Phase 1: Setup

**Purpose**: Ajout de dependances et types partages

- [x] T001 Add python-docx>=1.1.0 dependency in apps/backend/pyproject.toml
- [x] T002 Create shared public API response types in packages/shared/types/public.ts

---

## Phase 2: Foundational (Backend API publique + composable frontend)

**Purpose**: Endpoints publics et infrastructure frontend commune. DOIT etre termine avant toute user story.

- [x] T003 [P] Create public response schemas (PublicCompteResponse, PublicAnneesResponse, PublicDescriptionResponse, hierarchical line structure with sections) in apps/backend/app/schemas/public.py
- [x] T004 [P] Create public service with methods: get_published_compte(db, type, id, annee), get_collectivite_description(db, type, id), get_available_years(db, type, id) — all filter by status="published" — reuse account_service.py compute functions in apps/backend/app/services/public_service.py
- [x] T005 Create public router with endpoints: GET /{type}/{id}/annees, GET /{type}/{id}/description, GET /{type}/{id}/comptes?annee= — prefix /api/public/collectivites, no auth dependency in apps/backend/app/routers/public_comptes.py
- [x] T006 Mount public_comptes_router in FastAPI app (after geography_router, before admin routers) in apps/backend/app/main.py
- [x] T007 [P] Create usePublicComptes composable with methods: fetchAnnees(type, id), fetchDescription(type, id), fetchCompte(type, id, annee), downloadExport(type, id, annee, format) in apps/frontend/app/composables/usePublicComptes.ts
- [x] T008 [P] Modify GeographySelector to accept optional onSubmit prop callback (default: current navigateTo behavior), remove year selector when no years prop passed, so public landing page can use it without year in apps/frontend/app/components/GeographySelector.vue

**Checkpoint**: API publique fonctionnelle, composable frontend pret, GeographySelector adaptable

---

## Phase 3: User Story 1 - Landing Page (Priority: P1) MVP

**Goal**: Page d'accueil publique avec titre, logo TI Madagascar et selecteur geographique redirigeant vers la page de resultats

**Independent Test**: Acceder a http://localhost:3000/, voir le titre et le selecteur, selectionner une commune, verifier la redirection vers /collectivite/commune-{id}

### Implementation for User Story 1

- [x] T009 [US1] Rewrite landing page: replace health check with public landing (title "Plateforme de suivi des revenus miniers des collectivites territoriales", TI Madagascar logo placeholder, GeographySelector with onSubmit navigating to /collectivite/{type}-{id}, dark/light mode, responsive) in apps/frontend/app/pages/index.vue

**Checkpoint**: Landing page fonctionnelle, navigation vers page de resultats operationnelle

---

## Phase 4: User Story 2 - Recettes et Depenses (Priority: P1)

**Goal**: Page de resultats avec description collectivite, selecteur annee, onglets Recettes/Depenses, tableaux hierarchiques depliables a 3 niveaux avec en-tetes de section

**Independent Test**: Acceder a /collectivite/commune-{id}, selectionner une annee, voir le tableau de recettes avec lignes niv1 repliees, deplier pour voir niv2/niv3, passer a l'onglet Depenses avec sous-onglets par programme

### Implementation for User Story 2

- [x] T010 [P] [US2] Create AccountTable component: collapsible rows (3 levels, initially collapsed to niv1 only), section headers ("FONCTIONNEMENT", "INVESTISSEMENT"), niv1 bold with colored background, niv2/niv3 indented, dynamic columns from template, computed values display (totals, rates), horizontal scroll on mobile with scroll indicator, dark/light mode in apps/frontend/app/components/AccountTable.vue
- [x] T011 [US2] Create results page: route param parsing [type]-[id], fetch description + available years on mount, year selector dropdown (default: most recent), 4 tabs (Recettes/Depenses/Recapitulatifs/Equilibre — last 2 empty placeholders), Recettes tab with AccountTable for recettes data, Depenses tab with sub-tabs per programme each containing AccountTable, RichContentRenderer for description, empty state messages, dark/light mode, responsive in apps/frontend/app/pages/collectivite/[type]-[id].vue

**Checkpoint**: Tableaux recettes et depenses consultables avec donnees reelles, navigation complete depuis la landing page

---

## Phase 5: User Story 3 - Recapitulatifs et Equilibre (Priority: P2)

**Goal**: Onglets Recapitulatifs (recap recettes + recap depenses en vue scrollable unique) et Equilibre (recettes vs depenses par section avec excedent/deficit)

**Independent Test**: Acceder aux onglets Recapitulatifs et Equilibre pour Andrafiabe 2023, verifier que les totaux correspondent au document officiel

### Implementation for User Story 3

- [x] T012 [P] [US3] Create RecapTable component: two sections in single scrollable view — recap recettes (categories niv1, sous-totaux par section fonctionnement/investissement, totaux reelles/ordre) then recap depenses (categories en lignes, programmes en colonnes, mandat/paiement/reste a payer), section titles as separators, dark/light mode, responsive horizontal scroll in apps/frontend/app/components/RecapTable.vue
- [x] T013 [P] [US3] Create EquilibreTable component: two-column layout (depenses vs recettes) per section (fonctionnement, investissement), separation operations reelles / operations d'ordre, sous-totaux par type, total par section, resultat definitif (excedent/deficit), dark/light mode, responsive in apps/frontend/app/components/EquilibreTable.vue
- [x] T014 [US3] Integrate RecapTable and EquilibreTable into Recapitulatifs and Equilibre tabs, fetch recap and equilibre data via usePublicComptes, replace placeholder content in apps/frontend/app/pages/collectivite/[type]-[id].vue

**Checkpoint**: Les 4 onglets sont fonctionnels, toutes les vues de consultation disponibles

---

## Phase 6: User Story 4 - Export (Priority: P3)

**Goal**: Boutons Imprimer, Telecharger Excel et Telecharger Word sur la page de resultats

**Independent Test**: Cliquer sur chaque bouton d'export, verifier que l'impression s'ouvre et que les fichiers Excel/Word contiennent les bonnes donnees

### Implementation for User Story 4

- [x] T015 [P] [US4] Create export service: generate_excel(db, compte) with sheets (Recettes, one per programme depenses, Recap Recettes, Recap Depenses, Equilibre) using openpyxl, generate_word(db, compte) with structured document using python-docx, both return BytesIO — reuse account_service.py for data in apps/backend/app/services/export_service.py
- [x] T016 [US4] Add export endpoint GET /{type}/{id}/comptes/{annee}/export?format=xlsx|docx returning StreamingResponse with proper Content-Type and Content-Disposition headers in apps/backend/app/routers/public_comptes.py
- [x] T017 [P] [US4] Add print stylesheet (@media print) hiding navigation, expanding tables, proper page breaks in apps/frontend/app/assets/css/print.css and import in apps/frontend/app/assets/css/main.css
- [x] T018 [US4] Add action buttons bar (Imprimer via window.print, Telecharger Excel, Telecharger Word via usePublicComptes.downloadExport) above tabs in apps/frontend/app/pages/collectivite/[type]-[id].vue

**Checkpoint**: Les 3 modes d'export fonctionnent correctement

---

## Phase 7: User Story 5 - SEO et Partage (Priority: P3)

**Goal**: Meta titres et descriptions dynamiques sur les pages de collectivites pour le referencement et le partage

**Independent Test**: Verifier les balises meta dans le HTML source de la page de resultats, partager l'URL et verifier l'apercu

### Implementation for User Story 5

- [x] T019 [P] [US5] Add dynamic SEO meta tags using useSeoMeta: title "{collectivite_name} - Compte administratif {annee}", description "Consultez les recettes et depenses de {collectivite_name} pour l'exercice {annee}", og:title, og:description in apps/frontend/app/pages/collectivite/[type]-[id].vue
- [x] T020 [P] [US5] Add SEO meta tags to landing page using useSeoMeta: title "Plateforme de suivi des revenus miniers - PCQVP Madagascar", description statique in apps/frontend/app/pages/index.vue

**Checkpoint**: SEO operationnel sur toutes les pages publiques

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Verification transversale de la qualite

- [x] T021 Verify responsive mobile layout (375px) on all public pages: horizontal scroll indicators on tables, touch-friendly tab navigation, GeographySelector usability
- [x] T022 Verify dark/light mode consistency across all new components (AccountTable, RecapTable, EquilibreTable, landing page, results page)
- [x] T023 Run quickstart.md validation scenarios end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Pas de dependances — peut demarrer immediatement
- **Foundational (Phase 2)**: Depend de Phase 1 — BLOQUE toutes les user stories
- **US1 (Phase 3)**: Depend de Phase 2 (T008 GeographySelector, T007 composable)
- **US2 (Phase 4)**: Depend de Phase 2 (T007 composable, T005 router) — peut demarrer en parallele avec US1
- **US3 (Phase 5)**: Depend de US2 (la page de resultats doit exister pour integrer les onglets)
- **US4 (Phase 6)**: Backend (T015, T016) peut demarrer en parallele avec US2/US3. Frontend (T017, T018) depend de US2 (page de resultats)
- **US5 (Phase 7)**: Depend de US1 (landing) et US2 (page resultats) pour ajouter les meta tags
- **Polish (Phase 8)**: Depend de toutes les user stories

### User Story Dependencies

- **US1 (P1)**: Independante apres Phase 2
- **US2 (P1)**: Independante apres Phase 2 (peut etre en parallele avec US1)
- **US3 (P2)**: Depend de US2 (integration dans la page de resultats)
- **US4 (P3)**: Backend independant ; frontend depend de US2
- **US5 (P3)**: Depend de US1 et US2 (pages doivent exister)

### Within Each User Story

- Composants avant pages (models before services, components before pages)
- Backend avant frontend quand applicable
- Integration en dernier

### Parallel Opportunities

- T003 + T004 + T007 + T008 (Phase 2 : schemas, service, composable, selector en parallele)
- T010 (AccountTable) en parallele avec le backend de Phase 2
- T012 + T013 (RecapTable + EquilibreTable en parallele)
- T015 + T017 (export service backend + print stylesheet en parallele)
- T019 + T020 (SEO meta pages en parallele)

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Lancer en parallele (fichiers differents, pas de dependances):
Task T003: "Create public schemas in apps/backend/app/schemas/public.py"
Task T004: "Create public service in apps/backend/app/services/public_service.py"
Task T007: "Create usePublicComptes composable in apps/frontend/app/composables/usePublicComptes.ts"
Task T008: "Modify GeographySelector in apps/frontend/app/components/GeographySelector.vue"

# Puis sequentiel (depend de T003 + T004):
Task T005: "Create public router in apps/backend/app/routers/public_comptes.py"
Task T006: "Mount router in apps/backend/app/main.py"
```

## Parallel Example: User Story 4 (Export)

```bash
# Backend et frontend print en parallele:
Task T015: "Create export service in apps/backend/app/services/export_service.py"
Task T017: "Add print stylesheet in apps/frontend/app/assets/css/print.css"

# Puis sequentiel:
Task T016: "Add export endpoint in apps/backend/app/routers/public_comptes.py"
Task T018: "Add export buttons in apps/frontend/app/pages/collectivite/[type]-[id].vue"
```

---

## Implementation Strategy

### MVP First (US1 + US2 = Landing + Tableaux)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T008)
3. Complete Phase 3: US1 - Landing page (T009)
4. Complete Phase 4: US2 - Recettes & Depenses (T010-T011)
5. **STOP and VALIDATE**: Un visiteur peut naviguer depuis la landing page, selectionner une collectivite, voir les tableaux de recettes et depenses
6. Deploy/demo si pret

### Incremental Delivery

1. Setup + Foundational → Infrastructure prete
2. US1 + US2 → Consultation de base (MVP)
3. US3 → Recapitulatifs et equilibre
4. US4 → Export Excel/Word/impression
5. US5 → SEO et partage
6. Polish → Verification mobile, dark mode, validation

---

## Notes

- Aucune nouvelle table DB — lecture seule des donnees existantes (Features 006/007)
- Reutilisation maximale de account_service.py (calculs) et des composants existants (GeographySelector, RichContentRenderer)
- python-docx est la seule nouvelle dependance
- Les composants AccountTable, RecapTable, EquilibreTable sont en lecture seule (pas d'inputs editables)
- Le GeographySelector sur la landing publique ne montre pas le selecteur d'annee (l'annee est choisie sur la page de resultats)
