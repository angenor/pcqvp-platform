# Tasks: Saisie et stockage des comptes administratifs

**Input**: Design documents from `/specs/007-admin-accounts-entry/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api-endpoints.md

**Tests**: Inclus en phase finale (constitution exige la couverture des chemins critiques).

**Organization**: Tasks groupees par user story pour permettre l'implementation et le test independants.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Peut s'executer en parallele (fichiers differents, pas de dependances)
- **[Story]**: User story concernee (US1, US2, US3, US4, US5)
- Chemins exacts inclus dans chaque description

## Path Conventions

- **Backend**: `apps/backend/app/` (models/, schemas/, routers/, services/)
- **Frontend**: `apps/frontend/app/` (pages/, composables/, components/)
- **Shared**: `packages/shared/types/`
- **Migration**: `apps/backend/alembic/versions/`
- **Tests**: `apps/backend/tests/`

---

## Phase 1: Setup (Infrastructure partagee)

**Purpose**: Migration DB, modeles, schemas et types partages — socle pour toutes les user stories

- [X] T001 [P] Creer les types partages TypeScript (enums CollectiviteType, CompteStatus, interfaces CompteAdministratif, RecetteLine, DepenseProgram, DepenseLine, CompteListItem, CompteDetail, RecapRecettes, RecapDepenses, Equilibre) dans packages/shared/types/comptes.ts
- [X] T002 [P] Creer la migration Alembic 004 avec les 5 tables (comptes_administratifs, recette_lines, depense_programs, depense_lines, account_change_logs), les enums PostgreSQL (collectivitetype, comptestatus), les contraintes UNIQUE et les index composites dans apps/backend/alembic/versions/004_create_compte_administratif_tables.py
- [X] T003 Creer les 5 modeles SQLAlchemy (CompteAdministratif, RecetteLine, DepenseProgram, DepenseLine, AccountChangeLog) avec les enums StrEnum (CollectiviteType, CompteStatus), les relations lazy="selectin", les cascades et les contraintes CHECK dans apps/backend/app/models/compte_administratif.py
- [X] T004 Enregistrer les modeles dans apps/backend/app/models/__init__.py (import des 5 classes + enums)
- [X] T005 Creer les schemas Pydantic v2 (CompteCreate, CompteListItem, CompteDetail, RecetteLineUpsert, RecetteLineResponse, DepenseProgramCreate, DepenseProgramUpdate, DepenseLineUpsert, DepenseLineResponse, StatusUpdate, ChangeLogEntry, RecapRecettesResponse, RecapDepensesResponse, EquilibreResponse) dans apps/backend/app/schemas/compte_administratif.py

---

## Phase 2: Foundational (Prerequisites bloquants)

**Purpose**: Services de base et composable frontend — DOIT etre termine avant toute user story

- [X] T006 Implementer les fonctions de base dans apps/backend/app/services/compte_service.py : validate_collectivite(db, type, id) qui fait un lookup Province/Region/Commune selon le type, create_compte(db, data, user_id) qui valide la collectivite + verifie l'unicite type+id+annee + cree le compte + cree 3 programmes par defaut, get_compte_by_id(db, id) qui charge le compte avec ses relations
- [X] T007 Implementer les calculs de base dans apps/backend/app/services/account_service.py : compute_line_values(values, template_type) qui calcule les colonnes derivees (previsions_definitives, reste, taux_execution), compute_hierarchical_sums(lines, template_lines) qui calcule les sommes Niv2 et Niv1 a partir des Niv3
- [X] T008 Creer le composable frontend useComptes() dans apps/frontend/app/composables/useComptes.ts avec toutes les fonctions API : createCompte(), fetchComptes(filters), fetchCompte(id), upsertRecetteLine(compteId, data), createProgramme(compteId, data), updateProgramme(compteId, progId, data), deleteProgramme(compteId, progId), upsertDepenseLine(compteId, progId, data), updateStatus(compteId, status), fetchRecapRecettes(id), fetchRecapDepenses(id), fetchEquilibre(id), fetchChangelog(id)
- [X] T009 Ajouter le lien "Comptes administratifs" dans la navigation sidebar de apps/frontend/app/layouts/admin.vue (section Comptes, icone et route /admin/accounts, avec classes dark: appropriees)

**Checkpoint**: Foundation prete — les user stories peuvent commencer

---

## Phase 3: User Story 1 - Creer un compte administratif (Priority: P1)

**Goal**: Permettre a un admin/editor de creer un compte administratif pour une collectivite et une annee, avec 3 programmes par defaut

**Independent Test**: Creer un compte pour Andrafiabe 2023 via l'interface et verifier qu'il apparait avec 3 programmes

### Implementation for User Story 1

- [X] T010 [US1] Creer le router apps/backend/app/routers/admin_comptes.py avec le prefix "/api/admin/comptes" et les 2 premiers endpoints : POST / (creation avec validation collectivite, unicite, 3 programmes par defaut, retourne 201 avec CompteDetail) et GET /{id} (detail complet du compte avec programmes), en utilisant require_role("admin", "editor") et le pattern service retourne Model|str
- [X] T011 [US1] Enregistrer le router admin_comptes dans apps/backend/app/main.py via app.include_router()
- [X] T012 [US1] Creer la page apps/frontend/app/pages/admin/accounts/new.vue avec le formulaire de creation : select type de collectivite (province/region/commune), composant GeographySelector dynamique selon le type selectionne, input annee d'exercice obligatoire, bouton creer qui appelle createCompte() et redirige vers la page du compte cree. Gestion du cas region (pas de commune requise). Dark mode obligatoire.

**Checkpoint**: Un compte peut etre cree avec 3 programmes par defaut

---

## Phase 4: User Story 2 - Saisir les donnees de recettes (Priority: P1)

**Goal**: Permettre la saisie des recettes avec auto-save ligne par ligne et calculs dynamiques

**Independent Test**: Saisir les recettes d'Andrafiabe 2023 et verifier que les totaux calcules correspondent au document officiel

### Implementation for User Story 2

- [X] T013 [US2] Ajouter la fonction upsert_recette_line(db, compte_id, template_line_id, values, user) dans apps/backend/app/services/compte_service.py : validation que template_line_id est du bon template, INSERT ON CONFLICT UPDATE sur (compte_admin_id, template_line_id), creation d'un changelog si le compte est publie (avec old_value/new_value)
- [X] T014 [US2] Ajouter la fonction get_recettes_with_computed(db, compte_id) dans apps/backend/app/services/account_service.py : charger toutes les RecetteLine du compte, joindre les AccountTemplateLine pour la structure, appliquer compute_line_values() sur chaque ligne, appliquer compute_hierarchical_sums() pour les Niv1/Niv2, retourner les lignes enrichies
- [X] T015 [US2] Ajouter l'endpoint PUT /api/admin/comptes/{id}/recettes dans apps/backend/app/routers/admin_comptes.py : accepte RecetteLineUpsert, appelle upsert_recette_line(), retourne RecetteLineResponse avec les computed values
- [X] T016 [US2] Enrichir l'endpoint GET /api/admin/comptes/{id} dans admin_comptes.py pour inclure les recettes calculees (appel a get_recettes_with_computed) dans la reponse CompteDetail
- [X] T017 [P] [US2] Creer le composant apps/frontend/app/components/AccountDataTable.vue : props (templateLines, columns, editableColumns, values, computedFn), affichage hierarchique avec indentation (Niv1 gras, Niv2 indent, Niv3 double-indent), sections Fonctionnement/Investissement, cellules editables uniquement pour Niv3, emit @save-line(templateLineId, values) sur blur de cellule, indicateur de synchronisation par ligne (pending/success/error avec retry), colonnes calculees en lecture seule avec badge "Calcule", dark mode obligatoire
- [X] T018 [US2] Creer la page apps/frontend/app/pages/admin/accounts/[id]/recettes.vue : charger le compte et le template recettes, passer les donnees a AccountDataTable, handler @save-line qui appelle upsertRecetteLine() du composable, recalcul des sommes hierarchiques localement apres chaque save reussi, indicateur global de synchronisation, dark mode obligatoire

**Checkpoint**: Les recettes peuvent etre saisies avec auto-save et calculs dynamiques

---

## Phase 5: User Story 3 - Saisir les depenses par programme (Priority: P1)

**Goal**: Permettre la saisie des depenses par programme avec onglets, ajout/suppression/renommage de programmes

**Independent Test**: Saisir les depenses du Programme I d'Andrafiabe 2023 et verifier les calculs

### Implementation for User Story 3

- [X] T019 [US3] Ajouter les fonctions CRUD programmes dans apps/backend/app/services/compte_service.py : add_programme(db, compte_id, intitule) avec numero auto-incremente, update_programme(db, compte_id, prog_id, intitule), delete_programme(db, compte_id, prog_id) avec CASCADE sur DepenseLine, changelog si publie pour chaque operation
- [X] T020 [US3] Ajouter la fonction upsert_depense_line(db, programme_id, template_line_id, values, user) dans apps/backend/app/services/compte_service.py : validation template depense, INSERT ON CONFLICT UPDATE sur (programme_id, template_line_id), changelog si publie
- [X] T021 [US3] Ajouter la fonction get_depenses_with_computed(db, compte_id) dans apps/backend/app/services/account_service.py : charger les programmes avec leurs DepenseLine, joindre les template lines, appliquer compute_line_values() et compute_hierarchical_sums() par programme, retourner les programmes enrichis
- [X] T022 [US3] Ajouter les endpoints programmes dans apps/backend/app/routers/admin_comptes.py : POST /{id}/programmes (201), PUT /{id}/programmes/{prog_id} (200), DELETE /{id}/programmes/{prog_id} (204), PUT /{id}/programmes/{prog_id}/depenses (200, upsert ligne depense)
- [X] T023 [US3] Enrichir GET /api/admin/comptes/{id} pour inclure les depenses calculees par programme (appel a get_depenses_with_computed)
- [X] T024 [US3] Creer la page apps/frontend/app/pages/admin/accounts/[id]/depenses.vue : onglets dynamiques (un par programme), reutiliser AccountDataTable pour chaque programme, bouton "Ajouter un programme", dialogue de confirmation avant suppression d'un programme, edition inline de l'intitule du programme, dark mode obligatoire

**Checkpoint**: Les depenses peuvent etre saisies par programme avec gestion complete des programmes

---

## Phase 6: User Story 4 - Consulter les recapitulatifs et l'equilibre (Priority: P2)

**Goal**: Afficher les recapitulatifs recettes, depenses croisees et le tableau d'equilibre, tout calcule dynamiquement

**Independent Test**: Comparer les recapitulatifs calcules avec les feuilles RECAP RECETTE, RECAP DEP et EQUILIBRE du document Andrafiabe 2023

### Implementation for User Story 4

- [X] T025 [P] [US4] Implementer calculate_recettes_recap(db, compte_id) dans apps/backend/app/services/account_service.py : agreger les recettes par categorie Niv1, grouper par section (fonctionnement/investissement), separer operations reelles et operations d'ordre (basees sur le sort_order des template lines), calculer sous-totaux par section
- [X] T026 [P] [US4] Implementer calculate_depenses_recap(db, compte_id) dans apps/backend/app/services/account_service.py : croisement categories Niv1 x programmes avec mandat_admis, paiement et reste_a_payer, totaux par categorie et par programme, groupement par section
- [X] T027 [US4] Implementer calculate_equilibre(db, compte_id) dans apps/backend/app/services/account_service.py : mettre en regard recettes et depenses par section, distinguer operations reelles et operations d'ordre, calculer excedent/deficit par section et resultat definitif global
- [X] T028 [US4] Ajouter les 3 endpoints recapitulatifs dans apps/backend/app/routers/admin_comptes.py : GET /{id}/recapitulatifs/recettes, GET /{id}/recapitulatifs/depenses, GET /{id}/recapitulatifs/equilibre
- [X] T029 [US4] Creer la page apps/frontend/app/pages/admin/accounts/[id]/recap.vue avec 3 sections : tableau recap recettes (Niv1 par section), tableau croise depenses (comptes x programmes), tableau d'equilibre (depenses/recettes cote a cote avec excedent/deficit). Tous les tableaux en lecture seule. Dark mode obligatoire.

**Checkpoint**: Les recapitulatifs et l'equilibre sont consultables et correspondent au document officiel

---

## Phase 7: User Story 5 - Publier et gerer le statut (Priority: P2)

**Goal**: Permettre la publication/depublication avec journal des modifications, et la liste filtree des comptes

**Independent Test**: Publier un compte, modifier une valeur, verifier le journal, depublier, filtrer la liste

### Implementation for User Story 5

- [X] T030 [US5] Ajouter la fonction update_status(db, compte_id, new_status, user) dans apps/backend/app/services/compte_service.py : changement de statut draft/published, creation changelog entry pour tout changement de statut
- [X] T031 [US5] Ajouter la fonction list_comptes(db, collectivite_type, collectivite_id, annee) dans apps/backend/app/services/compte_service.py avec filtres optionnels et resolution du nom de collectivite (lookup Province/Region/Commune)
- [X] T032 [US5] Ajouter les endpoints dans apps/backend/app/routers/admin_comptes.py : GET / (liste filtree avec query params), PUT /{id}/status (admin only via require_role("admin")), GET /{id}/changelog
- [X] T033 [US5] Creer la page apps/frontend/app/pages/admin/accounts/index.vue : tableau des comptes avec filtres (select collectivite_type, select collectivite via GeographySelector, input annee), colonnes (collectivite, annee, statut, date modification), bouton "Nouveau compte" vers /admin/accounts/new, liens vers les sous-pages (recettes, depenses, recap). Dark mode obligatoire.
- [X] T034 [US5] Ajouter les boutons Publier/Depublier et le lien vers le journal dans les pages de detail du compte (recettes.vue, depenses.vue, recap.vue) : bouton conditionnel selon le role (admin only pour publier), badge statut visible, lien vers le changelog

**Checkpoint**: Les comptes peuvent etre publies/depublies avec tracabilite, la liste est filtrable

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Tests backend, validation des calculs et coherence globale

- [X] T035 [P] Creer les tests backend dans apps/backend/tests/test_comptes.py : fixtures (db, client, admin_headers, seed templates + commune Andrafiabe), tests CRUD compte (creation, doublon 409, validation collectivite), tests upsert recette/depense (auto-save, valeurs JSONB), tests programmes (CRUD, suppression cascade), tests calculs (computed columns, sommes hierarchiques sur donnees Andrafiabe), tests recapitulatifs (recap recettes, recap depenses croise, equilibre avec verification des montants officiels), tests publication (status change, changelog, role admin only)
- [X] T036 [P] Executer la migration 004 sur la base de test et valider que les 5 tables sont creees correctement avec les contraintes (unique, check, FK, index)
- [X] T037 Valider le parcours complet quickstart.md : creer un compte Andrafiabe 2023, saisir les recettes et depenses des 3 programmes, verifier les recapitulatifs et l'equilibre, publier le compte

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Pas de dependance — peut commencer immediatement
- **Foundational (Phase 2)**: Depend de Phase 1 (modeles et schemas necessaires) — BLOQUE toutes les user stories
- **US1 (Phase 3)**: Depend de Phase 2 — peut commencer immediatement apres
- **US2 (Phase 4)**: Depend de US1 (besoin d'un compte existant pour saisir des recettes)
- **US3 (Phase 5)**: Depend de US1 (besoin d'un compte avec programmes), peut commencer en parallele de US2
- **US4 (Phase 6)**: Depend de US2 et US3 (besoin de donnees saisies pour calculer les recapitulatifs)
- **US5 (Phase 7)**: Depend de US1 (besoin de comptes existants pour la liste), peut commencer en parallele de US2/US3
- **Polish (Phase 8)**: Depend de toutes les phases precedentes

### User Story Dependencies

- **US1 (P1)**: Apres Phase 2 — aucune dependance sur d'autres stories
- **US2 (P1)**: Apres US1 — necessite un compte existant pour la saisie
- **US3 (P1)**: Apres US1 — peut etre parallele a US2 (fichiers differents sauf account_service.py)
- **US4 (P2)**: Apres US2 + US3 — les recapitulatifs dependent des donnees saisies
- **US5 (P2)**: Apres US1 — peut etre parallele a US2/US3/US4 (endpoints et pages independants)

### Within Each User Story

- Modeles/schemas (Phase 1) avant services
- Services avant endpoints/router
- Endpoints avant pages frontend
- Composant partage (AccountDataTable) avant pages qui l'utilisent

### Parallel Opportunities

**Phase 1** (toutes en parallele) :
```
T001 (types TS) || T002 (migration) — puis T003 (modeles) → T004 (init) + T005 (schemas)
```

**Phase 2** :
```
T006 (service CRUD) || T007 (service calculs) || T008 (composable frontend) || T009 (sidebar)
```

**Apres Phase 3 (US1) terminee** :
```
US2 (T013-T018) || US3 backend (T019-T023) || US5 backend (T030-T032)
```

**Phase 6 (US4)** :
```
T025 (recap recettes) || T026 (recap depenses) — puis T027 (equilibre) → T028 (endpoints) → T029 (page)
```

---

## Parallel Example: User Story 2

```bash
# Apres US1 terminee, lancer en parallele :
Task T013: "upsert_recette_line dans compte_service.py"
Task T014: "get_recettes_with_computed dans account_service.py"

