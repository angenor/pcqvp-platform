# Tasks: Gestion de la hierarchie geographique

**Input**: Design documents from `/specs/005-geography-hierarchy/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api.md

**Tests**: Non explicitement demandes dans la spec. Un fichier de tests backend est inclus en phase Polish.

**Organization**: Tasks groupees par user story pour permettre l'implementation et le test independants de chaque story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Peut tourner en parallele (fichiers differents, pas de dependances)
- **[Story]**: User story associee (US1, US2, US3, US4)
- Chemins exacts inclus dans les descriptions

## Path Conventions

- **Backend**: `apps/backend/app/`
- **Frontend**: `apps/frontend/app/`
- **Shared**: `packages/shared/types/`
- **Migrations**: `apps/backend/alembic/versions/`

---

## Phase 1: Setup (Infrastructure partagee)

**Purpose**: Types partages et configuration initiale

- [x] T001 Create shared geography types in packages/shared/types/geography.ts (RichContentBlock, ProvinceListItem, ProvinceDetail, RegionListItem, RegionDetail, CommuneListItem, CommuneDetail, PaginatedResponse, Hierarchy types - see contracts/api.md)
- [x] T002 [P] Create frontend geography types re-exporting shared types in apps/frontend/app/types/geography.ts

---

## Phase 2: Foundational (Prerequisites bloquants)

**Purpose**: Modeles, migration, schemas et service communs a TOUTES les user stories

**CRITICAL**: Aucune user story ne peut demarrer avant completion de cette phase

- [x] T003 Create Province, Region, Commune models in apps/backend/app/models/geography.py (inherit UUIDBase, add updated_at field, JSONB description_json, FK with ON DELETE RESTRICT, unique code constraints, indexes on province_id and region_id - see data-model.md)
- [x] T004 Export geography models in apps/backend/app/models/__init__.py (add Province, Region, Commune imports)
- [x] T005 Create Alembic migration in apps/backend/alembic/versions/002_create_geography_tables.py (create provinces, regions, communes tables in order; downgrade drops in reverse order - see data-model.md)
- [x] T006 [P] Create Pydantic schemas in apps/backend/app/schemas/geography.py (RichContentBlock discriminated union, ProvinceCreate/Update/List/Detail, RegionCreate/Update/List/Detail, CommuneCreate/Update/List/Detail, PaginatedResponse generic, HierarchyProvince/Region/Commune - see contracts/api.md)
- [x] T007 Create geography service in apps/backend/app/services/geography.py (CRUD functions for Province/Region/Commune: create, get_by_id, list with optional filter+search+pagination, update, delete with child count check returning 409 if children exist, get_hierarchy for full tree - see contracts/api.md and research.md R5)
- [x] T008 [P] Create useGeography composable in apps/frontend/app/composables/useGeography.ts (wrap useApi for: fetchProvinces, fetchRegions(province_id?), fetchCommunes(region_id?), fetchProvinceDetail, fetchRegionDetail, fetchCommuneDetail, fetchHierarchy, admin CRUD: createProvince, updateProvince, deleteProvince, and same for regions/communes, admin paginated lists: fetchAdminProvinces, fetchAdminRegions, fetchAdminCommunes)

**Checkpoint**: Foundation prete - l'implementation des user stories peut commencer

---

## Phase 3: User Story 1 - Naviguer dans la hierarchie geographique (Priority: P1) MVP

**Goal**: Un visiteur peut selectionner une collectivite via un selecteur a 4 niveaux chaines (Province* > Region* > Commune > Annee*) et etre redirige vers la page correspondante

**Independent Test**: Charger la page d'accueil, selectionner Province + Region + Annee, cliquer OK → redirection vers la page de la region. Recommencer avec Province + Region + Commune + Annee → redirection vers la page de la commune.

### Implementation for User Story 1

- [x] T009 [US1] Create public geography router in apps/backend/app/routers/geography.py (GET /api/provinces, GET /api/provinces/{id}, GET /api/regions with optional province_id query param, GET /api/regions/{id}, GET /api/communes with optional region_id query param, GET /api/communes/{id}, GET /api/geography/hierarchy - all public, no auth required - see contracts/api.md)
- [x] T010 [US1] Register public geography router in apps/backend/app/main.py (add router include with prefix)
- [x] T011 [P] [US1] Create GeographySelector.vue in apps/frontend/app/components/GeographySelector.vue (4 chained selects: Province* > Region* > Commune (optional) > Annee* (obligatoire). Province and Region and Annee marked with red asterisk. Commune has no asterisk. On Province change → reset Region/Commune/Annee. On Region change → reset Commune. OK button disabled until Province + Region + Annee filled. OK redirects to /regions/{id}/annee/{year} or /communes/{id}/annee/{year}. Annee select accepts years prop with fallback to disabled state. Use useography composable. Dark/light mode with dark: classes. See spec.md US1 acceptance scenarios)
- [x] T012 [US1] Integrate GeographySelector in apps/frontend/app/pages/index.vue (replace or add to existing content, centered on page, dark/light mode compatible)

**Checkpoint**: US1 fonctionnelle et testable independamment - le selecteur fonctionne sur la page d'accueil

---

## Phase 4: User Story 2 - Gerer les provinces, regions et communes (Priority: P2)

**Goal**: Un admin/editeur peut creer, modifier et supprimer des entites geographiques via l'interface d'administration avec listes paginees et recherche

**Independent Test**: Se connecter en admin, creer une province avec nom+code, creer une region rattachee, creer une commune rattachee. Verifier qu'elles apparaissent dans les listes. Tenter de supprimer la province → message d'erreur (contient des regions).

### Implementation for User Story 2

- [x] T013 [US2] Create admin geography router in apps/backend/app/routers/admin_geography.py (POST/PUT/DELETE /api/admin/provinces, regions, communes + GET paginated lists /api/admin/provinces, regions, communes with search+skip+limit params. All protected with require_role("admin", "editor"). Return 409 on duplicate code or delete with children. Return PaginatedResponse with items+total - see contracts/api.md)
- [x] T014 [US2] Register admin geography router in apps/backend/app/main.py (add router include with prefix, after public router)
- [x] T015 [US2] Add geography navigation section to apps/frontend/app/layouts/admin.vue (add "Geographie" section in sidebar with links to provinces, regions, communes lists. Dark/light mode compatible)
- [x] T016 [P] [US2] Create provinces list page in apps/frontend/app/pages/admin/geography/provinces/index.vue (layout: admin, middleware: auth. Table with name/code/actions columns. Search input field. Pagination controls (20/page). Create button linking to new province form. Edit/Delete action buttons. Delete confirmation dialog with referential integrity error handling. Dark/light mode with dark: classes)
- [x] T017 [P] [US2] Create regions list page in apps/frontend/app/pages/admin/geography/regions/index.vue (same as provinces list + province filter dropdown. Dark/light mode)
- [x] T018 [P] [US2] Create communes list page in apps/frontend/app/pages/admin/geography/communes/index.vue (same as regions list + region filter dropdown. Dark/light mode)
- [x] T019 [P] [US2] Create province edit/create page in apps/frontend/app/pages/admin/geography/provinces/[id].vue (layout: admin, middleware: auth. Form with name, code fields. JSON textarea for description_json as placeholder for rich editor. Save/Cancel buttons. Load existing data if editing. Handle 409 duplicate code error. Dark/light mode. Route param "id" = "new" for creation)
- [x] T020 [P] [US2] Create region edit/create page in apps/frontend/app/pages/admin/geography/regions/[id].vue (same as province + province_id select dropdown. Dark/light mode)
- [x] T021 [P] [US2] Create commune edit/create page in apps/frontend/app/pages/admin/geography/communes/[id].vue (same as region + region_id select dropdown filtered by province. Dark/light mode)

**Checkpoint**: US2 fonctionnelle - admin peut gerer toutes les entites geographiques

---

## Phase 5: User Story 3 - Consulter les details d'une collectivite (Priority: P3)

**Goal**: Un visiteur peut consulter les informations detaillees d'une province, region ou commune (description riche + liste des sous-divisions)

**Independent Test**: Acceder directement a l'URL d'une province → voir nom, code, description riche rendue, liste des regions. Acceder a une region → voir communes. Acceder a une commune → voir description riche avec images.

### Implementation for User Story 3

- [x] T022 [P] [US3] Create RichContentRenderer.vue in apps/frontend/app/components/RichContentRenderer.vue (receives description_json array prop. Renders blocks in order: heading → h2 tag, paragraph → p tag, image → img tag with alt and error placeholder for broken URLs. Dark/light mode compatible)
- [x] T023 [P] [US3] Create province detail page in apps/frontend/app/pages/provinces/[id].vue (public page, no auth. Display name, code, rendered description_json via RichContentRenderer, list of regions with links. 404 handling if province not found. Dark/light mode)
- [x] T024 [P] [US3] Create region detail page in apps/frontend/app/pages/regions/[id].vue (same pattern as province detail. Display communes list. Breadcrumb to parent province. Dark/light mode)
- [x] T025 [P] [US3] Create commune detail page in apps/frontend/app/pages/communes/[id].vue (same pattern. Breadcrumb to parent region and province. Dark/light mode)

**Checkpoint**: US3 fonctionnelle - les pages publiques de detail affichent le contenu riche correctement

---

## Phase 6: User Story 4 - Editer du contenu riche pour les descriptions (Priority: P4)

**Goal**: Un admin/editeur utilise un editeur visuel de blocs pour composer les descriptions (titres, paragraphes, images) avec reordonnement

**Independent Test**: Ouvrir l'edition d'une entite, ajouter un titre, un paragraphe et une image. Reordonner les blocs. Sauvegarder et verifier que le contenu est correctement restitue sur la page publique via RichContentRenderer.

### Implementation for User Story 4

- [x] T026 [US4] Create RichContentEditor.vue in apps/frontend/app/components/RichContentEditor.vue (v-model binding to description_json array. Buttons to add heading/paragraph/image block. Each block renders inline editable fields: heading → text input, paragraph → textarea, image → URL input + preview with broken image placeholder. Drag handle or up/down buttons for reordering blocks. Delete button per block. Dark/light mode with dark: classes. See spec.md US4 acceptance scenarios)
- [x] T027 [US4] Replace JSON textarea with RichContentEditor in apps/frontend/app/pages/admin/geography/provinces/[id].vue, apps/frontend/app/pages/admin/geography/regions/[id].vue, and apps/frontend/app/pages/admin/geography/communes/[id].vue (replace description_json textarea with <RichContentEditor v-model="form.description_json" />)

**Checkpoint**: US4 fonctionnelle - l'editeur de contenu riche remplace le textarea brut

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verification globale et corrections transversales

- [x] T028 Dark mode audit on all new pages and components (verify every element has appropriate dark: classes in GeographySelector.vue, RichContentEditor.vue, RichContentRenderer.vue, all admin list pages, all admin edit pages, all public detail pages, updated index.vue, updated admin.vue)
- [x] T029 Edge case handling verification (empty states: no provinces → informative message in selector, no regions for province → disabled region select with message, no annees → disabled annee select. 404 pages for nonexistent entities. Referential integrity: delete blocked with child count in error message. Duplicate code: 409 with explicit message. Broken image URLs: placeholder in RichContentRenderer)
- [x] T030 Create backend tests in apps/backend/tests/test_geography.py (test CRUD operations for Province/Region/Commune, test referential integrity blocking on delete, test unique code constraint, test pagination and search, test hierarchy endpoint, test admin auth requirement on protected routes)
- [x] T031 Run quickstart.md validation (follow quickstart.md steps end-to-end to verify setup works)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (shared types) - BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 - MVP target
- **US2 (Phase 4)**: Depends on Phase 2 - can run in parallel with US1
- **US3 (Phase 5)**: Depends on Phase 2 - can run in parallel with US1/US2
- **US4 (Phase 6)**: Depends on US2 (edit pages must exist to integrate the editor)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Phase 2 only → fully independent
- **US2 (P2)**: Phase 2 only → fully independent (can parallel with US1)
- **US3 (P3)**: Phase 2 only → fully independent (can parallel with US1/US2)
- **US4 (P4)**: US2 required (modifies edit pages created in US2)

### Within Each User Story

- Backend routes before frontend pages (API must exist)
- Models → Schemas → Service → Routes (backend chain in Phase 2)
- Composable available from Phase 2 for all frontend tasks
- [P] tasks within a story can run in parallel

### Parallel Opportunities

**Phase 2 parallels**:
- T006 (schemas) || T008 (composable) - different stacks
- T003→T004→T005 sequential (model → export → migration)
- T007 after T003+T006

**Cross-story parallels** (after Phase 2):
- US1 (T009-T012) || US2 (T013-T021) || US3 (T022-T025)
- Within US2: T016 || T017 || T018 (list pages) and T019 || T020 || T021 (edit pages)
- Within US3: T022 || T023 || T024 || T025 (all independent files)

---

## Parallel Example: User Story 2

```bash
# After T013-T015 (admin router + main.py + layout):

