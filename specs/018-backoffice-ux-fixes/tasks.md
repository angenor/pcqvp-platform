---
description: "Task list — Correctifs UX back-office (lot 018)"
---

# Tasks: Correctifs UX back-office (lot 018)

**Input**: Design documents from `/specs/018-backoffice-ux-fixes/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Tests**: inclus pour les endpoints backend (standards projet CLAUDE.md — pytest + pytest-asyncio, coverage ≥ 80 %). Pas de framework de test frontend en place → validation manuelle via quickstart.md.
**Organization**: regroupés par user story ; chaque story est livrable et testable de façon indépendante.

## Format: `[ID] [P?] [Story] Description`

- **[P]** : exécutable en parallèle (fichier distinct, aucune dépendance sur une tâche non terminée)
- **[Story]** : US1 / US2 / US3 / US4 ; absent sur Setup, Foundational et Polish
- Chaque tâche cite un chemin de fichier exact

## Path Conventions

- Backend : `backend/app/...` et `backend/tests/...`
- Frontend : `frontend/app/...`
- Types partagés : `packages/shared/src/...`
- Migrations : `backend/alembic/versions/...`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: vérifier que l'environnement local est prêt à recevoir les modifications. Projet déjà initialisé, rien à bootstrapper.

- [X] T001 Vérifier que PostgreSQL dev (`docker compose up -d`), backend venv (`pip install -e ".[dev]"`, `alembic upgrade head`) et frontend (`pnpm install`) sont à jour à la racine du repo

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: aucune infrastructure partagée nouvelle à construire avant les user stories — chaque story apporte sa propre migration et ses propres modèles pour préserver l'indépendance de livraison. On établit simplement le filet de sécurité.

**⚠️ CRITICAL**: aucun travail user story ne commence tant que cette phase n'est pas validée

- [X] T002 Exécuter `pytest` à la racine de `backend/` pour établir la baseline verte (aucune régression préalable) et noter la durée de référence

**Checkpoint**: baseline validée → les quatre stories peuvent démarrer en parallèle

---

## Phase 3: User Story 1 — Rétablir l'insertion d'images dans l'éditeur éditorial (Priority: P1) 🎯 MVP

**Goal**: rétablir l'upload + insertion d'image dans le corps des pages éditoriales (EditorJS) selon le diagnostic R1 (propagation auth / liste MIME / config plugin).

**Independent Test**: se connecter en `editor`, ouvrir une page éditoriale, insérer une image PNG/JPG valide dans le corps de page, sauvegarder, vérifier le rendu public. Voir quickstart.md § US1.

### Tests for User Story 1

- [X] T003 [P] [US1] Test d'intégration backend : upload image via multipart (champ `image`) avec Bearer valide renvoie 200 + payload `{success:1, file:{url}}` dans `backend/tests/test_editor_image_upload.py`
- [X] T004 [P] [US1] Test d'intégration backend : upload image sans Bearer renvoie 401, MIME refusé renvoie 415, fichier > 5 Mo renvoie 413 dans `backend/tests/test_editor_image_upload.py`

### Implementation for User Story 1

- [X] T005 [US1] Reproduire le bug en local (devtools réseau + logs `uvicorn`) sur `frontend/app/pages/admin/editorial.vue`, capturer : code HTTP, headers envoyés par `@editorjs/image`, champ de formulaire, MIME détecté
- [X] T006 [US1] Selon le diagnostic, appliquer le correctif **minimal** dans `frontend/app/components/RichContentEditor.vue` (config `additionalRequestHeaders` recalculée à chaque requête, ou fallback `uploader` custom) et/ou dans `backend/app/routers/upload.py` (`ALLOWED_IMAGE_TYPES` si MIME légitime rejeté)
- [X] T007 [US1] Vérifier que le rendu public (`frontend/app/components/RichContentRenderer.vue`) affiche correctement les images insérées (pas de CSS cassé, responsive, alt)
- [X] T008 [US1] Ajouter un message d'erreur utilisateur clair dans `RichContentEditor.vue` lorsque l'upload échoue (toast + preservation du contenu existant)

**Checkpoint**: US1 complète → MVP. Insertion d'image fonctionnelle de bout en bout, tests backend verts.

---

## Phase 4: User Story 2 — Supprimer un compte administratif depuis la liste (Priority: P2)

**Goal**: exposer un DELETE sécurisé, journalisé, bloqué si le compte est publié, avec action Supprimer dans la liste back-office.

**Independent Test**: se connecter en `admin`, depuis la liste des comptes, supprimer un compte en brouillon, vérifier sa disparition + entrée dans `audit_logs`. Tester qu'un compte publié est refusé avec le message prévu. Voir quickstart.md § US2.

### Tests for User Story 2

- [X] T009 [P] [US2] Test contract : `DELETE /api/admin/comptes/{id}` avec rôle `admin` sur compte `draft` renvoie 204, ligne retirée de la DB dans `backend/tests/test_admin_comptes_delete.py`
- [X] T010 [P] [US2] Test contract : même endpoint sur compte `published` renvoie 409 avec payload `CompteStillPublishedError`, compte conservé intact dans `backend/tests/test_admin_comptes_delete.py`
- [X] T011 [P] [US2] Test contract : rôle `editor` sur l'endpoint renvoie 403 dans `backend/tests/test_admin_comptes_delete.py`
- [X] T012 [P] [US2] Test d'intégration : après suppression, une entrée `compte_administratif.deleted` est présente dans `audit_logs` avec `actor_user_id`, `target_id`, et snapshot JSON non vide dans `backend/tests/test_admin_comptes_delete.py`

### Implementation for User Story 2

- [X] T013 [P] [US2] Créer la migration Alembic `backend/alembic/versions/NNN_add_audit_logs.py` qui crée la table `audit_logs` (colonnes + index `ix_audit_logs_action_created`, `ix_audit_logs_actor_created` selon data-model.md)
- [X] T014 [P] [US2] Créer le modèle SQLAlchemy `AuditLog` dans `backend/app/models/audit_log.py` (hérite de `UUIDBase`, FK `actor_user_id` avec `ondelete=RESTRICT`)
- [X] T015 [US2] Créer le service `backend/app/services/audit_log.py` avec `async def record_compte_deletion(db, actor, compte) -> None` (snapshot JSON + insert) — dépend de T014
- [X] T016 [US2] Ajouter l'endpoint `DELETE /api/admin/comptes/{compte_id}` dans `backend/app/routers/admin_comptes.py` : dépendance `require_role("admin")`, retourne 409 `CompteStillPublishedError` si `status == "published"`, sinon transaction `record_compte_deletion` + `db.delete(compte)` (cascade automatique sur enfants) — dépend de T015
- [X] T017 [US2] Ajouter la méthode `deleteCompte(id: string): Promise<void>` dans `frontend/app/composables/useComptes.ts` via `useApi`
- [X] T018 [US2] Ajouter la colonne/action « Supprimer » dans `frontend/app/components/AccountTable.vue` : visible uniquement pour l'`admin` (via `useAuth`), ouvre un modal `ConfirmDeleteCompteModal` ; si l'API renvoie 409, afficher le message de blocage + bouton « Repasser en brouillon » qui appelle l'endpoint `PUT /status` existant
- [X] T019 [US2] Créer `frontend/app/components/ConfirmDeleteCompteModal.vue` avec classes Tailwind `dark:`, textes français, traitement des deux cas (confirmation simple vs blocage publié)
- [X] T020 [US2] Câbler l'action Supprimer dans `frontend/app/pages/admin/accounts/index.vue` (passe l'événement au composable, refresh la liste après 204, toast succès/erreur)

**Checkpoint**: US2 complète → suppression fonctionnelle, audit vérifiable, UI conforme au rôle. Indépendant de US1 / US3 / US4.

---

## Phase 5: User Story 3 — Documents officiels des collectivités (Priority: P2)

**Goal**: section « Documents officiels » en back-office (upload + réordo + remplacer + supprimer) pour Province / Région / Commune, rendu public sous la bannière avec titre + icône type + taille + date.

**Independent Test**: attacher deux documents à une commune, réordonner, remplacer le premier, supprimer le second, vérifier page publique conforme. Voir quickstart.md § US3.

### Tests for User Story 3

- [X] T021 [P] [US3] Test contract : `POST /api/admin/upload/document` avec PDF valide renvoie 200 + `{success:1, file:{url,name,size,mime}}`, fichier > 20 Mo renvoie 413, MIME non listé renvoie 415, sans Bearer renvoie 401 dans `backend/tests/test_upload_document.py`
- [X] T022 [P] [US3] Test contract : `POST /api/admin/collectivity-documents` avec parent province valide crée une ligne + FK exclusive respectée, titre vide renvoie 400, MIME non listé renvoie 400 dans `backend/tests/test_collectivity_documents.py`
- [X] T023 [P] [US3] Test contract : `GET /api/admin/collectivity-documents?parent_type=commune&parent_id=...` renvoie les documents dans l'ordre `position` dans `backend/tests/test_collectivity_documents.py`
- [X] T024 [P] [US3] Test contract : `PUT /api/admin/collectivity-documents/{id}/file` remplace `file_path`, `file_mime`, `file_size_bytes` et met à jour `updated_at`, ancien fichier supprimé du disque dans `backend/tests/test_collectivity_documents.py`
- [X] T025 [P] [US3] Test contract : `PATCH /api/admin/collectivity-documents/reorder` réordonne correctement, liste incomplète renvoie 400, ID étranger renvoie 400 dans `backend/tests/test_collectivity_documents.py`
- [X] T026 [P] [US3] Test contract : `DELETE /api/admin/collectivity-documents/{id}` renvoie 204, ligne retirée, fichier disque supprimé dans `backend/tests/test_collectivity_documents.py`
- [X] T027 [P] [US3] Test d'intégration : contrainte CHECK `parent_exclusive` refuse une insertion avec deux FK non nulles (SQLAlchemy/asyncpg) dans `backend/tests/test_collectivity_documents.py`
- [X] T028 [P] [US3] Test d'intégration : suppression cascade d'une commune supprime ses `collectivity_documents` dans `backend/tests/test_collectivity_documents.py`
- [X] T029 [P] [US3] Test d'intégration : le payload public d'une collectivité (`GET /api/geography/communes/{id}`) inclut la liste des documents dans l'ordre `position` dans `backend/tests/test_public_geography_documents.py`

### Implementation for User Story 3

- [X] T030 [P] [US3] Créer la migration Alembic `backend/alembic/versions/NNN_add_collectivity_documents.py` qui crée la table `collectivity_documents` avec contrainte CHECK `parent_exclusive` + 3 index partiels `(parent_id, position)` selon data-model.md
- [X] T031 [P] [US3] Créer le modèle `CollectivityDocument` dans `backend/app/models/collectivity_document.py` (hérite de `UUIDBase`, 3 FK nullables avec `ondelete=CASCADE`, relations `selectin` vers Province/Region/Commune, `@validates` pour contrainte d'exclusivité côté ORM)
- [X] T032 [P] [US3] Créer les schémas Pydantic dans `backend/app/schemas/collectivity_document.py` : `CollectivityDocumentCreate`, `CollectivityDocumentUpdate`, `CollectivityDocumentRead` (avec `parent_type`/`parent_id` dérivés + `download_url`), `CollectivityDocumentsReorder`
- [X] T033 [US3] Ajouter l'endpoint `POST /api/admin/upload/document` dans `backend/app/routers/upload.py` : constantes `MAX_DOCUMENT_SIZE = 20*1024*1024` et `ALLOWED_DOCUMENT_TYPES`, réponse `{success:1, file:{url,name,size,mime}}`, stockage sous `uploads/documents/` — dépend de T001
- [X] T034 [US3] Créer le routeur `backend/app/routers/admin_collectivity_documents.py` : GET list, POST create, PUT update (titre), PUT replace file, PATCH reorder, DELETE, toutes protégées par `require_role("admin","editor")` — dépend de T031, T032
- [X] T035 [US3] Enregistrer le routeur dans `backend/app/main.py` (import + `app.include_router(...)`) — dépend de T034
- [X] T036 [US3] Étendre `backend/app/routers/public_geography.py` (schémas de réponse + jointure `selectin`) pour exposer les documents dans le payload de Province / Region / Commune, triés par `position` — dépend de T031
- [X] T037 [P] [US3] Ajouter le type partagé `CollectivityDocument` dans `packages/shared/src/collectivity.ts` (interface TS conforme à data-model.md)
- [X] T038 [P] [US3] Créer le composable `frontend/app/composables/useCollectivityDocuments.ts` qui encapsule via `useApi` les opérations list / create / update / replaceFile / reorder / delete et un helper `uploadDocumentFile(file)`
- [X] T039 [US3] Créer le composant réutilisable `frontend/app/components/CollectivityDocumentsEditor.vue` : zone d'upload, liste avec titre + icône type + taille + date, actions Remplacer / Renommer / Supprimer, drag & drop réordo, classes Tailwind `dark:`, i18n français — dépend de T037, T038
- [X] T040 [US3] Intégrer `CollectivityDocumentsEditor` dans `frontend/app/pages/admin/geography/provinces/[id].vue` immédiatement après la bannière et avant la description riche — dépend de T039
- [X] T041 [US3] Intégrer `CollectivityDocumentsEditor` dans `frontend/app/pages/admin/geography/regions/[id].vue` au même emplacement — dépend de T039
- [X] T042 [US3] Intégrer `CollectivityDocumentsEditor` dans `frontend/app/pages/admin/geography/communes/[id].vue` au même emplacement — dépend de T039
- [X] T043 [US3] Créer le composant d'affichage public `frontend/app/components/CollectivityDocumentsList.vue` : titre (lien de téléchargement) + icône FontAwesome selon MIME + taille formatée (`formatBytes` helper) + date `DD/MM/YYYY`, état vide = section masquée, classes Tailwind `dark:`
- [X] T044 [US3] Intégrer `CollectivityDocumentsList` dans `frontend/app/pages/provinces/[id].vue` juste après la bannière — dépend de T043
- [X] T045 [US3] Intégrer `CollectivityDocumentsList` dans `frontend/app/pages/regions/[id].vue` au même emplacement — dépend de T043
- [X] T046 [US3] Intégrer `CollectivityDocumentsList` dans `frontend/app/pages/communes/[id].vue` au même emplacement — dépend de T043

**Checkpoint**: US3 complète → documents opérationnels côté admin et affichés côté public pour les trois niveaux de collectivité. Indépendant de US1 / US2 / US4.

---

## Phase 6: User Story 4 — Raccourcis comptes depuis la liste des communes (Priority: P3)

**Goal**: deux actions par ligne dans la liste des communes — « Voir les comptes » et « Soumettre un compte » — reliant en un clic la liste filtrée et le formulaire pré-rempli.

**Independent Test**: depuis la liste des communes back-office, cliquer chacun des deux raccourcis et vérifier la redirection + pré-remplissage. Voir quickstart.md § US4.

### Implementation for User Story 4

Pas de test automatisé : validation exclusivement via les scénarios manuels de quickstart.md, car aucun endpoint n'est modifié (les query params `collectivite_type` / `collectivite_id` sont déjà supportés par `admin/accounts/index.vue` et `admin/accounts/new.vue`).

- [X] T047 [US4] Ajouter deux actions par ligne dans `frontend/app/pages/admin/geography/communes/index.vue` : « Voir les comptes » → `/admin/accounts?collectivite_type=commune&collectivite_id={id}` ; « Soumettre un compte » → `/admin/accounts/new?collectivite_type=commune&collectivite_id={id}`. Icônes FontAwesome, classes Tailwind `dark:`, accessibilité (aria-label)
- [X] T048 [US4] Vérifier sur `frontend/app/pages/admin/accounts/index.vue` que le filtre pré-rempli affiche correctement un état vide explicite (« Aucun compte pour cette commune — Soumettre un compte ») si le résultat est vide — modification UX mineure si nécessaire
- [X] T049 [US4] Vérifier sur `frontend/app/pages/admin/accounts/new.vue` que le sélecteur de commune est bien pré-rempli (et visuellement marqué) quand les query params sont présents ; ajuster si l'ergonomie actuelle laisse la commune modifiable par inadvertance

**Checkpoint**: US4 complète → navigation directe opérationnelle. Aucun endpoint backend modifié.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: finalisation, validation globale et conformité projet avant livraison.

- [X] T050 [P] Passer `ruff check backend/ --fix` et corriger les éventuels warnings introduits
- [X] T051 [P] Vérifier manuellement que tous les nouveaux écrans (Editeur, modals, sections documents, raccourcis) respectent dark / light mode (pas de contraste cassé, pas de classe oubliée)
- [X] T052 [P] Mettre à jour `backend/README.md` avec les nouveaux endpoints `/api/admin/upload/document`, `/api/admin/collectivity-documents/*`, `DELETE /api/admin/comptes/{id}` (section « Endpoints »)
- [X] T053 [P] Relire `specs/018-backoffice-ux-fixes/quickstart.md` et synchroniser avec les chemins UI réels livrés
- [ ] T054 Exécuter la suite `pytest` complète depuis `backend/` : tout vert, coverage ≥ 80 % sur les nouveaux fichiers (`audit_log.py`, `collectivity_document.py`, `admin_collectivity_documents.py`, extensions `upload.py` et `admin_comptes.py`)
- [ ] T055 Exécuter la checklist de validation manuelle `specs/018-backoffice-ux-fixes/quickstart.md` de bout en bout sur un environnement local (US1 → US4 + checks transverses)
- [ ] T056 Préparer le commit / PR final avec message `feat(018): back-office UX fixes (editor image, compte delete, collectivity documents, commune shortcuts)` (hors scope automatique — attendre confirmation utilisateur avant de committer)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup** : aucune dépendance, démarre immédiatement
- **Phase 2 Foundational** : dépend de Phase 1, **bloque toutes les user stories**
- **Phases 3-6 (US1-US4)** : dépendent de Phase 2 ; peuvent s'exécuter **en parallèle** (si équipe suffisante)
- **Phase 7 Polish** : dépend des user stories retenues pour la livraison

### User Story Dependencies

- **US1 (P1)** : indépendante — corrige un bug existant, ne touche pas aux nouvelles tables
- **US2 (P2)** : indépendante de US1, US3, US4 — apporte sa propre migration (`audit_logs`) et son modèle
- **US3 (P2)** : indépendante de US1, US2, US4 — apporte sa propre migration (`collectivity_documents`) et ses propres modèles
- **US4 (P3)** : indépendante, purement UI frontend — s'appuie sur des endpoints déjà présents

### Within Each User Story

- Tests écrits **avant** l'implémentation (workflow TDD du projet)
- Modèles avant services
- Services avant routes
- Backend avant frontend
- Composable frontend avant composant qui l'utilise

### Parallel Opportunities

- Après T002 (baseline), les quatre user stories peuvent démarrer en parallèle si la capacité équipe le permet
- Dans US2 : T013 (migration), T014 (modèle), T009-T012 (tests) peuvent se développer en parallèle
- Dans US3 : T021 → T029 (tests) + T030 (migration) + T031 (modèle) + T032 (schémas) + T037 (type partagé) peuvent démarrer ensemble ; les intégrations pages admin T040/T041/T042 et pages publiques T044/T045/T046 sont parallèles entre elles une fois les composants T039 et T043 prêts
- Polish : T050-T053 sont parallèles entre eux

---

## Parallel Example: User Story 3 (démarrage)

```bash
# Après T002 baseline, kick-off US3 en parallèle :

# Tests en parallèle (fichiers distincts) :
Task: "T021 Tests upload document → backend/tests/test_upload_document.py"
Task: "T022-T026 Tests CRUD documents → backend/tests/test_collectivity_documents.py"
Task: "T029 Tests payload public → backend/tests/test_public_geography_documents.py"

# Infra en parallèle :
Task: "T030 Migration Alembic collectivity_documents"
Task: "T031 Modèle SQLAlchemy CollectivityDocument"
Task: "T032 Schémas Pydantic"
Task: "T037 Type partagé TypeScript"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only — le bug bloquant)

1. Phase 1 Setup (T001)
2. Phase 2 Foundational (T002 baseline verte)
3. Phase 3 US1 : T003-T008
4. **STOP, valider en local via quickstart § US1**
5. Déploiement MVP possible immédiatement — l'éditeur éditorial est à nouveau fonctionnel

### Incremental Delivery (livraison recommandée)

1. Setup + Foundational
2. US1 → validation → **déploiement MVP** (correctif critique)
3. US2 → validation → déploiement (admins peuvent nettoyer les comptes)
4. US3 → validation → déploiement (nouvelle fonctionnalité documents)
5. US4 → validation → déploiement (gain UX)
6. Phase 7 Polish une fois toutes les stories retenues livrées

Chaque palier apporte de la valeur sans casser le précédent.

### Parallel Team Strategy (si capacité équipe disponible)

Après T002 :
- Dev A : US1 (court — ~½ journée selon diagnostic)
- Dev B : US2 (backend + UI modale — ~1-2 jours)
- Dev C : US3 (plus volumineux — ~3-4 jours, peut être scindé en backend + frontend)
- Dev D : US4 (UI frontend uniquement — ~½ journée)

Toutes les stories convergent vers la phase 7 pour le run quickstart et les finitions.

---

## Notes

- `[P]` = fichier distinct, aucune dépendance bloquante sur une tâche non terminée
- `[Story]` = traçabilité vers spec.md ; absent sur Setup, Foundational, Polish
- Chaque story est indépendamment complétable et livrable
- Écrire les tests avant l'implémentation (RED → GREEN → REFACTOR)
- Commit après chaque tâche ou groupe logique (respecter la règle « nouveau commit plutôt qu'amend »)
- Vérifier le mode sombre / clair à chaque écran touché (`dark:` Tailwind)
- Respecter les rôles `admin` / `editor` conformément à la spec (FR-015, R7)
- Le commit final (T056) attend validation utilisateur avant exécution
