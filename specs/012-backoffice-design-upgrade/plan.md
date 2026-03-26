# Implementation Plan: Back-Office Design Upgrade

**Branch**: `012-backoffice-design-upgrade` | **Date**: 2026-03-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/012-backoffice-design-upgrade/spec.md`

## Summary

Refonte visuelle complète du back-office admin en s'inspirant du design de l'ancienne plateforme `collectivites_territoriales/`. Les changements sont purement frontend : mise en place d'un design system centralisé (CSS variables, palette TI Madagascar), adoption des polices Barlow Condensed/Inter/JetBrains Mono (globalement), création d'une bibliothèque de composants UI réutilisables (Button, Badge, StatCard, DataTable, Modal, FormInput), refonte du layout admin (sidebar repliable + header professionnel), et migration complète des 19 pages admin existantes vers les nouveaux composants. FontAwesome est ajouté comme système d'icônes. Aucune modification backend.

## Technical Context

**Language/Version**: TypeScript strict (Nuxt 4.4+, Vue 3.5+)
**Primary Dependencies**: Tailwind CSS 4, @nuxtjs/color-mode, @fortawesome/fontawesome-svg-core + vue-fontawesome (à ajouter), Google Fonts (Barlow Condensed, Inter, JetBrains Mono)
**Storage**: localStorage (persistance état sidebar)
**Testing**: Vitest (existant mais pas de tests frontend actuels — validation visuelle manuelle)
**Target Platform**: Web (navigateurs modernes)
**Project Type**: Web application (frontend Nuxt 4)
**Performance Goals**: Temps de chargement additionnel < 500ms (polices + icônes)
**Constraints**: Aucune modification backend, toutes les fonctionnalités existantes préservées
**Scale/Scope**: 19 pages admin à migrer, 9 composants existants à adapter, ~10 nouveaux composants UI à créer

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principe | Statut | Justification |
|----------|--------|---------------|
| I. Données Ouvertes & Transparence | ✅ PASS | Aucun changement sur les données ou l'API — design uniquement |
| II. Sécurité & Confidentialité | ✅ PASS | Aucun changement d'authentification ou d'autorisation |
| III. Simplicité & Maintenabilité | ✅ PASS | Les composants réutilisables et le design system centralisé améliorent la maintenabilité. Les abstractions (Button, Badge, etc.) sont justifiées par une utilisation concrète sur 19+ pages |

**Contraintes techniques** :
- ✅ Monorepo respecté — changements uniquement dans `apps/frontend/`
- ✅ Tailwind CSS 4 conservé comme framework CSS
- ✅ Types partagés `packages/shared/` non impactés
- ✅ `useApi` reste le point d'entrée API unique

## Project Structure

### Documentation (this feature)

```text
specs/012-backoffice-design-upgrade/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (composants UI)
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
apps/frontend/
├── app/
│   ├── assets/
│   │   └── css/
│   │       └── main.css              # Design system: CSS variables, polices, tokens
│   ├── components/
│   │   ├── ui/                       # NOUVEAU: Composants UI réutilisables
│   │   │   ├── UiButton.vue
│   │   │   ├── UiBadge.vue
│   │   │   ├── UiStatCard.vue
│   │   │   ├── UiDataTable.vue
│   │   │   ├── UiModal.vue
│   │   │   ├── UiFormInput.vue
│   │   │   ├── UiFormSelect.vue
│   │   │   ├── UiFormTextarea.vue
│   │   │   ├── UiAlert.vue
│   │   │   └── UiLoadingSpinner.vue
│   │   ├── admin/                    # NOUVEAU: Composants layout admin
│   │   │   ├── AdminSidebar.vue
│   │   │   ├── AdminHeader.vue
│   │   │   └── AdminBreadcrumb.vue
│   │   ├── AccountDataTable.vue      # EXISTANT: adapté au design system
│   │   ├── RecapTable.vue            # EXISTANT: adapté au design system
│   │   ├── EquilibreTable.vue        # EXISTANT: adapté au design system
│   │   ├── GeographySelector.vue     # EXISTANT: adapté au design system
│   │   ├── RichContentEditor.vue     # EXISTANT: adapté au design system
│   │   ├── RichContentRenderer.vue   # EXISTANT: adapté au design system
│   │   ├── SearchBar.vue             # EXISTANT: adapté au design system
│   │   ├── NewsletterForm.vue        # EXISTANT: adapté au design system
│   │   └── AccountTable.vue          # EXISTANT: adapté au design system
│   ├── composables/
│   │   └── useSidebar.ts             # NOUVEAU: état sidebar (collapsed/expanded + localStorage)
│   ├── layouts/
│   │   └── admin.vue                 # MODIFIÉ: utilise AdminSidebar + AdminHeader
│   ├── pages/admin/                  # MODIFIÉ: 19 pages migrées vers composants UI
│   └── plugins/
│       └── fontawesome.ts            # NOUVEAU: configuration FontAwesome
├── nuxt.config.ts                    # MODIFIÉ: ajout polices Google Fonts
└── package.json                      # MODIFIÉ: ajout dépendances FontAwesome
```

**Structure Decision**: Les nouveaux composants UI sont dans `components/ui/` (préfixe `Ui` pour auto-import Nuxt sans conflit). Les composants spécifiques au layout admin sont dans `components/admin/`. Les composants existants restent à la racine de `components/` et sont adaptés pour utiliser les variables CSS du design system.

## Complexity Tracking

Aucune violation de constitution — pas de tracking nécessaire.
