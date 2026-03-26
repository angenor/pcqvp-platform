# Routes & Navigation Contract

**Feature**: 013-admin-geography-grid | **Date**: 2026-03-26

## Nouvelles routes frontend (Nuxt file-based routing)

| Route | Fichier | Description |
|-------|---------|-------------|
| `/admin/geography/provinces` | `provinces/index.vue` | Grille de toutes les provinces (MODIFIÉ) |
| `/admin/geography/provinces/:id/regions` | `provinces/[id]/regions.vue` | Grille des régions d'une province (NOUVEAU) |
| `/admin/geography/regions` | `regions/index.vue` | Grille de toutes les régions avec filtre province (MODIFIÉ) |
| `/admin/geography/regions/:id/communes` | `regions/[id]/communes.vue` | Grille des communes d'une région (NOUVEAU) |
| `/admin/geography/communes` | `communes/index.vue` | Grille de toutes les communes avec filtres cascade (MODIFIÉ) |

## Routes existantes conservées (non modifiées)

| Route | Fichier | Description |
|-------|---------|-------------|
| `/admin/geography/provinces/new` | `provinces/[id].vue` | Formulaire création province |
| `/admin/geography/provinces/:id` | `provinces/[id].vue` | Formulaire édition province |
| `/admin/geography/regions/new` | `regions/[id].vue` | Formulaire création région |
| `/admin/geography/regions/:id` | `regions/[id].vue` | Formulaire édition région |
| `/admin/geography/communes/new` | `communes/[id].vue` | Formulaire création commune |
| `/admin/geography/communes/:id` | `communes/[id].vue` | Formulaire édition commune |

## Navigations inter-pages (liens)

### Depuis la grille Provinces
- **Clic sur carte** → `/admin/geography/provinces/:id/regions`
- **Menu ⋮ > Éditer** → `/admin/geography/provinces/:id`
- **Bouton "Nouvelle province"** → `/admin/geography/provinces/new`

### Depuis la grille Régions d'une Province
- **Clic sur carte région** → `/admin/geography/regions/:id/communes`
- **Menu ⋮ > Éditer** → `/admin/geography/regions/:id`
- **Voir les comptes** → `/admin/accounts?collectivite_type=region&collectivite_id=:id`
- **Soumettre un compte** → `/admin/accounts/new?collectivite_type=region&collectivite_id=:id`
- **Fil d'Ariane > Provinces** → `/admin/geography/provinces`

### Depuis la grille Régions (page principale)
- **Clic sur carte** → `/admin/geography/regions/:id/communes`
- **Menu ⋮ > Éditer** → `/admin/geography/regions/:id`
- **Voir les comptes** → `/admin/accounts?collectivite_type=region&collectivite_id=:id`
- **Bouton "Nouvelle région"** → `/admin/geography/regions/new`

### Depuis la grille Communes d'une Région
- **Menu ⋮ > Éditer** → `/admin/geography/communes/:id`
- **Fil d'Ariane > Provinces** → `/admin/geography/provinces`
- **Fil d'Ariane > [Province]** → `/admin/geography/provinces/:provinceId/regions`
- **Fil d'Ariane > [Région]** → (page actuelle)

### Depuis la grille Communes (page principale)
- **Menu ⋮ > Éditer** → `/admin/geography/communes/:id`
- **Bouton "Nouvelle commune"** → `/admin/geography/communes/new`

## API Endpoints utilisés (existants, aucune modification)

| Endpoint | Méthode | Usage |
|----------|---------|-------|
| `/api/provinces` | GET | Charger toutes les provinces |
| `/api/provinces/:id` | GET | Détail province (avec régions) |
| `/api/regions` | GET | Charger toutes les régions |
| `/api/regions?province_id=:id` | GET | Régions d'une province |
| `/api/regions/:id` | GET | Détail région (avec communes) |
| `/api/communes` | GET | Charger toutes les communes |
| `/api/communes?region_id=:id` | GET | Communes d'une région |
| `/api/admin/provinces/:id` | DELETE | Supprimer une province |
| `/api/admin/regions/:id` | DELETE | Supprimer une région |
| `/api/admin/communes/:id` | DELETE | Supprimer une commune |
