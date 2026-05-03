# Tasks: Carte interactive Madagascar — GeoJSON administrable depuis le back-office

**Input**: Design documents from `/specs/019-regions-geojson-admin/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: INCLUDED. La spec liste explicitement les tests à livrer (unit backend, intégration backend, frontend, E2E).

**Organization**: tâches groupées par user story (US1=P1, US2=P2, US3=P2, US4=P3) pour permettre implémentation et test indépendants.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallélisable (fichiers distincts, pas de dépendance sur tâche incomplète)
- **[Story]**: US1, US2, US3, US4 — phases user-story uniquement
- Setup, Foundational, Polish : pas de label Story
- Chemins relatifs depuis racine repo `pcqvp-platform-new-version/`

## Path Conventions

Web app monorepo (cf. plan.md) :
- Backend : `backend/app/...`, `backend/alembic/versions/...`, `backend/tests/...`
- Frontend : `frontend/app/...`, `frontend/tests/...`
- Shared : `packages/shared/src/...`
- Docs : `docs/admin/...`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: dépendances, configuration, types partagés.

- [X] T001 Ajouter `shapely>=2.0`, `simplification>=0.7`, `ijson>=3.2` à la section `[project.dependencies]` de `backend/pyproject.toml` ; lancer `pip install -e ".[dev]"` pour vérifier.
- [X] T002 [P] Ajouter les clés de configuration geodata (`GEODATA_MAX_UPLOAD_BYTES`, `GEODATA_MAX_VERSIONS`, `GEODATA_SIMPLIFY_RATIO`, `GEODATA_MIN_FEATURE_AREA_DEG2`, `GEODATA_FEATURES_MIN_WARN`, `GEODATA_FEATURES_MAX_WARN`, `GEODATA_SYNC_TIMEOUT_SECONDS`, `GEODATA_RATE_LIMIT_UPLOADS_PER_HOUR`, `GEODATA_NAME_ALIASES`, `GEODATA_COORDINATE_PRECISION`, `GEODATA_PUBLIC_CACHE_MAX_AGE`, `GEODATA_REGION_CODE_PREFIX`) dans `backend/app/core/config.py` (cf. data-model.md §Configuration applicative).
- [X] T003 [P] Créer `packages/shared/src/types/geodata.ts` exposant `GeodataVersionListItem`, `GeodataVersionDetail`, `GeodataWarning`, `GeodataJobStatus`, `GeodataUploadResponse` (formes alignées sur `contracts/admin-geodata.openapi.yaml`).
- [X] T004 [P] Créer `frontend/app/types/geodata.ts` qui re-exporte les types depuis `@pcqvp/shared` (ou les déclare localement si `packages/shared` n'est pas wired pour le runtime Nuxt).
- [X] T005 Préparer le fichier de seed `backend/alembic/seed/madagascar_regions_v1.geojson` (~400 Ko) en faisant tourner localement le pipeline sur l'export Overpass actuel des 23 régions ; vérifier `features_count == 23` et `size < 1 MB`. Commiter le fichier.

**Checkpoint** : deps installées, config alimentée, seed file prêt, types partagés disponibles.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: modèle DB, schémas Pydantic, pipeline pur, services, dépendances d'auth — tout ce dont US1+ a besoin avant de coder un endpoint.

⚠️ Aucune story ne peut commencer avant complétion de cette phase.

- [X] T006 Créer le modèle SQLAlchemy `GeodataVersion` dans `backend/app/models/geodata_version.py` (héritage `UUIDBase`, colonnes et défauts cf. data-model.md §Schéma).
- [X] T007 Enregistrer le modèle dans `backend/app/models/__init__.py` (import explicite pour Alembic autogenerate).
- [X] T008 Créer la migration Alembic `backend/alembic/versions/009_create_geodata_versions.py` : `CREATE TABLE geodata_versions` + 4 index (incl. `uq_geodata_version_one_active` partial unique sur `is_active=true` cf. R6) ; `downgrade` = `DROP TABLE`.
- [X] T009 Créer la migration `backend/alembic/versions/010_seed_geodata_initial.py` qui charge `seed/madagascar_regions_v1.geojson`, INSERT avec `is_active=true`, `created_by_user_id` = ID admin seed ; `downgrade` supprime cet enregistrement par `original_filename`.
- [ ] T010 Lancer `alembic upgrade head` (à exécuter manuellement) puis vérifier en SQL `SELECT count(*), bool_or(is_active) FROM geodata_versions` (attendu : 1, true).
- [X] T011 [P] Créer les schémas Pydantic v2 dans `backend/app/schemas/geodata.py` : `GeodataWarning`, `GeodataUploadResponse`, `GeodataJobStatus`, `GeodataVersionListItem`, `GeodataVersionDetail`, `GeodataVersionList` (paginé), `GeodataActivateResponse` — alignés avec `contracts/admin-geodata.openapi.yaml`.
- [X] T012 [P] Implémenter le pipeline pur dans `backend/app/services/geodata_pipeline.py` avec fonctions immutables :
  - `parse_streaming(file_path) -> Iterable[Feature]` (ijson, filtre `admin_level=='4'` + `name` non vide + geometry Polygon/MultiPolygon)
  - `dedupe_by_name(features) -> tuple[list[Feature], list[Warning]]` (max area)
  - `normalize_names(features, aliases) -> list[Feature]` (NFD + lookup + canonical)
  - `assign_region_codes(features, prefix) -> list[Feature]` (slugify NFD ASCII)
  - `simplify_features(features, ratio) -> tuple[list[Feature], list[Warning]]` (simplification Visvalingam-weighted, validation shapely, drop si area < 0.001)
  - `round_coordinates(features, precision) -> list[Feature]`
  - `sanitize_properties(features) -> list[Feature]` (drop tout sauf `name, name_official, region_code, admin_level`)
  - `build_warnings(features, expected_min, expected_max) -> list[Warning]` (count out-of-range)
  - `run_pipeline(file_path, settings) -> PipelineResult` (orchestrateur)
- [X] T013 [P] Implémenter `backend/app/services/geodata_jobs.py` : registre `dict[UUID, GeodataJob]` avec `asyncio.Lock`, fonctions `create_job`, `update_status`, `get_job`, `purge_expired` (TTL 30 min après `completed_at`).
- [X] T014 Implémenter `backend/app/services/geodata_service.py` (orchestration DB) :
  - `create_version(db, user, pipeline_result, original_filename, original_size, notes) -> GeodataVersion` (purge LRU dans la même transaction si `count >= 50`)
  - `list_versions(db, limit, offset) -> tuple[list[GeodataVersion], int]`
  - `get_version(db, version_id) -> GeodataVersion`
  - `activate_version(db, target_id) -> GeodataVersion` (transaction `FOR UPDATE` + UPDATEs atomiques cf. R6)
  - `delete_version(db, version_id) -> None` (refuse si `is_active=true` → lever `HTTPException(409)`)
  - `get_active_version(db) -> GeodataVersion | None`
- [X] T015 [P] Étendre `backend/app/services/audit_log.py` avec `record_geodata_uploaded`, `record_geodata_activated`, `record_geodata_deleted` (payload conforme R12 / data-model §AuditLog).
- [X] T016 Définir la dépendance d'auth admin réutilisable. Si elle n'existe pas déjà sous `backend/app/core/security.py` (`get_current_admin_user`), l'extraire/la créer pour exiger `role == 'admin'` (rejette `editor` cf. clarification spec → FR-027).

**Checkpoint** : modèle DB en place, version seed active, pipeline + service + audit + auth admin disponibles. Les 4 user stories peuvent maintenant être implémentées en parallèle (avec quelques dépendances explicitées plus bas).

---

## Phase 3: User Story 1 — Publier une nouvelle géographie (Priority: P1) 🎯 MVP

**Goal**: un admin upload un GeoJSON, le système le traite, l'admin l'active, la carte d'accueil reflète immédiatement la nouvelle version.

**Independent Test**: depuis le seed initial, uploader un GeoJSON modifié (ex. 23 régions avec un nom changé), l'activer, recharger la home, vérifier que le nom modifié apparaît dans le tooltip de la région.

### Tests pour US1

- [X] T017 [P] [US1] Test unitaire pipeline `backend/tests/unit/test_geodata_pipeline.py::test_pipeline_22mb_to_under_1mb` : sur fichier d'échantillon Overpass committé en fixture, vérifier `features_count == 23`, `processed_size < 1 MB`, `compression_ratio >= 0.95`.
- [X] T018 [P] [US1] Test unitaire pipeline `test_pipeline_drops_non_admin_level_4` (filtrage features non-régionales) dans `backend/tests/unit/test_geodata_pipeline.py`.
- [X] T019 [P] [US1] Test unitaire pipeline `test_pipeline_dedup_keeps_largest_area` (déduplication par nom) dans `backend/tests/unit/test_geodata_pipeline.py`.
- [X] T020 [P] [US1] Test unitaire pipeline `test_pipeline_normalizes_matsiatra_ambony_to_haute_matsiatra` (alias) dans `backend/tests/unit/test_geodata_pipeline.py`.
- [X] T021 [P] [US1] Test unitaire pipeline `test_pipeline_region_code_stable` (NFD slugify, `MG-haute-matsiatra` etc.) dans `backend/tests/unit/test_geodata_pipeline.py`.
- [X] T022 [P] [US1] Test intégration `backend/tests/integration/test_admin_geodata.py::test_upload_then_activate_then_public_endpoint_serves_new_version` (parcours bout-en-bout).
- [X] T023 [P] [US1] Test intégration `backend/tests/integration/test_public_geojson.py::test_public_endpoint_returns_200_with_etag_then_304_on_if_none_match`.
- [X] T024 [P] [US1] Test intégration `backend/tests/integration/test_admin_geodata.py::test_only_one_active_version_after_concurrent_activations` (deux requêtes simultanées → une 200, une 409).
- [X] T025 [P] [US1] Test composable Vitest `frontend/tests/unit/useGeodataAdmin.spec.ts::uploadVersion polls until done`.

### Backend US1

- [X] T026 [US1] Créer le router admin upload+activation dans `backend/app/routers/admin_geodata.py` :
  - `POST /api/admin/geodata/regions/upload` : valider extension/MIME/taille (50 Mo) AVANT traitement ; sauvegarder en `tempfile.NamedTemporaryFile` ; lancer pipeline via `asyncio.wait_for(run_in_executor..., timeout=settings.GEODATA_SYNC_TIMEOUT_SECONDS)` ; sur succès sync → `create_version` + audit + 201 `UploadResponse` ; sur `TimeoutError` → enregistrer job + `BackgroundTasks` + 202 `JobAccepted`.
  - `GET /api/admin/geodata/regions/jobs/{job_id}` : lecture du registre `geodata_jobs`.
  - `POST /api/admin/geodata/regions/versions/{id}/activate` : `activate_version` + `record_geodata_activated` + 200 `VersionDetail`.
  - Auth : `Depends(get_current_admin_user)` sur tous.
- [X] T027 [US1] Étendre `backend/app/routers/geography.py` avec `GET /api/geography/regions/geojson` (pas d'auth) :
  - Récupérer `get_active_version`.
  - Calculer `etag = f'W/"{version.id}"'`.
  - Si `If-None-Match` correspond → `Response(status=304, headers={ETag, Cache-Control})`.
  - Sinon → `JSONResponse(version.geojson_processed, headers={ETag, 'Cache-Control': 'public, max-age=3600', 'Content-Type': 'application/geo+json'})`.
  - Si aucune version active → `503` avec `{detail: "No active geodata version"}`.
- [X] T028 [US1] Enregistrer le router admin dans `backend/app/main.py` : `from app.routers.admin_geodata import router as admin_geodata_router` + `app.include_router(admin_geodata_router)`.

### Frontend US1

- [X] T029 [P] [US1] Composable `frontend/app/composables/useGeodataAdmin.ts` exposant `uploadVersion(file, notes?)`, `pollJob(jobId)`, `activateVersion(id)` (placeholders pour `listVersions`, `getVersion`, `deleteVersion` qui seront utilisés en US2 mais peuvent être stubbés). Construit sur `useApi()`. Polling tous les 1500 ms jusqu'à `done` ou `failed`.
- [X] T030 [US1] Page admin `frontend/app/pages/admin/geodata/regions/index.vue` :
  - Layout `admin`, middleware `auth` + check rôle `admin` (redirect 403 sinon — clarification spec).
  - Section « Version active » : carte d'identité (date, taille, nb régions, liste de noms via `region_names`).
  - Bouton « Téléverser une nouvelle version » → ouvre `UploadVersionModal`.
- [X] T031 [P] [US1] Composant `frontend/app/components/geodata/UploadVersionModal.vue` :
  - drag & drop accepte `.geojson` / `.json`.
  - `<progress>` durant l'upload + spinner durant le polling async.
  - Affiche stats post-traitement (`features_count`, `processed_size_bytes`, `region_names`) et liste des `warnings`.
  - Bouton « Activer maintenant » qui ouvre `ActivateVersionModal`.
  - Dark/light Tailwind.
- [X] T032 [P] [US1] Composant `frontend/app/components/geodata/ActivateVersionModal.vue` : confirmation expliquant l'impact (carte d'accueil mise à jour immédiatement). Sur OK, appelle `activateVersion(id)`.
- [X] T033 [US1] Modifier `frontend/app/layouts/admin.vue` : ajouter un lien sidebar « Géodonnées » sous la section Géographie, pointant vers `/admin/geodata/regions`. Visible uniquement si `user.role === 'admin'`.
- [X] T034 [US1] Refactor `frontend/app/components/MadagascarMap.vue` :
  - Supprimer `import('@amcharts/amcharts5-geodata/madagascarRegionHigh')` et le mapping `amchartsToRegionName`.
  - Au `onMounted`, `await useApi('/api/geography/regions/geojson')` ; gérer trois états locaux `loading | success | error`.
  - Sur `success`, injecter le GeoJSON dans `am5map.MapPolygonSeries.geoJSON`.
  - Lookup région↔BDD : sur chaque feature, `properties.name` normalisé (NFD + casefold) comparé à la liste `useGeography().regions`.
  - Sur `error`, afficher un message localisé en zone carte (« Carte temporairement indisponible »), pas de crash.
  - Préserver clic, hover, légende, indicateurs de chargement, dark/light.
  - Garder le fichier sous 320 lignes.

**Checkpoint US1** : un admin peut publier une nouvelle géographie en < 5 min ; la carte d'accueil affiche la nouvelle version après recharge. MVP livrable.

---

## Phase 4: User Story 2 — Historique et rollback (Priority: P2)

**Goal**: lister les versions, prévisualiser une version inactive, réactiver une version antérieure, supprimer une inactive.

**Independent Test**: après US1, uploader une 2ᵉ version, l'activer, puis ré-activer la 1ʳᵉ, vérifier que `GET /api/geography/regions/geojson` renvoie un autre `ETag` et que le contenu correspond à la 1ʳᵉ.

### Tests pour US2

- [X] T035 [P] [US2] Test intégration `backend/tests/integration/test_admin_geodata.py::test_list_versions_paginated` (création de 5 versions, `?limit=2&offset=2` retourne items 3-4).
- [X] T036 [P] [US2] Test intégration `backend/tests/integration/test_admin_geodata.py::test_rollback_restores_previous_geojson` (active V1, V2, V1 ; final endpoint sert payload V1).
- [X] T037 [P] [US2] Test intégration `backend/tests/integration/test_admin_geodata.py::test_delete_active_version_returns_409`.
- [X] T038 [P] [US2] Test intégration `backend/tests/integration/test_admin_geodata.py::test_delete_inactive_version_succeeds_204`.
- [X] T039 [P] [US2] Test intégration `backend/tests/integration/test_admin_geodata.py::test_lru_purge_keeps_active_evicts_oldest_inactive_when_quota_reached` (créer 51 versions, vérifier 50 restantes, l'active n'est jamais évincée).

### Backend US2

- [X] T040 [US2] Étendre `backend/app/routers/admin_geodata.py` :
  - `GET /api/admin/geodata/regions/versions?limit=&offset=` → `list_versions` + retour `{items, total}`.
  - `GET /api/admin/geodata/regions/versions/{id}` → `get_version` + retour `VersionDetail` (incluant `geojson_processed` pour preview).
  - `DELETE /api/admin/geodata/regions/versions/{id}` → `delete_version` + `record_geodata_deleted` + 204 ; lever 409 si active.

### Frontend US2

- [X] T041 [P] [US2] Compléter `frontend/app/composables/useGeodataAdmin.ts` avec `listVersions(limit, offset)`, `getVersion(id)` (preview), `deleteVersion(id)`.
- [X] T042 [P] [US2] Composant `frontend/app/components/geodata/VersionTable.vue` :
  - colonnes : date, auteur (email), taille traitée, nb régions, statut (badge active/inactive), warnings (badge si > 0), actions (Prévisualiser, Activer, Supprimer).
  - Désactiver Supprimer pour la version active.
  - Pagination (limit 20).
- [X] T043 [P] [US2] Composant `frontend/app/components/geodata/PreviewVersionModal.vue` :
  - Mini-carte amCharts, init au mount, geoJSON injecté depuis `getVersion(id).geojson_processed`.
  - Liste des `region_names` à droite ; warnings au-dessus.
- [X] T044 [US2] Intégrer `VersionTable` + `PreviewVersionModal` dans `frontend/app/pages/admin/geodata/regions/index.vue` ; brancher boutons Prévisualiser, Activer (réutilise `ActivateVersionModal`), Supprimer (avec confirmation native).

**Checkpoint US2** : rollback en < 5 s opérationnel, suppression bloquée sur l'active, quota 50 respecté.

---

## Phase 5: User Story 3 — Refus des fichiers invalides (Priority: P2)

**Goal**: bloquer extension/MIME/taille incorrectes, GeoJSON malformé, GeoJSON sans features régionales, propriétés HTML/JS, et appliquer le rate limit.

**Independent Test**: soumettre chacun des cas invalides à `POST /upload` et vérifier code retour + absence de version créée.

### Tests pour US3

- [X] T045 [P] [US3] Test intégration `backend/tests/integration/test_admin_geodata.py::test_reject_csv_extension_returns_400`.
- [X] T046 [P] [US3] Test intégration `backend/tests/integration/test_admin_geodata.py::test_reject_xml_content_returns_400`.
- [X] T047 [P] [US3] Test intégration `backend/tests/integration/test_admin_geodata.py::test_reject_geojson_without_admin_level_4_features_returns_400`.
- [X] T048 [P] [US3] Test intégration `backend/tests/integration/test_admin_geodata.py::test_reject_file_over_50mb_returns_413`.
- [X] T049 [P] [US3] Test intégration `backend/tests/integration/test_admin_geodata.py::test_strips_html_js_properties_keeps_only_allowed_keys`.
- [ ] T050 [P] [US3] Test intégration `backend/tests/integration/test_admin_geodata.py::test_rate_limit_blocks_11th_upload_within_hour_returns_429`. (Reporté : risque de pollution du compteur slowapi inter-tests, à traiter avec un fixture de reset dédié.)
- [X] T051 [P] [US3] Test intégration `backend/tests/integration/test_admin_geodata.py::test_editor_role_cannot_access_admin_geodata_returns_403` (clarification Q1).

### Backend US3

- [X] T052 [US3] Renforcer la validation entrée dans `backend/app/routers/admin_geodata.py::upload` :
  - Refuser extension si pas dans `{".geojson", ".json"}` → 400 `ErrorResponse{code:"INVALID_EXTENSION"}`.
  - Refuser MIME si pas dans `{"application/json", "application/geo+json", "text/json"}` → 400.
  - Refuser `Content-Length > GEODATA_MAX_UPLOAD_BYTES` → 413.
  - En cas de pipeline échouant pour `FeatureCollection` invalide ou 0 feature exploitable : raise `HTTPException(400, code="NO_FEATURES")`.
- [X] T053 [US3] Appliquer `slowapi` rate limit `@limiter.limit("10/hour")` sur `POST /upload` (clé : `actor_user_id`). Configurer `GEODATA_RATE_LIMIT_UPLOADS_PER_HOUR` comme paramètre.
- [X] T054 [US3] Vérifier que la sanitization des properties dans `backend/app/services/geodata_pipeline.py::sanitize_properties` est l'avant-dernière étape avant `round_coordinates` ; ajouter un test couvrant `<script>`, balises HTML, champs métier inconnus.

### Frontend US3

- [X] T055 [P] [US3] Dans `frontend/app/components/geodata/UploadVersionModal.vue`, afficher les messages d'erreur backend (`detail`) sous forme de toast/notification non bloquante. Ne pas vider le formulaire pour permettre correction.
- [X] T056 [P] [US3] Côté frontend, refuser drop si extension `.csv`/`.xml`/etc. avant l'envoi (validation client préventive — n'absout pas la validation serveur), dans `frontend/app/components/geodata/UploadVersionModal.vue`.

**Checkpoint US3** : 100 % des cas invalides retournent une erreur explicite, aucun écrit en base.

---

## Phase 6: User Story 4 — Détection des écarts BDD + comportement carte (Priority: P3)

**Goal**: avertir l'admin quand le GeoJSON contient des régions sans correspondance en table `regions`, et afficher ces régions en gris (« Données non disponibles ») sur la carte d'accueil.

**Independent Test**: uploader un GeoJSON contenant une région fictive `Foobar` ; vérifier (a) le warning `REGION_NOT_IN_DATABASE` côté admin ; (b) la carte d'accueil affiche `Foobar` en gris avec tooltip dédié.

### Tests pour US4

- [X] T057 [P] [US4] Test intégration `backend/tests/integration/test_admin_geodata.py::test_pipeline_emits_region_not_in_database_warning_for_unknown_region`.
- [X] T058 [P] [US4] Test intégration `backend/tests/integration/test_admin_geodata.py::test_pipeline_emits_feature_count_out_of_range_when_outside_20_30`.
- [ ] T059 [P] [US4] Test E2E Playwright `frontend/tests/e2e/home-map-unknown-region.spec.ts` : seed en base sans `Vatovavy`, mais le GeoJSON l'inclut → tooltip « Données non disponibles » + clic désactivé. (Reporté : aucune config Playwright n'existe encore dans `frontend/`.)

### Backend US4

- [X] T060 [US4] Étendre `backend/app/services/geodata_pipeline.py::run_pipeline` pour, après normalisation, comparer les `name` finaux à `SELECT lower(name) FROM regions` (passé en argument résolu une fois côté `backend/app/services/geodata_service.py`) ; pour chaque non-match, ajouter un warning `REGION_NOT_IN_DATABASE`.

### Frontend US4

- [X] T061 [US4] Dans `frontend/app/components/MadagascarMap.vue`, lors du binding région↔BDD :
  - Si `properties.name` (normalisé) n'a pas de match dans `useGeography().regions`, appliquer la classe/couleur grisée neutre (param Tailwind dark/light), désactiver `cursor-pointer`, désactiver le clic, afficher tooltip « Données non disponibles » (string localisée FR — fallback EN si absent).
  - Implémentation FR-029 (cf. spec.md §Functional Requirements).

**Checkpoint US4** : la carte tolère les écarts entre GeoJSON et BDD sans plantage et sans navigation orpheline.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T062 [P] E2E Playwright `frontend/tests/e2e/geodata-admin.spec.ts` : login admin → upload (avec petit GeoJSON fixture) → activation → recharge home → présence du nom de région attendu dans le DOM/tooltip.
- [ ] T063 [P] Tester non-régression : la carte d'accueil charge en < 2 s sur profil 3G simulé (Lighthouse / Playwright trace) ; payload < 1 Mo (assertion sur taille du body) — script de mesure `frontend/tests/e2e/home-map-perf.spec.ts`.
- [X] T064 [P] Ajouter une assertion `wc -l frontend/app/components/MadagascarMap.vue < 320` dans la suite de tests ou un script de garde CI `scripts/check_madagascar_map_size.sh`.
- [X] T065 [P] Documenter la procédure d'export Overpass + upload + rollback dans `docs/admin/geodata-management.md` (cible : guide admin non-tech).
- [ ] T066 [P] Mettre à jour `backend/README.md` et `frontend/README.md` avec mention de la nouvelle dépendance et de la nouvelle route admin (mention concise).
- [ ] T067 Lancer `ruff check backend/ --fix` et `pnpm lint` (frontend) ; corriger les warnings introduits.
- [ ] T068 Confirmer la couverture de tests ≥ 80 % sur `backend/app/services/geodata_*` et `backend/app/routers/admin_geodata.py` (`pytest --cov`).
- [ ] T069 Lancer l'agent `code-reviewer` sur le diff complet de la branche, traiter CRITICAL/HIGH avant merge.
- [ ] T070 Vérifier que le bundle frontend n'a pas grossi de plus de 50 Ko (`pnpm build` ; comparer `Output | gzip` aux mesures de la branche `main`).

---

## Dependencies & Story Completion Order

```text
Phase 1 (Setup)
   ↓
