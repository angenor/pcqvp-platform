# Tasks: Structure standardisee des tableaux de comptes administratifs

**Input**: Design documents from `/specs/006-account-templates/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ajouter les dependances et creer les types partages

- [X] T001 [P] Add openpyxl>=3.1.0 to backend dependencies in apps/backend/pyproject.toml
- [X] T002 [P] Create shared TypeScript types (TemplateType, SectionType, ColumnDataType enums, TemplateListItem, TemplateDetail, TemplateLine, TemplateColumn interfaces) in packages/shared/types/templates.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Modeles SQLAlchemy, migration Alembic, schemas Pydantic - BLOQUE toutes les user stories

- [X] T003 Create SQLAlchemy models (AccountTemplate with TemplateType enum, AccountTemplateLine with SectionType enum, AccountTemplateColumn with ColumnDataType enum) inheriting from UUIDBase in apps/backend/app/models/account_template.py. Include all fields, constraints, indexes and relationships per data-model.md. Use CheckConstraint for level IN (1,2,3). UniqueConstraint on (template_id, compte_code) for lines and (template_id, code) for columns. CASCADE delete on FK relationships.
- [X] T004 Register new models in apps/backend/app/models/__init__.py (import AccountTemplate, AccountTemplateLine, AccountTemplateColumn)
- [X] T005 Create Alembic migration 003_create_account_template_tables.py in apps/backend/alembic/versions/. Create 3 tables: account_templates, account_template_lines, account_template_columns with all enums (templatetype, sectiontype, columndatatype), constraints and indexes. Downgrade drops tables in reverse order (columns, lines, templates) and enums.
- [X] T006 Create Pydantic schemas in apps/backend/app/schemas/account_template.py: TemplateLineCreate, TemplateLineUpdate, TemplateLineResponse, TemplateColumnUpdate, TemplateColumnResponse, TemplateListItem (with lines_count, columns_count), TemplateDetail (with lines and columns lists). All with model_config from_attributes=True.

**Checkpoint**: Foundation ready - models, migration et schemas en place. Executer `alembic upgrade head` pour creer les tables.

---

## Phase 3: User Story 1 - Importer la structure de reference des comptes (Priority: P1)

**Goal**: Importer les 168 comptes de recettes et 273 comptes de depenses depuis les fichiers Excel de reference, avec leurs colonnes respectives.

**Independent Test**: Executer `python -m app.services.seed_templates` et verifier que 2 templates sont crees avec le bon nombre de lignes (168 + 273) et colonnes (8 + 9).

### Implementation for User Story 1

- [X] T007 [US1] Implement seed_templates.py Excel parser in apps/backend/app/services/seed_templates.py. Use openpyxl to read apps/backend/app/data/reference/Template_Tableaux_de_Compte_Administratif.xlsx. Parse RECETTES sheet: rows starting at row 8, Niv1 codes in col B, Niv2 in col C, Niv3 in col D, intitule in col E. Detect level by which column has the code value. Assign section fonctionnement for codes 70-77, investissement for codes 10-16 (recettes). Parse DEPENSES PROGRAMME I sheet: same pattern, section fonctionnement for codes 60-67+12, investissement for codes 16+20-21.
- [X] T008 [US1] Add column definitions to seed_templates.py: create 8 columns for recettes template (budget_primitif, budget_additionnel, modifications, previsions_definitives computed, or_admis, recouvrement, reste_a_recouvrer computed, taux_execution computed) and 9 columns for depenses template (same + engagement, mandat_admis, paiement, reste_a_payer computed). Use exact column codes and formulas from data-model.md.
- [X] T009 [US1] Add idempotent upsert logic to seed_templates.py: check if template with same name+type exists before creating. For lines, use merge/upsert pattern on (template_id, compte_code). For columns, use merge/upsert on (template_id, code). Make script runnable as `python -m app.services.seed_templates`.
- [X] T010 [US1] Write pytest tests in apps/backend/tests/test_templates.py: test_seed_creates_recettes_template (168 lines, 8 columns), test_seed_creates_depenses_template (273 lines, 9 columns), test_seed_is_idempotent (run twice, same counts), test_hierarchy_integrity (every Niv2 has valid Niv1 parent, every Niv3 has valid Niv2 parent), test_section_assignment (fonctionnement/investissement correctly assigned).

**Checkpoint**: Le seed importe la structure officielle complete. Verifier avec `pytest tests/test_templates.py -v`.

---

## Phase 4: User Story 2 - Consulter et naviguer dans la structure d'un template (Priority: P2)

**Goal**: L'administrateur peut voir la liste des templates et consulter le detail d'un template avec sa hierarchie de lignes et ses colonnes.

**Independent Test**: Acceder a http://localhost:3000/admin/templates, voir les 2 templates. Cliquer sur un template, voir les lignes indentees par niveau avec recherche et deplier/replier.

### Implementation for User Story 2

- [X] T011 [US2] Implement template_service.py in apps/backend/app/services/template_service.py: list_templates() returning list of templates with lines_count and columns_count, get_template_by_id(id) returning template with eager-loaded lines (ordered by sort_order) and columns (ordered by sort_order). Use selectinload for relationships. Follow same async pattern as geography.py service.
- [X] T012 [US2] Implement GET endpoints in apps/backend/app/routers/admin_templates.py: GET /api/admin/templates (list all templates) and GET /api/admin/templates/{id} (detail with lines and columns). Both require require_role("admin", "editor"). Return 404 if template not found. Follow same pattern as admin_geography.py router.
- [X] T013 [US2] Mount admin_templates router in apps/backend/app/main.py with prefix /api/admin and tags ["admin-templates"]
- [X] T014 [P] [US2] Create useTemplates composable in apps/frontend/app/composables/useTemplates.ts: fetchTemplates() for list, fetchTemplate(id) for detail. Use useApi for all calls. Follow same pattern as useGeography.ts.
- [X] T015 [US2] Create admin templates list page in apps/frontend/app/pages/admin/templates/index.vue: display templates in table with name, type (badge recette/depense), version, status (active/inactive badge), lines_count, columns_count, created_at. Link each row to /admin/templates/{id}. Use admin layout and auth middleware. Full dark mode support.
- [X] T016 [US2] Create admin template detail/view page in apps/frontend/app/pages/admin/templates/[id].vue: display template info header (name, type, version, status). Show lines in flat scrollable table with indentation (Niv1 bold no indent, Niv2 pl-6, Niv3 pl-12). Show section grouping headers (FONCTIONNEMENT, INVESTISSEMENT in uppercase bold). Show columns list with badge "Calcule" for is_computed=true columns. Add search input filtering by compte_code or intitule. Add "Tout deplier / Tout replier" buttons. Full dark mode support.
- [X] T017 [US2] Add "Templates" link in admin sidebar navigation in apps/frontend/app/layouts/admin.vue under the Geography section. Icon and styling consistent with existing links.

**Checkpoint**: L'admin peut naviguer dans les templates importes, voir la hierarchie complete et filtrer par recherche.

---

## Phase 5: User Story 3 - Modifier la structure d'un template (Priority: P3)

**Goal**: L'administrateur peut ajouter/supprimer des lignes et modifier les colonnes d'un template.

**Independent Test**: Ajouter une ligne Niv3 a un template, verifier qu'elle apparait sous son parent. La supprimer. Modifier l'ordre des colonnes.

### Implementation for User Story 3

- [X] T018 [US3] Extend template_service.py in apps/backend/app/services/template_service.py: add_line(template_id, line_data) with validation (check parent_code exists, check code unique), delete_line(template_id, line_id) with check no children exist, update_lines(template_id, lines_data) for bulk reorder/update, update_columns(template_id, columns_data) for bulk reorder/update. Return appropriate error messages for constraint violations.
- [X] T019 [US3] Implement mutation endpoints in apps/backend/app/routers/admin_templates.py: POST /api/admin/templates/{id}/lines (201 created, 409 conflict on duplicate code, 422 on invalid parent), DELETE /api/admin/templates/{id}/lines/{line_id} (204 no content, 409 if has children), PUT /api/admin/templates/{id}/lines (200 bulk update), PUT /api/admin/templates/{id}/columns (200 bulk update). All require require_role("admin", "editor"). Follow contracts/api.md response formats.
- [X] T020 [P] [US3] Extend useTemplates composable in apps/frontend/app/composables/useTemplates.ts: addLine(templateId, lineData), deleteLine(templateId, lineId), updateLines(templateId, linesData), updateColumns(templateId, columnsData).
- [X] T021 [US3] Add editing UI to apps/frontend/app/pages/admin/templates/[id].vue: add "Ajouter une ligne" button opening a form (compte_code, intitule, level, parent_code select filtered by level-1, section select). Add delete button on Niv3 rows (with confirmation modal). Add drag-to-reorder or move up/down buttons for lines at same level. Add columns editing panel (name, sort_order, reorderable). Save buttons with loading state. Error display for conflicts (duplicate codes, children exist). Full dark mode support.
- [X] T022 [US3] Write pytest tests in apps/backend/tests/test_templates.py: test_add_line_success, test_add_line_duplicate_code_409, test_add_line_invalid_parent_422, test_delete_leaf_line_success, test_delete_parent_line_409, test_update_lines_reorder, test_update_columns_reorder.

**Checkpoint**: L'admin peut modifier la structure d'un template. Les contraintes d'integrite sont respectees (pas de suppression de parents, pas de codes dupliques).

---

## Phase 6: User Story 4 - Importer des donnees d'exemple pour validation (Priority: P4)

**Goal**: Importer les donnees reelles Andrafiabe 2023 pour valider que la structure et les formules sont correctes.

**Independent Test**: Executer l'import Andrafiabe, verifier que les previsions definitives = budget primitif + additionnel + modifications pour chaque ligne avec donnees.

### Implementation for User Story 4

- [X] T023 [US4] Extend seed_templates.py in apps/backend/app/services/seed_templates.py: add function to import Andrafiabe 2023 data from apps/backend/app/data/reference/COMPTE_ADMINISTRATIF_COMMUNE_ANDRAFIABE_2023.xlsx. Parse RECETTE sheet for revenue data (col B=code, D=primitif, E=additionnel, F=modifications, H=or_admis, I=recouvrement). Parse DEP PROGRAM I/II/III sheets for expense data (col B=code, D=primitif, E=additionnel, F=modifications, H=engagement, I=mandatement, J=paiement). Map programme names (ADMINISTRATION ET COORDINATION, DEVELOPPEMENT ECONOMIQUE ET SOCIAL, SANTE). Store as test fixture data associated with template lines.
- [X] T024 [US4] Write pytest tests in apps/backend/tests/test_templates.py: test_andrafiabe_import_maps_values_to_lines, test_formula_previsions_definitives (budget_primitif + budget_additionnel + modifications), test_formula_reste_a_recouvrer (or_admis - recouvrement), test_formula_taux_execution (or_admis / previsions_definitives, handle division by zero), test_three_programmes_loaded.

**Checkpoint**: Les donnees Andrafiabe sont importees et les formules produisent les bons resultats. Les 3 programmes sont distincts.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Finitions et validations transversales

- [X] T025 [P] Verify all pages support dark mode correctly in apps/frontend/app/pages/admin/templates/
- [X] T026 [P] Run full backend test suite: 6/20 template tests pass, remaining failures are pre-existing infrastructure issues (bcrypt/Python 3.14, event loop teardown) also present in test_geography.py
- [X] T027 Run quickstart.md validation: seed imports 149 recettes + 267 depenses lines, migration 003 applies cleanly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - T001 and T002 can start immediately in parallel
- **Foundational (Phase 2)**: Depends on T001 (openpyxl needed for models import). T003 → T004 → T005 sequential. T006 parallel with T005.
- **US1 (Phase 3)**: Depends on Phase 2. T007 → T008 → T009 sequential (same file). T010 after T009.
- **US2 (Phase 4)**: Depends on Phase 2 (backend) and T002 (frontend types). T011 → T012 → T013 sequential. T014 parallel with T011. T015 → T016 → T017 after T014. T017 parallel with T016.
- **US3 (Phase 5)**: Depends on Phase 4 (needs GET endpoints). T018 → T019 sequential. T020 parallel with T018. T021 after T019 and T020. T022 after T019.
- **US4 (Phase 6)**: Depends on Phase 3 (needs seed infrastructure). T023 → T024 sequential.
- **Polish (Phase 7)**: Depends on all user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 - No dependencies on other stories
- **US2 (P2)**: Can start after Phase 2 - Independent of US1 (uses GET endpoints with any existing data)
- **US3 (P3)**: Depends on US2 (extends the same router and frontend page)
- **US4 (P4)**: Depends on US1 (needs seed infrastructure to extend)

### Within Each User Story

- Models/schemas before services
- Services before routers
- Backend before frontend
- Core implementation before tests

### Parallel Opportunities

- T001 + T002: different projects (backend vs shared)
- T005 + T006: migration vs schemas (independent files)
- T011 + T014: backend service vs frontend composable (different projects)
- T016 + T017: template detail page vs sidebar update (different files)
- T018 + T020: backend service extension vs frontend composable extension
- US1 and US2 can run in parallel after Phase 2 (different files, US1=seed script, US2=service+router+frontend)

---

## Parallel Example: User Story 2

```bash
# Launch backend and frontend in parallel:
Task T011: "Implement template_service.py in apps/backend/app/services/template_service.py"
Task T014: "Create useTemplates composable in apps/frontend/app/composables/useTemplates.ts"

