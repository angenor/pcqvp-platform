# Tasks: Back-Office Design Upgrade

**Input**: Design documents from `/specs/012-backoffice-design-upgrade/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Non demandés — validation visuelle manuelle.

**Organization**: Tasks groupées par user story. Chaque story est indépendamment implémentable et testable après la phase foundational.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Peut s'exécuter en parallèle (fichiers différents, pas de dépendances)
- **[Story]**: User story associée (US1, US2, US3, US4, US5)

---

## Phase 1: Setup (Dépendances & Configuration)

**Purpose**: Installer les nouvelles dépendances et configurer les prérequis

- [x] T001 Installer les dépendances FontAwesome dans apps/frontend/package.json (`pnpm add @fortawesome/fontawesome-svg-core @fortawesome/free-solid-svg-icons @fortawesome/free-regular-svg-icons @fortawesome/vue-fontawesome`)
- [x] T002 Ajouter les liens Google Fonts (Barlow Condensed, Inter, JetBrains Mono) dans apps/frontend/nuxt.config.ts (section app.head.link)
- [x] T003 [P] Créer le plugin FontAwesome avec les icônes nécessaires dans apps/frontend/app/plugins/fontawesome.ts (s'inspirer de collectivites_territoriales/frontend_collectivites_territoriales/app/plugins/fontawesome.ts)

---

## Phase 2: Foundational (Design System CSS)

**Purpose**: Mettre en place le design system centralisé — BLOQUE toutes les user stories

**⚠️ CRITICAL**: Aucune tâche de composant ne peut commencer sans cette phase

- [x] T004 Réécrire apps/frontend/app/assets/css/main.css avec le design system complet : variables CSS (palette TI Madagascar #3695d8, couleurs sémantiques, bg/text/border tokens, typographie, espacements, ombres, z-index, transitions), mode sombre via `.dark`, classes utilitaires typographiques (font-heading, font-body, font-mono), support prefers-reduced-motion. S'inspirer de collectivites_territoriales/frontend_collectivites_territoriales/app/assets/css/main.css

**Checkpoint**: Design system et polices visibles sur toutes les pages (admin + public)

---

## Phase 3: User Story 1 — Typographie professionnelle et design system (Priority: P1) 🎯 MVP

**Goal**: Les polices Barlow Condensed/Inter/JetBrains Mono sont appliquées globalement et le design system CSS est fonctionnel en mode clair et sombre

**Independent Test**: Ouvrir n'importe quelle page admin → les titres utilisent Barlow Condensed, le texte Inter, les nombres JetBrains Mono. Basculer en mode sombre → la palette s'inverse correctement.

### Implementation for User Story 1

- [x] T005 [P] [US1] Créer le composant UiLoadingSpinner avec variantes de taille et couleur dans apps/frontend/app/components/ui/UiLoadingSpinner.vue (voir data-model.md pour les props)
- [x] T006 [P] [US1] Créer le composant UiAlert avec variantes sémantiques (success, warning, error, info), mode dismissible et icône par défaut dans apps/frontend/app/components/ui/UiAlert.vue
- [x] T007 [US1] Vérifier que la typographie et les variables CSS s'appliquent correctement sur la page admin/login.vue — adapter les classes Tailwind en dur pour utiliser les variables CSS du design system (var(--bg-card), var(--text-primary), var(--color-primary), etc.)

**Checkpoint**: Typographie et design system visibles et cohérents sur toutes les pages. Mode sombre fonctionnel.

---

## Phase 4: User Story 2 — Layout admin professionnel (Priority: P1)

**Goal**: Sidebar repliable avec menus groupés, header fixe avec fil d'Ariane et toggle sombre, responsive (mobile/tablette/desktop)

**Independent Test**: Naviguer dans le back-office → sidebar visible avec icônes et groupes de menus. Cliquer replier → 64px avec icônes seules. Recharger → l'état persiste. Sur mobile → sidebar en overlay.

### Implementation for User Story 2

- [x] T008 [US2] Créer le composable useSidebar dans apps/frontend/app/composables/useSidebar.ts (état réactif isCollapsed, isMobileOpen, persistance localStorage, watchers pour breakpoints responsive)
- [x] T009 [US2] Créer le composant AdminBreadcrumb dans apps/frontend/app/components/admin/AdminBreadcrumb.vue (auto-génération depuis useRoute(), mapping des segments URL vers labels français lisibles, liens cliquables)
- [x] T010 [US2] Créer le composant AdminSidebar dans apps/frontend/app/components/admin/AdminSidebar.vue (sidebar fixe 256px/64px, logo PCQVP, menus groupés par catégorie avec icônes FontAwesome, sous-menus avec animation chevron, états actifs, overlay mobile, responsive, support mode sombre)
- [x] T011 [US2] Créer le composant AdminHeader dans apps/frontend/app/components/admin/AdminHeader.vue (header fixe, bouton hamburger mobile, AdminBreadcrumb intégré, toggle mode sombre, email utilisateur, bouton déconnexion, margin-left adaptatif selon état sidebar)
- [x] T012 [US2] Refactoriser apps/frontend/app/layouts/admin.vue pour utiliser AdminSidebar et AdminHeader — remplacer toute la sidebar et le header inline par les nouveaux composants, adapter le padding du contenu principal selon l'état de la sidebar

**Checkpoint**: Navigation admin complète et fonctionnelle sur desktop, tablette et mobile. État sidebar persistant.

---

## Phase 5: User Story 3 — Composants UI réutilisables (Priority: P2)

**Goal**: Bibliothèque de composants UI cohérents (Button, Badge, StatCard, Modal, FormInput, FormSelect, FormTextarea) utilisés dans les pages admin existantes

**Independent Test**: Naviguer dans les pages admin → tous les boutons, badges, formulaires et modales utilisent les nouveaux composants avec un style cohérent. Tester en mode sombre.

### Implementation for User Story 3

- [x] T013 [P] [US3] Créer le composant UiButton dans apps/frontend/app/components/ui/UiButton.vue (6 variantes, 3 tailles, loading/disabled, icône FontAwesome, support NuxtLink via prop to, mode block)
- [x] T014 [P] [US3] Créer le composant UiBadge dans apps/frontend/app/components/ui/UiBadge.vue (6 variantes couleur, 2 tailles, dot indicator)
- [x] T015 [P] [US3] Créer le composant UiStatCard dans apps/frontend/app/components/ui/UiStatCard.vue (label, valeur, icône, variante couleur, tendance optionnelle, état skeleton loading, lien cliquable)
- [x] T016 [P] [US3] Créer le composant UiModal dans apps/frontend/app/components/ui/UiModal.vue (v-model visibilité, titre, description, 3 tailles, fermeture backdrop/X, mode danger, slots default + footer, Teleport to body, transitions scale+opacity)
- [x] T017 [P] [US3] Créer le composant UiFormInput dans apps/frontend/app/components/ui/UiFormInput.vue (v-model, types text/email/password/number/date, label, placeholder, required avec indicateur rouge, error avec bordure rouge + message, disabled, icône préfixe, focus ring primaire)
- [x] T018 [P] [US3] Créer le composant UiFormSelect dans apps/frontend/app/components/ui/UiFormSelect.vue (v-model, options array, label, placeholder, required, error, disabled)
- [x] T019 [P] [US3] Créer le composant UiFormTextarea dans apps/frontend/app/components/ui/UiFormTextarea.vue (v-model, label, rows, required, error, disabled)
- [x] T020 [US3] Migrer la page dashboard apps/frontend/app/pages/admin/index.vue — remplacer les 4 cartes stats inline par UiStatCard, utiliser UiButton, appliquer variables CSS du design system
- [x] T021 [US3] Migrer la page login apps/frontend/app/pages/admin/login.vue — remplacer les inputs inline par UiFormInput, le bouton par UiButton, l'erreur par UiAlert
- [x] T022 [P] [US3] Migrer la page config apps/frontend/app/pages/admin/config.vue — remplacer l'input inline par UiFormInput, le bouton par UiButton, le message succès par UiAlert
- [x] T023 [P] [US3] Migrer la page analytics apps/frontend/app/pages/admin/analytics.vue — remplacer les boutons par UiButton, l'alerte par UiAlert, appliquer variables CSS
- [x] T024 [US3] Migrer les pages de détail géographie (create/edit) : adapter apps/frontend/app/pages/admin/geography/provinces/[id].vue, apps/frontend/app/pages/admin/geography/regions/[id].vue, apps/frontend/app/pages/admin/geography/communes/[id].vue — remplacer les inputs/selects par UiFormInput/UiFormSelect, les boutons par UiButton, les erreurs par UiAlert
- [x] T025 [US3] Migrer la page de création de compte apps/frontend/app/pages/admin/accounts/new.vue — remplacer les selects/inputs par UiFormSelect/UiFormInput, le bouton par UiButton, l'erreur par UiAlert
- [x] T026 [US3] Migrer les modales de confirmation de suppression dans les pages de liste géographie (provinces/index.vue, regions/index.vue, communes/index.vue) — remplacer les modales inline par UiModal avec mode danger

**Checkpoint**: Tous les boutons, badges, formulaires et modales des pages admin utilisent les composants UI. Cohérence visuelle en mode clair et sombre.

---

## Phase 6: User Story 4 — Tables de données améliorées (Priority: P2)

**Goal**: Composant DataTable professionnel avec recherche, tri, pagination, skeleton et état vide — intégré dans toutes les pages de liste admin

**Independent Test**: Ouvrir une page de liste admin (provinces, utilisateurs) → DataTable avec barre de recherche, en-têtes triables, pagination, skeleton au chargement, état vide quand aucun résultat.

### Implementation for User Story 4

- [x] T027 [US4] Créer le composant UiDataTable dans apps/frontend/app/components/ui/UiDataTable.vue (colonnes configurables, barre de recherche, tri asc/desc avec indicateur visuel, pagination avec Précédent/Suivant et numéros de page, skeleton loader, état vide avec icône/message/slot action, slots cell-{key} pour rendu custom, slot toolbar pour actions en-tête, slot actions pour colonne d'actions par ligne)
- [x] T028 [US4] Migrer la page liste provinces apps/frontend/app/pages/admin/geography/provinces/index.vue — remplacer la table inline par UiDataTable avec colonnes Nom/Code/Actions, intégrer la recherche et pagination existantes
- [x] T029 [P] [US4] Migrer la page liste régions apps/frontend/app/pages/admin/geography/regions/index.vue — remplacer par UiDataTable avec colonnes Nom/Code/Province/Actions, intégrer les filtres existants (recherche + province dropdown)
- [x] T030 [P] [US4] Migrer la page liste communes apps/frontend/app/pages/admin/geography/communes/index.vue — remplacer par UiDataTable avec colonnes Nom/Code/Région/Actions
- [x] T031 [US4] Migrer la page liste utilisateurs apps/frontend/app/pages/admin/users/index.vue — remplacer par UiDataTable avec colonnes Email/Role(UiBadge)/Statut(UiBadge)/Date/Actions
- [x] T032 [P] [US4] Migrer la page newsletter apps/frontend/app/pages/admin/newsletter.vue — remplacer par UiDataTable avec colonnes Email/Statut(UiBadge)/Date/Actions, intégrer filtres existants et export CSV
- [x] T033 [P] [US4] Migrer la page liste comptes administratifs apps/frontend/app/pages/admin/accounts/index.vue — remplacer par UiDataTable avec colonnes Collectivité/Type/Année/Statut(UiBadge)/Modifié/Actions, intégrer les 4 filtres dropdown
- [x] T034 [P] [US4] Migrer la page liste templates apps/frontend/app/pages/admin/templates/index.vue — remplacer par UiDataTable avec colonnes Nom/Type(UiBadge)/Version/Statut(UiBadge)/Lignes/Colonnes/Date

**Checkpoint**: Toutes les pages de liste admin (7) utilisent UiDataTable. Recherche, tri et pagination fonctionnels.

---

## Phase 7: User Story 5 — Icônes et finitions visuelles (Priority: P3)

**Goal**: Système d'icônes FontAwesome cohérent intégré partout, finitions visuelles (bordures arrondies 12px, ombres subtiles, transitions fluides)

**Independent Test**: Parcourir toutes les pages admin → chaque élément de navigation a une icône, les boutons d'action combinent icône + texte, les cartes ont des bordures arrondies et ombres cohérentes.

### Implementation for User Story 5

- [x] T035 [P] [US5] Adapter le composant GeographySelector dans apps/frontend/app/components/GeographySelector.vue — remplacer les selects inline par UiFormSelect, appliquer variables CSS du design system
- [x] T036 [P] [US5] Adapter le composant SearchBar dans apps/frontend/app/components/SearchBar.vue — appliquer variables CSS, icône FontAwesome pour la recherche, utiliser tokens du design system
- [x] T037 [P] [US5] Adapter le composant NewsletterForm dans apps/frontend/app/components/NewsletterForm.vue — remplacer par UiFormInput + UiButton + UiAlert
- [x] T038 [P] [US5] Adapter le composant AccountDataTable dans apps/frontend/app/components/AccountDataTable.vue — appliquer variables CSS du design system (bg-card, border-default, text-primary/secondary), bordures arrondies, ombres
- [x] T039 [P] [US5] Adapter les composants RecapTable et EquilibreTable dans apps/frontend/app/components/RecapTable.vue et apps/frontend/app/components/EquilibreTable.vue — appliquer variables CSS du design system
- [x] T040 [P] [US5] Adapter le composant AccountTable dans apps/frontend/app/components/AccountTable.vue — appliquer variables CSS du design system
- [x] T041 [P] [US5] Adapter le composant RichContentRenderer dans apps/frontend/app/components/RichContentRenderer.vue — appliquer variables CSS pour les couleurs de texte et bordures
- [x] T042 [US5] Migrer la page template détail apps/frontend/app/pages/admin/templates/[id].vue — remplacer les boutons inline par UiButton avec icônes, les modales par UiModal, appliquer le design system
- [x] T043 [US5] Migrer les pages comptes détail : apps/frontend/app/pages/admin/accounts/[id]/recettes.vue, apps/frontend/app/pages/admin/accounts/[id]/depenses.vue, apps/frontend/app/pages/admin/accounts/[id]/recap.vue — appliquer variables CSS, remplacer boutons par UiButton avec icônes, onglets stylisés

**Checkpoint**: Toutes les pages admin et composants utilisent le design system. Icônes cohérentes partout. Finitions visuelles uniformes.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Vérification finale, cohérence globale et nettoyage

- [x] T044 Vérification de cohérence : parcourir les 19 pages admin et vérifier que toutes utilisent les variables CSS du design system (aucune couleur Tailwind en dur type bg-blue-600, text-gray-900, etc.)
- [x] T045 Vérification responsive : tester le layout admin sur les 3 breakpoints (mobile <768px, tablette 768-1024px, desktop >1024px) — sidebar overlay/repliée/dépliée
- [x] T046 Vérification mode sombre : parcourir toutes les pages admin en mode sombre et vérifier la palette inversée (pas de flash, transitions fluides)
- [x] T047 Vérification fonctionnelle : tester que toutes les fonctionnalités existantes marchent (CRUD géographie, CRUD comptes, login, déconnexion, export, filtres, pagination, recherche)
- [x] T048 Adapter le style du composant RichContentEditor dans apps/frontend/app/components/RichContentEditor.vue — appliquer variables CSS du design system pour les styles de l'éditeur EditorJS (toolbar, conteneur, blocs)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Pas de dépendances — peut démarrer immédiatement
- **Foundational (Phase 2)**: Dépend de Phase 1 — BLOQUE toutes les user stories
- **US1 (Phase 3)**: Dépend de Phase 2 — vérification et composants de base
- **US2 (Phase 4)**: Dépend de Phase 2 — peut s'exécuter en parallèle avec US1
- **US3 (Phase 5)**: Dépend de Phase 2 — peut s'exécuter en parallèle avec US1/US2
- **US4 (Phase 6)**: Dépend de US3 (utilise UiButton, UiBadge dans les tables)
- **US5 (Phase 7)**: Dépend de US3 et US4 (composants UI et DataTable créés)
- **Polish (Phase 8)**: Dépend de toutes les user stories

### User Story Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational - Design System CSS)
    ↓
┌───────────────────────────────┐
│  US1 (P1) ──┐                │
│  US2 (P1) ──┤ en parallèle   │
│  US3 (P2) ──┘                │
└───────────────────────────────┘
    ↓
US4 (P2) — dépend de US3 (UiButton, UiBadge)
    ↓
US5 (P3) — dépend de US3 + US4
    ↓
Phase 8 (Polish)
```

