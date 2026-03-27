# Tasks: Comptes administratifs par région

**Input**: Design documents from `/specs/014-region-admin-accounts/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Non demandés explicitement - non inclus.

**Organization**: Tasks groupées par user story. Aucune modification backend nécessaire.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup

**Purpose**: Aucune configuration nécessaire - le projet est déjà fonctionnel et le backend supporte les régions.

*Pas de tâches dans cette phase.*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Aucun prérequis bloquant - les APIs backend, modèles et composables frontend existent déjà.

*Pas de tâches dans cette phase.*

**Checkpoint**: Le backend supporte déjà `collectivite_type=region`. Les composables `useComptes` et `useGeography` fournissent toutes les fonctions nécessaires. L'implémentation des user stories peut commencer.

---

## Phase 3: User Story 1 - Soumettre un compte administratif pour une région (Priority: P1) MVP

**Goal**: Permettre à un administrateur de créer un compte administratif pour une région et de retrouver les comptes filtrés par région dans la liste admin.

**Independent Test**: Créer un compte pour une région dans `/admin/accounts/new`, vérifier qu'il apparaît dans la liste filtrée `/admin/accounts?collectivite_type=region&collectivite_id={id}`.

### Implementation for User Story 1

- [X] T001 [US1] Ajouter la lecture des query params `collectivite_type` et `collectivite_id` au montage dans `frontend/app/pages/admin/accounts/index.vue` pour pré-remplir les filtres (type, province, région) en utilisant le même pattern que `frontend/app/pages/admin/accounts/new.vue` lignes 49-64 : détecter le type depuis `route.query`, récupérer le détail de la région pour trouver `province_id`, charger les régions en cascade, puis pré-sélectionner `filterType`, `selectedProvinceId` et `selectedRegionId`

**Checkpoint**: Un administrateur peut naviguer vers `/admin/accounts?collectivite_type=region&collectivite_id={id}` et voir la liste filtrée des comptes de cette région.

---

## Phase 4: User Story 2 - Voir les comptes d'une région depuis la fiche admin (Priority: P1)

**Goal**: Ajouter un bouton "Voir les comptes" sur la page d'édition/détail d'une région dans le backoffice.

**Independent Test**: Naviguer vers `/admin/geography/regions/{id}`, vérifier la présence du bouton "Voir les comptes" et qu'il redirige correctement vers la liste filtrée.

### Implementation for User Story 2

- [X] T002 [US2] Ajouter un `UiButton` "Voir les comptes" dans `frontend/app/pages/admin/geography/regions/[id]/index.vue` avec un lien vers `/admin/accounts?collectivite_type=region&collectivite_id=${route.params.id}`. Placer le bouton dans la zone d'actions existante (à côté du bouton "Annuler"), avec l'icône `['fas', 'calculator']` et le variant `ghost`. Le bouton ne doit apparaître que si `!isNew` (pas sur le formulaire de création de nouvelle région).

**Checkpoint**: Le bouton "Voir les comptes" est visible sur la fiche d'une région existante et redirige vers la liste filtrée.

---

## Phase 5: User Story 3 - Consulter publiquement les comptes d'une région (Priority: P2)

**Goal**: Afficher un tableau des comptes administratifs publiés sur la page publique d'une région.

**Independent Test**: Accéder à `/regions/{id}` pour une région ayant des comptes publiés, vérifier l'affichage du tableau avec les années et les liens "Consulter".

### Implementation for User Story 3

- [X] T003 [US3] Ajouter une section "Comptes administratifs" dans `frontend/app/pages/regions/[id].vue` : appeler `GET /api/public/collectivites/region/{id}/annees` via `useApi` au montage pour récupérer les années disponibles, puis afficher un tableau avec colonne "Année d'exercice" et colonne "Action" (lien "Consulter" vers `/api/public/collectivites/region/{id}/comptes?annee={year}` ou page de détail appropriée). Gérer l'état vide avec un message "Aucun compte administratif publié". Respecter le dark/light mode avec les classes Tailwind `dark:` (cohérent avec le style existant de la page).

**Checkpoint**: La page publique d'une région affiche les comptes publiés par année.

---

## Phase 6: User Story 4 - Régions sans communes (Priority: P2)

**Goal**: Vérifier que les régions sans communes fonctionnent correctement dans toutes les interfaces.

**Independent Test**: Accéder à la fiche d'une région sans commune (admin et public), créer un compte pour cette région, vérifier l'absence d'erreurs.

### Implementation for User Story 4

- [X] T004 [US4] Vérifier et corriger si nécessaire le comportement de `frontend/app/pages/admin/geography/regions/[id]/index.vue` quand la région n'a aucune commune : s'assurer que la page d'édition ne produit pas d'erreur. Vérifier aussi que `frontend/app/pages/regions/[id].vue` gère correctement une liste de communes vide (le code actuel utilise `v-if="region.communes?.length"` qui est déjà correct).

**Checkpoint**: Toutes les interfaces fonctionnent sans erreur pour les régions sans communes.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validation globale de la feature.

- [X] T005 Vérification manuelle complète selon `specs/014-region-admin-accounts/quickstart.md` : parcourir les 5 scénarios de test (bouton "Voir les comptes", filtrage, création compte région, publication, page publique, région sans commune)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1-2 (Setup/Foundational)**: Aucune tâche - déjà en place
- **Phase 3 (US1)**: Pas de dépendance - peut commencer immédiatement
- **Phase 4 (US2)**: Dépend de T001 (US1) pour que le lien "Voir les comptes" ait une destination fonctionnelle
- **Phase 5 (US3)**: Pas de dépendance directe - peut être fait en parallèle avec US1/US2
- **Phase 6 (US4)**: Pas de dépendance - vérification indépendante
- **Phase 7 (Polish)**: Dépend de toutes les phases précédentes

### User Story Dependencies

- **US1 (P1)**: Aucune dépendance
- **US2 (P1)**: Fonctionnellement lié à US1 (le lien pointe vers la liste filtrée)
- **US3 (P2)**: Indépendant - page publique séparée
- **US4 (P2)**: Indépendant - validation/vérification

### Parallel Opportunities

- T001 et T003 peuvent être exécutés en parallèle (fichiers différents)
- T002 peut être fait en parallèle avec T003 (fichiers différents), mais après T001
- T004 peut être fait en parallèle avec tout le reste

---

## Parallel Example

```bash
# Batch 1 - En parallèle :
Task T001: "Pré-remplir filtres via query params dans frontend/app/pages/admin/accounts/index.vue"
Task T003: "Ajouter tableau comptes publiés dans frontend/app/pages/regions/[id].vue"
Task T004: "Vérifier régions sans communes dans les interfaces"

# Batch 2 - Après T001 :
Task T002: "Ajouter bouton Voir les comptes dans frontend/app/pages/admin/geography/regions/[id]/index.vue"

# Batch 3 - Après tout :
Task T005: "Vérification manuelle complète"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Implémenter T001 : pré-remplissage des filtres via query params
2. Implémenter T002 : bouton "Voir les comptes" sur la fiche région
3. **STOP et VALIDER** : Un administrateur peut naviguer de la fiche région vers ses comptes

### Incremental Delivery

1. T001 + T002 → Navigation admin complète (MVP)
2. T003 → Page publique enrichie
3. T004 → Robustesse régions sans communes
4. T005 → Validation finale

---

## Notes

- **Impact minimal** : Seulement 3 fichiers Vue à modifier, aucun changement backend
- **Aucune migration DB** : Le modèle supporte déjà les régions
- **Pattern existant** : Le pré-remplissage via query params réutilise le pattern de `new.vue`
- Commit après chaque tâche
