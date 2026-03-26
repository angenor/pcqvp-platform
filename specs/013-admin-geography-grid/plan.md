# Implementation Plan: Navigation Géographique Admin en Grille

**Branch**: `013-admin-geography-grid` | **Date**: 2026-03-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/013-admin-geography-grid/spec.md`

## Summary

Refonte des pages admin Provinces, Régions et Communes : remplacement des tableaux (`UiDataTable`) par des grilles de cartes (`GeographyCard`), ajout de la navigation drill-down par URL (Province → Régions → Communes), menu contextuel (⋮) pour les actions CRUD, section "Données Financières" sur les cartes de région, et filtres en cascade sur la page Communes. Tout le chargement de données se fait sans pagination. Aucune modification backend.

## Technical Context

**Language/Version**: TypeScript strict (Nuxt 4.4+, Vue 3.5+)
**Primary Dependencies**: Tailwind CSS 4, @nuxtjs/color-mode, @fortawesome/vue-fontawesome (existant)
**Storage**: Aucun nouveau stockage
**Testing**: Validation visuelle manuelle (pas de tests frontend automatisés existants)
**Target Platform**: Web (navigateurs modernes)
**Project Type**: Web application (frontend Nuxt 4)
**Performance Goals**: Chargement identique — pas de pagination, données légères
**Constraints**: Aucune modification backend, routes existantes (edit/create) préservées
**Scale/Scope**: 3 pages modifiées, 2 nouvelles pages drill-down, 2 nouveaux composants

## Constitution Check

Constitution non configurée (template vide). Vérification des contraintes techniques du projet :

| Contrainte | Statut | Justification |
|-----------|--------|---------------|
| Monorepo respecté | ✅ PASS | Changements uniquement dans `frontend/` |
| Tailwind CSS 4 conservé | ✅ PASS | Styles via classes Tailwind |
| Types partagés non impactés | ✅ PASS | Aucune modification des types |
| `useApi` / `useGeography` comme point d'entrée API | ✅ PASS | Utilisation des composables existants |
| Dark/light mode obligatoire | ✅ PASS | Cartes et composants avec classes `dark:` |
| Backend inchangé | ✅ PASS | Aucune modification backend requise |

## Project Structure

### Documentation (this feature)

```text
specs/013-admin-geography-grid/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── contracts/
│   └── routes.md        # Routes & navigation contract
├── quickstart.md        # Phase 1 output
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
frontend/app/
├── components/
│   ├── GeographyCard.vue              # NOUVEAU: carte entité géographique
│   └── ui/
│       └── UiDropdownMenu.vue         # NOUVEAU: menu contextuel (⋮)
├── pages/admin/geography/
│   ├── provinces/
│   │   ├── index.vue                  # MODIFIÉ: tableau → grille de cartes
│   │   ├── [id].vue                   # INCHANGÉ: formulaire edit/create
│   │   └── [id]/
│   │       └── regions.vue            # NOUVEAU: régions d'une province (drill-down)
│   ├── regions/
│   │   ├── index.vue                  # MODIFIÉ: tableau → grille + filtre province + lien comptes
│   │   ├── [id].vue                   # INCHANGÉ: formulaire edit/create
│   │   └── [id]/
│   │       └── communes.vue           # NOUVEAU: communes d'une région (drill-down)
│   └── communes/
│       ├── index.vue                  # MODIFIÉ: tableau → grille + filtres cascade
│       └── [id].vue                   # INCHANGÉ: formulaire edit/create
```

**Structure Decision**: Le composant `GeographyCard` est spécifique au domaine (pas dans `ui/`) car il encode la logique métier géographique (type d'entité, lien comptes, drill-down). Le composant `UiDropdownMenu` est générique et va dans `ui/` car il est réutilisable partout.

## Implementation Phases

### Phase 1 — Composants de base (GeographyCard + UiDropdownMenu)

Créer les 2 nouveaux composants réutilisables :

1. **UiDropdownMenu.vue** — menu contextuel générique avec :
   - Bouton trigger (icône ⋮)
   - Liste d'items avec icône, label, variant (default/danger)
   - Fermeture au clic extérieur
   - Support dark mode
   - Positionnement automatique

2. **GeographyCard.vue** — carte d'entité géographique avec :
   - Affichage nom + code
   - Menu ⋮ (utilise UiDropdownMenu) avec actions Éditer / Supprimer
   - Zone cliquable pour navigation drill-down
   - Slot ou prop pour le lien "Voir les comptes" (régions)
   - Support dark mode + responsive

### Phase 2 — Page Provinces en grille + drill-down

1. **Modifier `provinces/index.vue`** :
   - Remplacer `UiDataTable` par une grille de `GeographyCard`
   - Charger toutes les provinces via `fetchProvinces()`
   - Barre de recherche pour filtrage client
   - Clic carte → `navigateTo(/admin/geography/provinces/${id}/regions)`
   - Menu ⋮ → Éditer / Supprimer (avec modale confirmation)
   - Bouton "Nouvelle province" conservé

2. **Créer `provinces/[id]/regions.vue`** :
   - Charger la province via `fetchProvinceDetail(id)` (inclut les régions)
   - Afficher les régions en grille de `GeographyCard`
   - Fil d'Ariane : Provinces > [Nom Province] > Régions
   - Clic carte région → `/admin/geography/regions/${regionId}/communes`
   - Lien "Voir les comptes" sur chaque carte de région
   - État vide si aucune région

### Phase 3 — Page Régions en grille + drill-down communes

1. **Modifier `regions/index.vue`** :
   - Remplacer `UiDataTable` par grille de `GeographyCard`
   - Charger via `fetchRegions(provinceId?)`
   - Filtre province en haut (sélecteur `UiFormSelect`)
   - Barre de recherche client
   - Chaque carte affiche lien "Voir les comptes"
   - Clic carte → `/admin/geography/regions/${id}/communes`

2. **Créer `regions/[id]/communes.vue`** :
   - Charger la région via `fetchRegionDetail(id)` (inclut les communes)
   - Afficher les communes en grille
   - Fil d'Ariane : Provinces > [Province] > Régions > [Région] > Communes
   - État vide si aucune commune

### Phase 4 — Page Communes en grille + filtres cascade

1. **Modifier `communes/index.vue`** :
   - Remplacer `UiDataTable` par grille de `GeographyCard`
   - Ajouter filtre Province (nouveau) + filtre Région (existant)
   - Cascade : changement province → recharger régions → reset filtre région
   - Charger via `fetchCommunes(regionId?)`
   - Barre de recherche client

## Complexity Tracking

Aucune violation de constitution — feature frontend-only de complexité modérée.

| Risque | Niveau | Mitigation |
|--------|--------|------------|
| Conflit de routes Nuxt ([id].vue vs [id]/regions.vue) | Moyen | Tester que Nuxt distingue correctement les routes dynamiques |
| Performance chargement toutes les communes | Faible | Nombre limité par région ; filtrage côté client rapide |
| Cohérence visuelle avec design system 012 | Faible | Utiliser les variables CSS et classes existantes |
