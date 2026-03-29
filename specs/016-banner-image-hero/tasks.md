# Tasks: Image banniere hero section collectivites

**Input**: Design documents from `/specs/016-banner-image-hero/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped par user story pour permettre l'implementation et le test independant de chaque story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Peut tourner en parallele (fichiers differents, pas de dependances)
- **[Story]**: User story concernee (US1, US2, US3)
- Chemins exacts dans les descriptions

---

## Phase 1: Setup

**Purpose**: Migration de base de donnees et types partages

- [X] T001 Creer la migration Alembic ajoutant `banner_image VARCHAR(500) NULL` sur les tables provinces, regions, communes dans `backend/alembic/versions/007_add_banner_image.py`
- [X] T002 Ajouter le champ `banner_image` aux modeles Province, Region, Commune dans `backend/app/models/geography.py`

**Checkpoint**: Migration prete, modeles a jour

---

## Phase 2: Foundational (Backend schemas + services + types partages)

**Purpose**: Schemas Pydantic, services et types partages utilises par toutes les user stories

- [X] T003 [P] Ajouter `banner_image: str | None` aux schemas ProvinceCreate, ProvinceUpdate, ProvinceDetail, RegionCreate, RegionUpdate, RegionDetail, CommuneCreate, CommuneUpdate, CommuneDetail dans `backend/app/schemas/geography.py`
- [X] T004 [P] Ajouter le parametre `banner_image` aux fonctions create/update de Province, Region, Commune dans `backend/app/services/geography.py`
- [X] T005 [P] Inclure `banner_image` dans la reponse de `get_collectivite_description()` dans `backend/app/services/public_service.py`
- [X] T006 [P] Ajouter `banner_image: string | null` aux interfaces ProvinceDetail, RegionDetail, CommuneDetail dans `packages/shared/types/geography.ts`
- [X] T007 [P] Ajouter `banner_image: string | null` a l'interface PublicDescriptionResponse dans `packages/shared/types/public.ts`
- [X] T008 [P] Ajouter `banner_image` aux parametres des fonctions create/update (Province, Region, Commune) dans `frontend/app/composables/useGeography.ts`

**Checkpoint**: Backend et types prets, les routers admin utilisent deja les schemas mis a jour automatiquement

---

## Phase 3: User Story 1 - Ajouter une image banniere depuis le backoffice (Priority: P1) MVP

**Goal**: Permettre aux editeurs d'ajouter, remplacer et supprimer une image banniere sur les communes et regions via le backoffice.

**Independent Test**: Editer une commune/region dans le backoffice, uploader une image banniere, sauvegarder, recharger la page et verifier que l'image est preservee.

### Implementation for User Story 1

- [X] T009 [P] [US1] Ajouter le champ d'upload d'image banniere (avec apercu, remplacement et suppression) au formulaire d'edition commune dans `frontend/app/pages/admin/geography/communes/[id].vue`
- [X] T010 [P] [US1] Ajouter le champ d'upload d'image banniere (avec apercu, remplacement et suppression) au formulaire d'edition region dans `frontend/app/pages/admin/geography/regions/[id]/index.vue`

**Checkpoint**: Un editeur peut ajouter/remplacer/supprimer une banniere sur une commune ou region. L'image persiste apres rechargement.

---

## Phase 4: User Story 2 - Affichage du hero section sur la page publique (Priority: P2)

**Goal**: Afficher un hero section full-bleed (~250-300px) avec l'image banniere en fond et le nom/type superposes sur la page publique de detail. Le hero remplace le bloc titre. La description riche reste affichee apres le hero.

**Independent Test**: Visiter la page publique d'une collectivite avec banniere et verifier le hero section. Visiter une collectivite sans banniere et verifier que le layout actuel est preserve.

### Implementation for User Story 2

- [X] T011 [US2] Creer le composant `CollectiviteHero.vue` (image fond full-bleed, overlay sombre, nom et type centres, responsive, dark/light mode) dans `frontend/app/components/CollectiviteHero.vue`
- [X] T012 [US2] Integrer `CollectiviteHero` dans la page de detail : afficher le hero si `banner_image` existe (remplacant le bloc titre), conserver le bloc titre sinon, et afficher la description riche apres le hero dans `frontend/app/pages/collectivite/[type]-[id].vue`

**Checkpoint**: Hero section visible sur les pages publiques avec banniere. Pages sans banniere inchangees. Description riche affichee apres le hero.

---

## Phase 5: User Story 3 - Gestion de la banniere province (Priority: P3)

**Goal**: Etendre la fonctionnalite banniere aux provinces (backoffice + page publique).

**Independent Test**: Editer une province, ajouter une banniere, verifier l'affichage sur la page publique.

### Implementation for User Story 3

- [X] T013 [US3] Ajouter le champ d'upload d'image banniere au formulaire d'edition province dans `frontend/app/pages/admin/geography/provinces/[id]/index.vue`

**Checkpoint**: Les provinces supportent egalement les bannieres. Le composant `CollectiviteHero` fonctionne deja pour les provinces car il est generique (base sur `banner_image` dans PublicDescriptionResponse).

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T014 [P] Verifier le rendu du hero section en mode sombre et clair sur mobile, tablette et desktop
- [X] T015 Valider le quickstart.md : suivre les etapes et verifier le fonctionnement de bout en bout

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Pas de dependance - demarrage immediat
- **Phase 2 (Foundational)**: Depend de Phase 1 (modeles necessaires pour les schemas)
- **Phase 3 (US1)**: Depend de Phase 2
- **Phase 4 (US2)**: Depend de Phase 2 (et idealement d'avoir des donnees de test via US1)
- **Phase 5 (US3)**: Depend de Phase 2
- **Phase 6 (Polish)**: Depend de toutes les phases precedentes

### User Story Dependencies

- **US1 (P1)**: Independante apres Phase 2
- **US2 (P2)**: Independante apres Phase 2 (peut utiliser des donnees seedees manuellement si US1 pas encore faite)
- **US3 (P3)**: Independante apres Phase 2

### Parallel Opportunities

- T003-T008 (Phase 2) : tous parallelisables (fichiers differents)
- T009-T010 (US1) : parallelisables (formulaires differents)
- US1, US2, US3 : peuvent etre implementees en parallele apres Phase 2

---

## Parallel Example: Phase 2

```bash
# Tous les fichiers sont differents, lancement en parallele :
Task: "T003 - Schemas Pydantic dans backend/app/schemas/geography.py"
Task: "T004 - Services geography dans backend/app/services/geography.py"
Task: "T005 - Service public dans backend/app/services/public_service.py"
Task: "T006 - Types geography dans packages/shared/types/geography.ts"
Task: "T007 - Types public dans packages/shared/types/public.ts"
Task: "T008 - Composable useGeography dans frontend/app/composables/useGeography.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completer Phase 1 : Setup (migration + modeles)
2. Completer Phase 2 : Foundational (schemas + services + types)
3. Completer Phase 3 : User Story 1 (formulaires admin)
4. **STOP et VALIDER** : Tester l'upload de banniere dans le backoffice
5. Deployer/demo si pret

### Incremental Delivery

1. Setup + Foundational -> Foundation prete
2. Ajouter US1 -> Tester -> Deploy/Demo (MVP : backoffice avec banniere)
3. Ajouter US2 -> Tester -> Deploy/Demo (hero section visible publiquement)
4. Ajouter US3 -> Tester -> Deploy/Demo (provinces incluses)
5. Polish -> Validation finale

---

## Notes

- L'endpoint d'upload existant (`POST /api/admin/upload/image`) est reutilise tel quel
- Les routers admin n'ont pas besoin de modification car ils utilisent les schemas Pydantic mis a jour
- Le composant `CollectiviteHero` est generique et fonctionne pour les 3 types de collectivites
- Commit apres chaque tache ou groupe logique