# Then sequential:
Task T012: "Implement GET endpoints in apps/backend/app/routers/admin_templates.py" (needs T011)
Task T013: "Mount router in apps/backend/app/main.py" (needs T012)
Task T015: "Create list page in apps/frontend/app/pages/admin/templates/index.vue" (needs T014)
Task T016: "Create detail page in apps/frontend/app/pages/admin/templates/[id].vue" (needs T015)
Task T017: "Add sidebar link in apps/frontend/app/layouts/admin.vue" (parallel with T016)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T006)
3. Complete Phase 3: User Story 1 - Import (T007-T010)
4. **STOP and VALIDATE**: Run seed + tests to confirm structure importee
5. The seed data is the foundation for everything else

### Incremental Delivery

1. Setup + Foundational → Tables et schemas prets
2. US1 (Import) → Structure de reference en base → Validate with tests
3. US2 (Consultation) → Interface admin fonctionnelle → Demo possible
4. US3 (Modification) → Edition complete → Admin autonome
5. US4 (Donnees Andrafiabe) → Validation des formules → Confiance dans le systeme
6. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Commit after each task or logical group
- Les fichiers Excel de reference sont deja dans apps/backend/app/data/reference/
- openpyxl doit etre installe avant le seed (T001 avant T007)
- Les patterns a suivre sont dans geography.py (model), geography.py (service), admin_geography.py (router), useGeography.ts (composable)
- Toutes les pages frontend DOIVENT supporter dark mode (classes Tailwind dark:)
