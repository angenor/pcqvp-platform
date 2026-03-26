# Quickstart: Navigation Géographique Admin en Grille

**Feature**: 013-admin-geography-grid | **Date**: 2026-03-26

## Prérequis

- Backend lancé (`uvicorn app.main:app --reload`)
- Base de données avec des provinces, régions et communes existantes
- Frontend lancé (`pnpm dev`)

## Vérification rapide

1. **Grille Provinces** : Aller sur `http://localhost:3000/admin/geography/provinces`
   - Les provinces doivent s'afficher en cartes dans une grille
   - Chaque carte a un nom, code et menu ⋮

2. **Drill-down Province → Régions** : Cliquer sur une carte de province
   - Redirigé vers `/admin/geography/provinces/:id/regions`
   - Les régions de cette province s'affichent en grille
   - Fil d'Ariane : Provinces > [Nom Province] > Régions

3. **Drill-down Région → Communes** : Cliquer sur une carte de région
   - Redirigé vers `/admin/geography/regions/:id/communes`
   - Les communes de cette région s'affichent en grille

4. **Grille Régions** : Aller sur `/admin/geography/regions`
   - Toutes les régions en grille
   - Filtre par province fonctionne
   - Lien "Voir les comptes" visible sur chaque carte

5. **Grille Communes** : Aller sur `/admin/geography/communes`
   - Filtres cascade Province → Région fonctionnent

6. **CRUD via menu ⋮** : Sur n'importe quelle carte
   - Cliquer ⋮ → "Éditer" navigue vers le formulaire existant
   - Cliquer ⋮ → "Supprimer" ouvre la modale de confirmation

7. **Données Financières** : Sur une carte de région
   - "Voir les comptes" redirige vers `/admin/accounts?collectivite_type=region&collectivite_id=:id`

## Fichiers clés modifiés

```
frontend/app/
├── components/
│   ├── GeographyCard.vue              # NOUVEAU
│   └── ui/UiDropdownMenu.vue          # NOUVEAU
├── pages/admin/geography/
│   ├── provinces/
│   │   ├── index.vue                  # MODIFIÉ → grille
│   │   └── [id]/
│   │       └── regions.vue            # NOUVEAU
│   ├── regions/
│   │   ├── index.vue                  # MODIFIÉ → grille + filtre
│   │   └── [id]/
│   │       └── communes.vue           # NOUVEAU
│   └── communes/
│       └── index.vue                  # MODIFIÉ → grille + filtres cascade
```