Phase 2 (Foundational) — bloque toutes les stories
   ↓
Phase 3 (US1, P1, MVP) ── livrable indépendamment
   ↓
Phase 4 (US2, P2)   ─┐
Phase 5 (US3, P2)   ─┤── parallélisables entre elles
Phase 6 (US4, P3)   ─┘
   ↓
Phase 7 (Polish)
```

**Inter-story constraints** :
- US2 dépend de US1 (réutilise `useGeodataAdmin`, `ActivateVersionModal`, page admin).
- US3 dépend de US1 (durcit le endpoint upload existant).
- US4 dépend de US1 (modifie `MadagascarMap.vue` créé en US1) ET de US2 indirectement (les warnings sont visibles dans le tableau des versions).

---

## Parallel Execution Examples

**Phase 1** : après T001, T002/T003/T004/T005 sont parallélisables [P].

**Phase 2** : après T010 (migration appliquée), T011/T012/T013/T015 sont indépendants [P]. T014 nécessite T006+T011.

**Phase 3 — tests US1** (T017-T025) tous parallélisables [P].

**Phase 3 — frontend US1** : T029/T031/T032 indépendants [P]. T030 dépend de T029. T033 indépendant. T034 indépendant des autres (autre fichier).

**Phase 4** : tests T035-T039 [P] ; backend T040 unique ; frontend T041/T042/T043 [P], T044 dépend de T041-T043.

**Phase 5** : tests T045-T051 [P] ; backend T052/T053/T054 séquentiels (modifient le même router/pipeline) ; frontend T055/T056 [P].

**Phase 6** : tests T057-T059 [P] ; backend T060 unique ; frontend T061 unique.

**Phase 7** : T062 à T066 tous [P] ; T067/T068/T069/T070 séquentiels.

---

## Implementation Strategy — MVP first

1. **MVP minimal** : Phase 1 + Phase 2 + Phase 3 (US1) → livre la valeur centrale (publier une nouvelle géographie).
2. **Itération 2** : Phase 4 (US2) → débloque rollback opérationnel.
3. **Itération 3** : Phase 5 (US3) → durcit la sécurité (rate limit, sanitization, refus formats invalides).
4. **Itération 4** : Phase 6 (US4) → améliore l'expérience visiteur sur les régions non rapprochées en BDD.
5. **Avant merge final** : Phase 7 (Polish) — peut courir en parallèle de la dernière itération.

---

## Validation finale (à exécuter avant `/speckit.implement`)

- [ ] Toutes les tâches respectent le format `- [ ] TID [P?] [Story?] description avec chemin de fichier`.
- [ ] Chaque user story du spec est couverte par au moins une phase complète (US1/US2/US3/US4 → Phase 3/4/5/6).
- [ ] Chaque entité et endpoint des contracts a au moins une tâche backend correspondante.
- [ ] Le seed initial (T005 + T009) est cohérent avec FR-021.
- [ ] Les invariants INV-1 à INV-5 (data-model.md) sont chacun couverts par au moins un test.