# Puis sequentiellement :
Task T015: "Endpoint PUT recettes dans admin_comptes.py" (depend de T013+T014)
Task T016: "Enrichir GET /comptes/{id}" (depend de T014)
Task T017: "Composant AccountDataTable.vue" (independant du backend)
Task T018: "Page recettes.vue" (depend de T015+T017)
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Completer Phase 1: Setup (migration + modeles + schemas + types)
2. Completer Phase 2: Foundational (services de base + composable)
3. Completer Phase 3: US1 (creation de compte)
4. Completer Phase 4: US2 (saisie recettes avec calculs)
5. **STOP et VALIDER**: Creer un compte Andrafiabe 2023, saisir les recettes, verifier les calculs
6. Deployer/Demo si pret

### Incremental Delivery

1. Setup + Foundational → Socle pret
2. US1 → Creation de comptes → Demo
3. US2 → Saisie recettes avec auto-save → Demo
4. US3 → Saisie depenses par programme → Demo
5. US4 → Recapitulatifs et equilibre → Demo (validation Andrafiabe)
6. US5 → Publication et gestion → Demo
7. Polish → Tests + validation complete

---

## Notes

- [P] = fichiers differents, pas de dependances
- [Story] = user story pour la tracabilite
- Chaque user story est independamment testable une fois terminee
- Committer apres chaque tache ou groupe logique
- Le composant AccountDataTable.vue est reutilise par US2 (recettes) et US3 (depenses)
- Les calculs dynamiques (account_service.py) sont enrichis incrementalement par US2, US3, US4
- Le changelog est integre dans les upsert existants (US2/US3) lors de US5 via un hook dans le service