### Within Each User Story

- Composants UI avant pages qui les utilisent
- Composants partagés (AdminSidebar, AdminHeader) avant layout refactoring
- Pages de liste après UiDataTable
- Adaptation composants existants en dernier

### Parallel Opportunities

- T002 et T003 en parallèle (nuxt.config vs plugin)
- T005 et T006 en parallèle (UiLoadingSpinner vs UiAlert)
- T013-T019 tous en parallèle (composants UI indépendants)
- T022 et T023 en parallèle (pages config et analytics)
- T029, T030, T032, T033, T034 en parallèle (pages de liste indépendantes)
- T035-T041 tous en parallèle (adaptation composants existants indépendants)

---

## Parallel Example: User Story 3 (Composants UI)

```bash
# Créer tous les composants UI en parallèle (fichiers indépendants) :
Task T013: "Créer UiButton dans apps/frontend/app/components/ui/UiButton.vue"
Task T014: "Créer UiBadge dans apps/frontend/app/components/ui/UiBadge.vue"
Task T015: "Créer UiStatCard dans apps/frontend/app/components/ui/UiStatCard.vue"
Task T016: "Créer UiModal dans apps/frontend/app/components/ui/UiModal.vue"
Task T017: "Créer UiFormInput dans apps/frontend/app/components/ui/UiFormInput.vue"
Task T018: "Créer UiFormSelect dans apps/frontend/app/components/ui/UiFormSelect.vue"
Task T019: "Créer UiFormTextarea dans apps/frontend/app/components/ui/UiFormTextarea.vue"

# Puis migrer les pages (après que les composants soient créés) :
Task T020: "Migrer dashboard avec UiStatCard"
Task T021: "Migrer login avec UiFormInput + UiButton"
Task T022: "Migrer config" (parallèle avec T023)
Task T023: "Migrer analytics" (parallèle avec T022)
```

