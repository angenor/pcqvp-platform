# Tasks: Navigation Géographique Admin en Grille

**Feature**: 013-admin-geography-grid | **Date**: 2026-03-26
**Plan**: [plan.md](plan.md) | **Spec**: [spec.md](spec.md)

## Phase 1: Foundational — Composants réutilisables

**Goal**: Créer les 2 nouveaux composants de base utilisés par toutes les pages.

- [x] T001 [P] Create UiDropdownMenu component in `frontend/app/components/ui/UiDropdownMenu.vue` — Generic dropdown menu with trigger button (⋮ icon), items list (label, icon, variant default/danger, action callback), click-outside close, dark mode support. Props: `items: DropdownItem[]`, `position: 'left' | 'right'`. Use FontAwesome `fas ellipsis-vertical` for trigger icon. Tailwind classes with `dark:` variants for all colors.

- [x] T002 [P] Create GeographyCard component in `frontend/app/components/GeographyCard.vue` — Card displaying a geographic entity with: name (prominent), code (secondary), clickable area for drill-down navigation, UiDropdownMenu (⋮) with "Éditer" and "Supprimer" actions, optional "Voir les comptes" link for regions, optional "Soumettre un compte" link for regions. Props: `id: string`, `name: string`, `code: string`, `type: 'province' | 'region' | 'commune'`, `clickRoute?: string`, `showFinancialLinks?: boolean`. Emits: `edit`, `delete`. Responsive card with rounded borders, shadow, dark mode support using CSS variables (--bg-card, --border-default, --shadow-sm). Click on card body navigates via `navigateTo(clickRoute)`. Click on menu ⋮ stops propagation. Financial links navigate to `/admin/accounts?collectivite_type=region&collectivite_id={id}` and `/admin/accounts/new?collectivite_type=region&collectivite_id={id}`.

## Phase 2: User Story 1 — Grille Provinces + drill-down Province→Régions→Communes (P1)

**Goal**: Remplacer le tableau provinces par une grille de cartes et créer les pages drill-down.
**Independent Test**: Naviguer `/admin/geography/provinces`, voir les cartes en grille, cliquer sur une province, voir ses régions, cliquer sur une région, voir ses communes. Vérifier fil d'Ariane et CRUD via menu ⋮.

- [x] T003 Refactor provinces list page `frontend/app/pages/admin/geography/provinces/index.vue` — Replace UiDataTable with a responsive grid of GeographyCard components. Load all provinces via `useGeography().fetchProvinces()` (no pagination). Add client-side search input (`UiFormInput`) that filters cards by name. Each card: `clickRoute="/admin/geography/provinces/${item.id}/regions"`, emit edit → `navigateTo(/admin/geography/provinces/${item.id})`, emit delete → show UiModal confirmation then call `deleteProvince(id)`. Keep "Nouvelle province" button navigating to `/admin/geography/provinces/new`. Grid layout: `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4`. Handle loading state and empty state ("Aucune province" with create button).

- [x] T004 Create drill-down page `frontend/app/pages/admin/geography/provinces/[id]/regions.vue` — New page showing regions of a specific province. Load province detail via `useGeography().fetchProvinceDetail(route.params.id)` which includes `regions[]`. Display breadcrumb: "Provinces" (link to `/admin/geography/provinces`) > "[Province Name]" > "Régions". Show regions in grid of GeographyCard with `type="region"`, `showFinancialLinks=true`, `clickRoute="/admin/geography/regions/${region.id}/communes"`. Menu ⋮ edit → `/admin/geography/regions/${region.id}`. Client-side search filter. Empty state: "Aucune région pour cette province" with button to `/admin/geography/regions/new`. Use admin layout and auth middleware.

- [x] T005 Create drill-down page `frontend/app/pages/admin/geography/regions/[id]/communes.vue` — New page showing communes of a specific region. Load region detail via `useGeography().fetchRegionDetail(route.params.id)` which includes `communes[]`. Need province info for breadcrumb: fetch region detail, then use region.province_id to build breadcrumb. Display breadcrumb: "Provinces" (link) > "[Province Name]" (link to `/admin/geography/provinces/${provinceId}/regions`) > "[Region Name]" > "Communes". Show communes in grid of GeographyCard with `type="commune"`. Menu ⋮ edit → `/admin/geography/communes/${commune.id}`. Client-side search. Empty state: "Aucune commune pour cette région" with button to `/admin/geography/communes/new`. Use admin layout and auth middleware.

## Phase 3: User Story 2 — Grille Régions + filtre par province (P1)

**Goal**: Remplacer le tableau régions par une grille avec filtre province et drill-down vers communes.
**Independent Test**: Naviguer `/admin/geography/regions`, voir la grille, filtrer par province, cliquer sur une région pour voir ses communes.

- [x] T006 Refactor regions list page `frontend/app/pages/admin/geography/regions/index.vue` — Replace UiDataTable with grid of GeographyCard. Load all regions via `useGeography().fetchRegions()` (no pagination, no province_id initially). Add province filter: `UiFormSelect` populated via `fetchProvinces()`, with "Toutes les provinces" default option. When province selected, call `fetchRegions(provinceId)` to get filtered results. Add client-side search input filtering by name. Each card: `type="region"`, `showFinancialLinks=true`, `clickRoute="/admin/geography/regions/${item.id}/communes"`. Menu ⋮ edit → `/admin/geography/regions/${item.id}`, delete → modal + `deleteRegion(id)`. Keep "Nouvelle région" button. Grid layout same as provinces. Loading and empty states.

## Phase 4: User Story 3 — Section "Données Financières" sur les régions (P1)

