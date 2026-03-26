# Quickstart: Back-Office Design Upgrade

**Feature**: 012-backoffice-design-upgrade | **Date**: 2026-03-22

## Prérequis

- Node.js 18+
- pnpm installé
- Le projet frontend dans `apps/frontend/`

## Setup rapide

```bash
# 1. Se positionner dans le frontend
cd apps/frontend

# 2. Installer les nouvelles dépendances (FontAwesome)
pnpm add @fortawesome/fontawesome-svg-core @fortawesome/free-solid-svg-icons @fortawesome/free-regular-svg-icons @fortawesome/vue-fontawesome

# 3. Lancer le dev server
pnpm dev
```

## Ordre d'implémentation recommandé

### Étape 1 : Fondations (design system + polices)
1. Ajouter les polices Google Fonts dans `nuxt.config.ts` (app.head.link)
2. Réécrire `app/assets/css/main.css` avec les variables CSS (tokens)
3. Configurer le plugin FontAwesome (`app/plugins/fontawesome.ts`)

### Étape 2 : Composants UI
4. Créer les composants `components/ui/` (UiButton, UiBadge, UiFormInput, UiFormSelect, UiFormTextarea, UiAlert, UiLoadingSpinner, UiStatCard, UiModal, UiDataTable)

### Étape 3 : Layout admin
5. Créer le composable `composables/useSidebar.ts`
6. Créer `components/admin/AdminSidebar.vue`
7. Créer `components/admin/AdminHeader.vue`
8. Créer `components/admin/AdminBreadcrumb.vue`
9. Refactoriser `layouts/admin.vue` pour utiliser les nouveaux composants

### Étape 4 : Migration des pages
10. Dashboard (`admin/index.vue`) — utilise UiStatCard
11. Pages géographie (6 pages) — utilise UiDataTable, UiFormInput, UiModal, UiButton
12. Pages comptes (5 pages) — adapte AccountDataTable, RecapTable, EquilibreTable au design system
13. Pages templates (2 pages) — utilise UiDataTable, UiModal
14. Pages outils (4 pages : users, newsletter, analytics, config) — utilise UiDataTable, UiBadge, UiButton

### Étape 5 : Adaptation composants existants
15. Adapter les 9 composants existants au design system (remplacer classes Tailwind en dur par variables CSS)

## Vérification

```bash
# Lancer le serveur de dev
cd apps/frontend && pnpm dev

# Vérifier visuellement :
# - http://localhost:3000/admin → Dashboard avec nouvelles polices + couleurs
# - Tester le toggle mode sombre
# - Tester la sidebar (déplier/replier)
# - Naviguer sur chaque page admin pour vérifier la cohérence
# - Tester sur mobile (DevTools responsive)
```

## Fichiers clés à consulter comme référence

| Fichier référence (ancienne plateforme) | Usage |
|----------------------------------------|-------|
| `collectivites_territoriales/frontend_collectivites_territoriales/app/assets/css/main.css` | Design system complet (variables CSS, palette, typographie) |
| `collectivites_territoriales/frontend_collectivites_territoriales/app/components/ui/` | Composants UI de référence |
| `collectivites_territoriales/frontend_collectivites_territoriales/app/components/admin/Sidebar.vue` | Sidebar de référence |
| `collectivites_territoriales/frontend_collectivites_territoriales/app/plugins/fontawesome.ts` | Configuration FontAwesome |