---

## Implementation Strategy

### MVP First (US1 + US2 = Phases 1-4)

1. Compléter Phase 1: Setup (dépendances)
2. Compléter Phase 2: Foundational (design system CSS)
3. Compléter Phase 3: US1 (typographie visible globalement)
4. Compléter Phase 4: US2 (layout admin professionnel)
5. **STOP and VALIDATE**: La sidebar repliable, le header avec fil d'Ariane et les polices sont en place. L'admin est déjà visuellement transformé.

### Incremental Delivery

1. Setup + Foundational → Polices et couleurs visibles partout
2. US1 + US2 → Layout admin professionnel (MVP!)
3. US3 → Composants UI + migration formulaires/pages simples
4. US4 → DataTable + migration pages de liste
5. US5 → Icônes + finitions + adaptation composants existants
6. Polish → Vérification globale

### Single Developer Strategy

Exécution séquentielle recommandée : Phase 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8
Avec parallélisation au sein de chaque phase (composants UI en parallèle, pages en parallèle).

---

## Notes

- [P] tasks = fichiers différents, pas de dépendances
- [Story] label mappe chaque tâche à sa user story
- Aucun test automatisé demandé — validation visuelle manuelle
- S'inspirer fortement de `collectivites_territoriales/frontend_collectivites_territoriales/` pour le code des composants (design system, sidebar, header, composants UI)
- Ne PAS copier le code directement — l'adapter au contexte de la plateforme actuelle
- Toutes les pages DOIVENT conserver leurs fonctionnalités existantes intactes
- Commit après chaque tâche ou groupe logique