**Goal**: Intégrer les liens vers les comptes administratifs dans les cartes de région.
**Independent Test**: Sur toute carte de région (page Régions ou drill-down), vérifier la présence de "Voir les comptes" et "Soumettre un compte" et que les redirections sont correctes.

- [x] T007 Verify and adjust GeographyCard financial links — Ensure the GeographyCard component (created in T002) correctly renders the "Voir les comptes" and "Soumettre un compte" links when `showFinancialLinks=true`. Verify: (1) "Voir les comptes" navigates to `/admin/accounts?collectivite_type=region&collectivite_id={id}`, (2) "Soumettre un compte" navigates to `/admin/accounts/new?collectivite_type=region&collectivite_id={id}`. Verify these links appear on region cards in both the provinces drill-down page (T004) and the regions list page (T006). Use FontAwesome icons: `fas coins` for "Voir les comptes", `fas plus-circle` for "Soumettre un compte". Links should be styled as small text links below the card content, not as primary actions.

- [x] T008 Update accounts creation page to accept query params `frontend/app/pages/admin/accounts/new.vue` — Modify the "new account" page to read `collectivite_type` and `collectivite_id` from `route.query` and pre-fill the corresponding form fields (type selector and geography selectors). If `collectivite_type=region` and `collectivite_id` is provided, pre-select "region" as type and set the region. This allows the "Soumettre un compte" link from GeographyCard to pre-fill the form.

## Phase 5: User Story 4 — Grille Communes + filtres cascade (P2)

**Goal**: Remplacer le tableau communes par une grille avec filtres cascade province → région.
**Independent Test**: Naviguer `/admin/geography/communes`, voir la grille, sélectionner une province (régions se mettent à jour), sélectionner une région (communes filtrées).

- [x] T009 Refactor communes list page `frontend/app/pages/admin/geography/communes/index.vue` — Replace UiDataTable with grid of GeographyCard. Add two cascade filters: (1) Province `UiFormSelect` populated via `fetchProvinces()` with "Toutes les provinces" default, (2) Region `UiFormSelect` initially showing all regions or empty. When province selected: load regions for that province via `fetchRegions(provinceId)`, reset region filter, load all communes (no region filter yet). When region selected: load communes via `fetchCommunes(regionId)`. When filters cleared: reload all communes. Add client-side search by name. Each card: `type="commune"`, no clickRoute (communes are leaf level), menu ⋮ edit → `/admin/geography/communes/${item.id}`, delete → modal + `deleteCommune(id)`. Keep "Nouvelle commune" button. Grid layout, loading and empty states.

## Phase 6: Polish & Cross-Cutting

**Goal**: Vérifications finales, cohérence visuelle et edge cases.

- [x] T010 Verify route coexistence between `[id].vue` and `[id]/regions.vue` — Test that Nuxt correctly distinguishes between `/admin/geography/provinces/:id` (edit form via `[id].vue`) and `/admin/geography/provinces/:id/regions` (drill-down via `[id]/regions.vue`). Same for regions: `[id].vue` vs `[id]/communes.vue`. If conflicts arise, consider renaming edit pages or using route middleware to disambiguate. Test with actual navigation in the browser.

- [x] T011 [P] Review responsive behavior on all grid pages — Verify all 5 grid pages (provinces index, provinces drill-down, regions index, regions drill-down, communes index) render correctly on mobile (<768px: 1 column), tablet (768-1024px: 2 columns), and desktop (>1024px: 3-4 columns). Verify cards don't overflow, text truncates properly for long names, and the ⋮ menu works on touch devices. Fix any layout issues.

- [x] T012 [P] Review dark mode on all new/modified pages — Verify all new components (GeographyCard, UiDropdownMenu) and modified pages display correctly in both light and dark mode. Check: card backgrounds, borders, text colors, dropdown menu colors, hover states, search input, filter selects, breadcrumb links, empty states. Use CSS variables from the design system (--bg-card, --text-primary, --border-default, etc.).

---

## Dependencies

```
T001 ──┐
       ├──→ T003 → T004 → T005 (US1: provinces grille + drill-down)
T002 ──┘        ↓
                T006 (US2: régions grille — peut commencer après T003 ou en parallèle)
                  ↓
                T007 (US3: données financières — vérifie T002 + T004 + T006)
                T008 (US3: pré-remplissage comptes — indépendant)
                  ↓
                T009 (US4: communes grille — peut commencer après T006 ou en parallèle)
                  ↓
                T010, T011, T012 (Polish — après toutes les pages)
```

## Parallel Execution Opportunities

### Phase 1 (T001 + T002)
Les deux composants de base sont indépendants — exécution en parallèle.

### Phase 2 (T003 → T004 → T005)
Séquentiel : chaque page dépend du composant GeographyCard (T002) et les pages drill-down dépendent de la page parente pour la cohérence de navigation.

### Phase 3 + Phase 4 (T006 + T007 + T008)
T006 (grille régions) peut commencer dès que T001+T002 sont terminés.
T008 (pré-remplissage comptes) est indépendant et peut être fait en parallèle de T006.
T007 est une vérification qui nécessite T002+T004+T006.

### Phase 6 (T010 + T011 + T012)
T011 et T012 sont indépendants et peuvent être exécutés en parallèle.

## Implementation Strategy

### MVP (User Story 1 seule)
T001 → T002 → T003 → T004 → T005
Résultat : grille provinces avec drill-down complet jusqu'aux communes.

### Incremental Delivery
1. **MVP** : US1 (provinces grille + drill-down) — valide le concept
2. **+US2** : Page régions en grille avec filtre province
3. **+US3** : Liens "Données Financières" sur les cartes de région
4. **+US4** : Page communes en grille avec filtres cascade
5. **Polish** : Vérifications responsive, dark mode, routes
