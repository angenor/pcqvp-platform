# Tasks: EditorJS Rich Content pour Géographies

**Input**: Design documents from `/specs/011-editorjs-rich-content/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Installation des dépendances EditorJS et configuration upload backend

- [x] T001 Installer les packages EditorJS dans le frontend : `pnpm add @editorjs/editorjs @editorjs/header @editorjs/image @editorjs/table @editorjs/list` dans apps/frontend/package.json
- [x] T002 [P] Ajouter les settings d'upload dans apps/backend/app/core/config.py : UPLOAD_DIR (default "uploads/images"), MAX_IMAGE_SIZE (default 5 * 1024 * 1024), ALLOWED_IMAGE_TYPES (default ["image/jpeg", "image/png", "image/webp", "image/gif"])
- [x] T003 [P] Créer le répertoire apps/backend/uploads/images/ et ajouter uploads/ au .gitignore du backend

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Types partagés, schémas Pydantic, endpoint upload et adaptation du service backend. DOIT être complété avant toute user story.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Mettre à jour les types partagés dans packages/shared/types/geography.ts : remplacer l'interface RichContentBlock par les interfaces EditorJSBlock (id?, type, data), EditorJSData (time?, blocks, version?) et exporter les types de blocs supportés (header, paragraph, image, table, list)
- [x] T005 Remplacer les schémas Pydantic dans apps/backend/app/schemas/geography.py : supprimer HeadingBlock, ParagraphBlock, ImageBlock et RichContentBlock. Créer EditorJSBlock (id: str | None, type: str validé parmi header/paragraph/image/table/list, data: dict) et EditorJSData (time: int | None, blocks: list[EditorJSBlock], version: str | None). Mettre à jour ProvinceCreate/Update, RegionCreate/Update, CommuneCreate/Update pour utiliser description_json: EditorJSData | None au lieu de list[RichContentBlock]
- [x] T006 Créer le routeur d'upload dans apps/backend/app/routers/upload.py : endpoint POST /api/admin/upload/image (multipart/form-data, validation MIME et taille, stockage avec UUID, retourne {success: 1, file: {url}}), endpoint POST /api/admin/upload/image-by-url (reçoit JSON {url}, télécharge et stocke localement), les deux protégés par require_role("admin", "editor")
- [x] T007 Monter le routeur upload et StaticFiles dans apps/backend/app/main.py : ajouter le routeur upload et monter StaticFiles(directory="uploads") sur le chemin /uploads pour servir les images
- [x] T008 Adapter le routeur admin géographie dans apps/backend/app/routers/admin_geography.py : modifier les endpoints create/update des provinces, régions et communes pour passer description_json au format EditorJS (dict avec model_dump() sur EditorJSData au lieu de la liste de blocs)
- [x] T009 Adapter le service géographie dans apps/backend/app/services/geography.py : mettre à jour les signatures et le traitement de description_json pour accepter un dict (format EditorJS) au lieu d'une liste de blocs

**Checkpoint**: Backend complet avec nouveaux schémas, upload fonctionnel et service adapté

---

## Phase 3: User Story 1 - Rédaction de contenu riche avec EditorJS (Priority: P1) 🎯 MVP

**Goal**: L'administrateur peut rédiger la description d'une province avec EditorJS (paragraphe, titre, image, tableau, liste) et sauvegarder.

**Independent Test**: Accéder à /admin/geography/provinces/[id], utiliser l'éditeur pour ajouter tous les types de blocs, sauvegarder, recharger et vérifier la persistance.

### Implementation for User Story 1

- [x] T010 [US1] Réécrire le composant RichContentEditor.vue dans apps/frontend/app/components/RichContentEditor.vue : initialiser EditorJS avec les outils Header, Image (configuré avec endpoint upload /api/admin/upload/image et fetchUrl pour upload-by-url), Table, List. Supporter v-model via defineModel avec EditorJSData. Utiliser onMounted pour instancier l'éditeur (client-only). Implémenter editor.save() pour émettre les données au parent. Gérer la destruction de l'instance dans onBeforeUnmount
- [x] T011 [US1] Ajouter les styles dark mode pour EditorJS dans apps/frontend/app/components/RichContentEditor.vue ou dans un fichier CSS dédié apps/frontend/app/assets/css/editorjs-dark.css : cibler .dark .codex-editor, .dark .ce-block, .dark .ce-toolbar, .dark .ce-inline-toolbar, .dark .tc-table avec les couleurs appropriées (fond sombre, texte clair, bordures adaptées)
- [x] T012 [US1] Mettre à jour la page admin province dans apps/frontend/app/pages/admin/geography/provinces/[id].vue : encapsuler RichContentEditor dans un wrapper ClientOnly avec un fallback de chargement, adapter le formulaire pour envoyer description_json au format EditorJSData (objet avec blocks) au lieu d'une liste de blocs
- [x] T013 [US1] Adapter le composable useGeography dans apps/frontend/app/composables/useGeography.ts : modifier les fonctions createProvince, updateProvince, createRegion, updateRegion, createCommune, updateCommune pour envoyer description_json comme objet EditorJSData au lieu d'un tableau de blocs

**Checkpoint**: L'édition d'une province avec EditorJS fonctionne de bout en bout (création, sauvegarde, rechargement)

---

## Phase 4: User Story 2 - Affichage public du contenu EditorJS (Priority: P1)

**Goal**: Le visiteur voit le contenu EditorJS (paragraphe, titre, image, tableau, liste) correctement rendu sur les pages publiques.

**Independent Test**: Créer du contenu avec tous les types de blocs via l'admin, consulter la page publique et vérifier le rendu de chaque bloc.

### Implementation for User Story 2

- [x] T014 [US2] Réécrire le composant RichContentRenderer.vue dans apps/frontend/app/components/RichContentRenderer.vue : accepter une prop descriptionJson de type EditorJSData (objet avec blocks au lieu d'un tableau). Rendre chaque type de bloc : header → h2/h3/h4 selon level, paragraph → p avec v-html, image → img avec caption et fallback placeholder, table → table HTML avec thead si withHeadings, list → ul/ol avec li. Support dark mode via classes dark:
- [x] T015 [US2] Mettre à jour les pages publiques qui utilisent RichContentRenderer : vérifier que apps/frontend/app/pages/provinces/[id].vue, apps/frontend/app/pages/regions/[id].vue et apps/frontend/app/pages/communes/[id].vue passent correctement la prop descriptionJson au format EditorJSData

**Checkpoint**: Le rendu public affiche correctement tous les types de blocs EditorJS avec support dark mode

---

## Phase 5: User Story 3 - Uniformité entre provinces, régions et communes (Priority: P2)

**Goal**: L'édition avec EditorJS est identique sur les trois types d'entités géographiques.

**Independent Test**: Naviguer entre les pages d'édition des provinces, régions et communes, vérifier que l'éditeur offre les mêmes outils et la même apparence.

### Implementation for User Story 3

- [x] T016 [P] [US3] Mettre à jour la page admin région dans apps/frontend/app/pages/admin/geography/regions/[id].vue : encapsuler RichContentEditor dans ClientOnly avec fallback, adapter le formulaire pour envoyer description_json au format EditorJSData
- [x] T017 [P] [US3] Mettre à jour la page admin commune dans apps/frontend/app/pages/admin/geography/communes/[id].vue : encapsuler RichContentEditor dans ClientOnly avec fallback, adapter le formulaire pour envoyer description_json au format EditorJSData

**Checkpoint**: Les trois types d'entités utilisent le même éditeur EditorJS avec une expérience identique

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Migration, tests et nettoyage

- [x] T018 [P] Créer le script de migration dans apps/backend/scripts/migrate_description_format.py : se connecter à la DB, lire les description_json au format ancien (liste de blocs), convertir chaque bloc vers le format EditorJS (heading → header avec level:2, paragraph → paragraph avec text, image → image avec file.url), écrire le résultat au format EditorJSData. Traiter les trois tables (provinces, regions, communes)
- [x] T019 [P] Mettre à jour les tests géographie dans apps/backend/tests/test_geography.py : adapter tous les payloads de test pour utiliser le format EditorJSData ({time, blocks, version}) au lieu de la liste de blocs. Vérifier la création, mise à jour et lecture avec le nouveau format
- [x] T020 [P] Créer les tests d'upload dans apps/backend/tests/test_upload.py : tester POST /api/admin/upload/image avec fichier valide (200), fichier trop gros (413), type MIME invalide (400), sans authentification (403). Tester POST /api/admin/upload/image-by-url avec URL valide
- [x] T021 Supprimer le code obsolète : retirer les anciennes interfaces HeadingBlock, ParagraphBlock, ImageBlock des types partagés packages/shared/types/geography.ts si encore référencées, nettoyer les imports inutilisés dans les composants et composables frontend
- [x] T022 Vérification finale dark mode : tester l'éditeur EditorJS et le renderer sur les 3 pages admin et les 3 pages publiques en mode clair et sombre, corriger les éventuels artefacts visuels

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) completion
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) - can start in parallel with US1
- **User Story 3 (Phase 5)**: Depends on US1 completion (le composant EditorJS doit être prêt)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Renderer indépendant de l'éditeur, peut être développé en parallèle avec US1
- **User Story 3 (P2)**: Depends on US1 completion - réutilise le composant RichContentEditor créé dans US1

### Within Each User Story

- Schémas/types avant composants
- Composants backend avant frontend
- Core implementation avant intégration dans les pages

### Parallel Opportunities

- T002 et T003 en parallèle (fichiers différents)
- T016 et T017 en parallèle (pages différentes, même pattern)
- T018, T019 et T020 en parallèle (fichiers différents)
- US1 et US2 peuvent être développés en parallèle (éditeur et renderer sont indépendants)

---

## Parallel Example: Phase 2

```bash
# Après T004 (types partagés), ces tâches peuvent avancer en parallèle :
Task T005: "Schémas Pydantic dans apps/backend/app/schemas/geography.py"
Task T006: "Routeur upload dans apps/backend/app/routers/upload.py"
```

## Parallel Example: User Story 3

```bash
# Les deux pages admin peuvent être mises à jour en parallèle :
Task T016: "Page admin région dans apps/frontend/app/pages/admin/geography/regions/[id].vue"
Task T017: "Page admin commune dans apps/frontend/app/pages/admin/geography/communes/[id].vue"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T009)
3. Complete Phase 3: User Story 1 (T010-T013)
4. **STOP and VALIDATE**: Tester l'édition d'une province avec EditorJS de bout en bout
5. Continuer avec US2 et US3

### Incremental Delivery

1. Setup + Foundational → Infrastructure prête
2. Add User Story 1 → Éditeur EditorJS fonctionnel pour provinces → Test indépendant
3. Add User Story 2 → Rendu public des blocs EditorJS → Test indépendant
4. Add User Story 3 → Régions et communes alignées → Test indépendant
5. Polish → Migration, tests, dark mode → Livraison complète

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- EditorJS nécessite `<ClientOnly>` dans Nuxt 4 (pas de SSR)
- Le format EditorJS est stocké directement en JSONB sans modification de schéma DB
- L'ancien format est abandonné (projet pas en production)
- Commit after each task or logical group