# Launch all list pages in parallel:
Task: "Create provinces list page in apps/frontend/app/pages/admin/geography/provinces/index.vue"
Task: "Create regions list page in apps/frontend/app/pages/admin/geography/regions/index.vue"
Task: "Create communes list page in apps/frontend/app/pages/admin/geography/communes/index.vue"

# Then launch all edit pages in parallel:
Task: "Create province edit page in apps/frontend/app/pages/admin/geography/provinces/[id].vue"
Task: "Create region edit page in apps/frontend/app/pages/admin/geography/regions/[id].vue"
Task: "Create commune edit page in apps/frontend/app/pages/admin/geography/communes/[id].vue"
```

## Parallel Example: Cross-Story

```bash
# After Phase 2 Foundational completes:

# Launch US1, US2, US3 backend tasks in parallel:
Task: T009 "Create public geography router"
Task: T013 "Create admin geography router"

# Then launch all frontend tasks in parallel:
Task: T011 "Create GeographySelector.vue"
Task: T016 "Create provinces list page"
Task: T022 "Create RichContentRenderer.vue"
Task: T023 "Create province detail page"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (types partages)
2. Complete Phase 2: Foundational (modeles, migration, schemas, service, composable)
3. Complete Phase 3: US1 (selecteur public sur page d'accueil)
4. **STOP and VALIDATE**: Tester le selecteur avec des donnees inserees manuellement en base
5. Deploy/demo si pret

### Incremental Delivery

1. Setup + Foundational → Foundation prete
2. US1 (selecteur) → Tester → Deploy (MVP!)
3. US2 (admin CRUD) → Tester → Deploy (les admins peuvent gerer les donnees)
4. US3 (pages detail) → Tester → Deploy (les visiteurs voient le contenu riche)
5. US4 (editeur riche) → Tester → Deploy (experience d'edition amelioree)
6. Polish → Tests, dark mode, edge cases → Deploy final

### Parallel Team Strategy

Avec plusieurs developpeurs :

1. Equipe complete Setup + Foundational ensemble
2. Une fois Phase 2 terminee :
   - Dev A : US1 (selecteur public) + US3 (pages detail)
   - Dev B : US2 (admin CRUD) puis US4 (editeur riche)
3. Polish en equipe

---

## Notes

- [P] tasks = fichiers differents, pas de dependances
- [Story] label mappe chaque tache a sa user story pour tracabilite
- Chaque user story est independamment completable et testable (sauf US4 qui depend de US2)
- Committer apres chaque tache ou groupe logique
- S'arreter a tout checkpoint pour valider la story independamment
- L'annee d'exercice dans le selecteur sera un placeholder (disabled/vide) tant que la feature comptes administratifs n'est pas implementee
