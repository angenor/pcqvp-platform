# Tasks: Section Éditoriaux du Backoffice

**Input**: Design documents from `/specs/015-backoffice-editorials/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md

**Tests**: Non demandés explicitement — tests exclus.

**Organization**: Tasks groupées par user story pour permettre l'implémentation et le test indépendants de chaque story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Peut s'exécuter en parallèle (fichiers différents, pas de dépendances)
- **[Story]**: User story concernée (US1, US2, US3)
- Chemins exacts inclus dans les descriptions

---

## Phase 1: Setup

**Purpose**: Création des types partagés et migration de la base de données

- [X] T001 [P] Créer les types TypeScript partagés dans packages/shared/types/editorial.ts
- [X] T002 [P] Créer la migration Alembic pour les tables editorial_contents, contact_info, resource_links dans backend/alembic/versions/006_create_editorial_tables.py

---

## Phase 2: Foundational (Prérequis bloquants)

**Purpose**: Infrastructure commune nécessaire à TOUTES les user stories

**⚠️ CRITICAL**: Aucune user story ne peut commencer avant la complétion de cette phase

- [X] T003 Créer les modèles SQLAlchemy EditorialContent, ContactInfo, ResourceLink dans backend/app/models/editorial.py
- [X] T004 [P] Créer les schémas Pydantic (HeroUpdate, BodyUpdate, FooterAboutUpdate, ContactInfoUpdate, ContactInfoResponse, ResourceLinkCreate, ResourceLinkUpdate, ResourceLinkResponse, EditorialPublicResponse, EditorialAdminResponse) dans backend/app/schemas/editorial.py
- [X] T005 [P] Créer le squelette du service éditorial avec les fonctions utilitaires de base (get_or_create_content, get_or_create_contact) dans backend/app/services/editorial.py
- [X] T006 [P] Créer le router admin éditorial (squelette avec GET /api/admin/editorial) dans backend/app/routers/admin_editorial.py
- [X] T007 [P] Créer le router public éditorial (GET /api/editorial) dans backend/app/routers/public_editorial.py
- [X] T008 Enregistrer les routers admin_editorial et public_editorial dans backend/app/main.py
- [X] T009 [P] Créer le composable useEditorial avec les fonctions fetchEditorial, fetchAdminEditorial dans frontend/app/composables/useEditorial.ts
- [X] T010 [P] Ajouter l'entrée menu "Éditoriaux" dans le groupe "Outils" du sidebar dans frontend/app/components/admin/AdminSidebar.vue
- [X] T011 Créer la page admin éditorial avec le squelette des 3 onglets (Hero Section, Corps de page, Footer) dans frontend/app/pages/admin/editorial.vue

**Checkpoint**: Infrastructure prête — l'implémentation des user stories peut commencer

---

## Phase 3: User Story 1 — Gestion de la Hero Section (Priority: P1) 🎯 MVP

**Goal**: Permettre aux admins de modifier le titre, sous-titre et description de la hero section de la page d'accueil

**Independent Test**: Modifier les 3 champs dans le backoffice, vérifier l'affichage sur la page d'accueil publique

### Implementation for User Story 1

- [X] T012 [US1] Implémenter les fonctions service get_hero() et update_hero() dans backend/app/services/editorial.py
- [X] T013 [US1] Implémenter l'endpoint PUT /api/admin/editorial/hero avec validation (titre non vide) dans backend/app/routers/admin_editorial.py
- [X] T014 [US1] Ajouter les données hero à la réponse GET /api/admin/editorial dans backend/app/routers/admin_editorial.py
- [X] T015 [US1] Ajouter les données hero à la réponse GET /api/editorial dans backend/app/routers/public_editorial.py
- [X] T016 [US1] Ajouter les fonctions updateHero() et les types hero au composable dans frontend/app/composables/useEditorial.ts
- [X] T017 [US1] Implémenter le formulaire de l'onglet "Hero Section" (3 champs texte + bouton Enregistrer + feedback) dans frontend/app/pages/admin/editorial.vue
- [X] T018 [US1] Modifier la page d'accueil pour charger dynamiquement le titre, sous-titre et description de la hero section depuis l'API dans frontend/app/pages/index.vue

**Checkpoint**: La hero section est entièrement gérable depuis le backoffice et s'affiche dynamiquement

---

## Phase 4: User Story 2 — Gestion du contenu riche du corps de page (Priority: P1)

**Goal**: Permettre aux admins d'insérer du contenu riche (titres, textes, images, tableaux, citations, liens) dans le corps de la page d'accueil

**Independent Test**: Créer du contenu riche dans l'éditeur, vérifier le rendu fidèle sur la page d'accueil

### Implementation for User Story 2

- [X] T019 [US2] Implémenter les fonctions service get_body() et update_body() dans backend/app/services/editorial.py
- [X] T020 [US2] Implémenter l'endpoint PUT /api/admin/editorial/body avec validation EditorJSData dans backend/app/routers/admin_editorial.py
- [X] T021 [US2] Ajouter les données body à la réponse GET /api/admin/editorial dans backend/app/routers/admin_editorial.py
- [X] T022 [US2] Ajouter les données body à la réponse GET /api/editorial dans backend/app/routers/public_editorial.py
- [X] T023 [US2] Ajouter la fonction updateBody() au composable dans frontend/app/composables/useEditorial.ts
- [X] T024 [US2] Implémenter l'onglet "Corps de page" avec RichContentEditor (v-model, ClientOnly, sauvegarde) dans frontend/app/pages/admin/editorial.vue
- [X] T025 [US2] Ajouter la section de présentation contextuelle avec RichContentRenderer sur la page d'accueil dans frontend/app/pages/index.vue

**Checkpoint**: Le contenu riche est éditable et affiché fidèlement sur la page d'accueil

---

## Phase 5: User Story 3 — Gestion du Footer (Priority: P2)

**Goal**: Permettre aux admins de modifier les sections "À propos" (texte riche), "Contact" (champs structurés) et "Ressources" (liste de liens) du footer

**Independent Test**: Modifier la section "À propos" dans le backoffice, vérifier la mise à jour dans le footer sur n'importe quelle page

### Implementation for User Story 3

- [X] T026 [US3] Implémenter les fonctions service get_footer_about(), update_footer_about(), get_contact(), update_contact(), list_resources(), create_resource(), update_resource(), delete_resource(), reorder_resources() dans backend/app/services/editorial.py
- [X] T027 [P] [US3] Implémenter les endpoints PUT /api/admin/editorial/footer/about et PUT /api/admin/editorial/footer/contact dans backend/app/routers/admin_editorial.py
- [X] T028 [P] [US3] Implémenter les endpoints CRUD pour les ressources (GET, POST, PUT, DELETE /api/admin/editorial/footer/resources et PUT /reorder) dans backend/app/routers/admin_editorial.py
- [X] T029 [US3] Ajouter les données footer complètes à la réponse GET /api/admin/editorial dans backend/app/routers/admin_editorial.py
- [X] T030 [US3] Ajouter les données footer complètes à la réponse GET /api/editorial dans backend/app/routers/public_editorial.py
- [X] T031 [US3] Ajouter les fonctions updateFooterAbout(), updateContact(), createResource(), updateResource(), deleteResource(), reorderResources() au composable dans frontend/app/composables/useEditorial.ts
- [X] T032 [US3] Implémenter l'onglet "Footer" avec 3 sous-sections : "À propos" (RichContentEditor), "Contact" (formulaire structuré email/téléphone/adresse), "Ressources" (liste de liens CRUD avec drag-and-drop ou boutons réordonner) dans frontend/app/pages/admin/editorial.vue
- [X] T033 [US3] Modifier le footer du layout default pour charger dynamiquement les contenus "À propos", "Contact" et "Ressources" depuis l'API dans frontend/app/layouts/default.vue

**Checkpoint**: Le footer complet est gérable depuis le backoffice et affiché dynamiquement sur toutes les pages

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Améliorations transversales et finalisation

- [X] T034 Implémenter la gestion des valeurs par défaut côté frontend : afficher les textes actuels hardcodés si l'API retourne des champs vides, dans frontend/app/pages/index.vue et frontend/app/layouts/default.vue
- [X] T035 Vérifier et ajuster le dark/light mode sur la page admin éditorial (onglets, formulaires, feedback) dans frontend/app/pages/admin/editorial.vue
- [X] T036 Valider la conformité du quickstart.md en testant manuellement le parcours complet (créer contenu → vérifier affichage public)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Pas de dépendances — peut commencer immédiatement
- **Foundational (Phase 2)**: Dépend de Phase 1 (T002 pour les modèles, T001 pour les types)
- **User Stories (Phase 3-5)**: Toutes dépendent de la complétion de Phase 2
  - US1 et US2 peuvent s'exécuter en parallèle (P1 toutes les deux)
  - US3 peut s'exécuter en parallèle avec US1/US2 ou après
- **Polish (Phase 6)**: Dépend de la complétion de toutes les user stories

### User Story Dependencies

- **User Story 1 (P1)**: Après Phase 2 — Aucune dépendance sur d'autres stories
- **User Story 2 (P1)**: Après Phase 2 — Aucune dépendance sur d'autres stories
- **User Story 3 (P2)**: Après Phase 2 — Aucune dépendance sur d'autres stories

### Within Each User Story

- Service avant router (backend)
- Router admin avant router public
- Composable avant page frontend
- Backend avant frontend (les endpoints doivent exister)

### Parallel Opportunities

- T001 et T002 en parallèle (Phase 1)
- T004, T005, T006, T007, T009, T010 en parallèle après T003 (Phase 2)
- US1, US2, US3 peuvent s'exécuter en parallèle après Phase 2
- T027 et T028 en parallèle (endpoints footer)

---

## Parallel Example: User Story 1

```bash
# Backend en parallèle (après T012):
Task: "Implémenter PUT /api/admin/editorial/hero dans admin_editorial.py"
Task: "Ajouter hero à GET /api/editorial dans public_editorial.py"

# Frontend en parallèle (après T016):
Task: "Formulaire onglet Hero Section dans editorial.vue"
Task: "Hero dynamique dans index.vue"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup (T001-T002)
2. Phase 2: Foundational (T003-T011)
3. Phase 3: User Story 1 — Hero Section (T012-T018)
4. **STOP et VALIDER**: Tester la hero section indépendamment
5. Déployer/démo si prêt

### Incremental Delivery

1. Setup + Foundational → Infrastructure prête
2. User Story 1 (Hero) → Tester → Démo (MVP!)
3. User Story 2 (Corps de page) → Tester → Démo
4. User Story 3 (Footer) → Tester → Démo
5. Polish → Finalisation

---

## Notes

- [P] tasks = fichiers différents, pas de dépendances
- [Story] label relie chaque tâche à sa user story pour la traçabilité
- Réutiliser les composants existants : RichContentEditor, RichContentRenderer, EditorJSData schema
- Le schéma EditorJSData de validation existe déjà dans backend/app/schemas/geography.py — à réutiliser
- Chaque user story est indépendamment complétable et testable
- Commit après chaque tâche ou groupe logique
