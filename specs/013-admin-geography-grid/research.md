# Research: Navigation Géographique Admin en Grille

**Feature**: 013-admin-geography-grid | **Date**: 2026-03-26

## R1 — Approche de chargement des données (sans pagination)

**Decision**: Utiliser les endpoints publics existants (`fetchProvinces()`, `fetchRegions(provinceId)`, `fetchCommunes(regionId)`) qui retournent toutes les entités sans pagination, plutôt que les endpoints admin paginés (`fetchAdminProvinces` avec skip/limit).

**Rationale**:
- Les endpoints publics retournent déjà toutes les entités d'un coup (pas de skip/limit)
- Madagascar a ~6 provinces, ~23 régions, et un nombre limité de communes par région
- Le filtrage sera côté client (recherche textuelle + filtres)
- Pas besoin de modifier le backend

**Alternatives considered**:
- Endpoints admin avec `limit=9999` — hack, intention pas claire dans le code
- Nouvel endpoint dédié "all" — surcharge inutile vu que les publics suffisent

## R2 — Structure des routes drill-down

**Decision**: Créer des pages Nuxt imbriquées pour le drill-down :
- `/admin/geography/provinces/` — grille de toutes les provinces
- `/admin/geography/provinces/[id]/regions.vue` — régions d'une province
- `/admin/geography/regions/[id]/communes.vue` — communes d'une région

**Rationale**:
- Cohérent avec le système de fichiers Nuxt 4 (file-based routing)
- Les URLs sont partageables et bookmarkables
- L'historique du navigateur (back/forward) fonctionne naturellement
- Le fil d'Ariane peut se construire à partir des segments d'URL

**Alternatives considered**:
- Query params (`?province_id=xxx`) — moins propre, pas de route dédiée
- État local sur la même page — pas bookmarkable, complexité d'état

## R3 — Composant carte pour la grille

**Decision**: Créer un composant `GeographyCard.vue` réutilisable qui affiche une entité géographique (province, région ou commune) avec nom, code, menu contextuel (⋮), et liens optionnels (Voir les comptes pour les régions).

**Rationale**:
- Un seul composant avec des props pour varier le contenu (type, actions)
- Le menu contextuel (⋮) est un pattern standard qui nécessite son propre composant `UiDropdownMenu.vue`
- Pas de `UiCard` générique existant — `GeographyCard` est spécifique au domaine

**Alternatives considered**:
- Composant `UiCard` générique + slot — trop abstrait pour 1 seul use case
- 3 composants séparés (ProvinceCard, RegionCard, CommuneCard) — duplication excessive

## R4 — Navigation "Données Financières" pour les régions

**Decision**: Sur chaque carte de région, ajouter un lien/bouton "Voir les comptes" qui navigue vers `/admin/accounts?collectivite_type=region&collectivite_id={id}`. Le bouton "Soumettre un compte" navigue vers `/admin/accounts/new?collectivite_type=region&collectivite_id={id}`.

**Rationale**:
- La page `/admin/accounts` supporte déjà le filtrage par type et collectivite_id via query params
- La page `/admin/accounts/new` peut être adaptée pour pré-remplir les champs via query params
- Pas de nouvelle page à créer, juste de la navigation avec paramètres

**Alternatives considered**:
- Section dépliable dans la carte — trop complexe visuellement pour une carte
- Page dédiée par région pour les comptes — duplication de la page accounts existante

## R5 — Page Communes : filtres en cascade

**Decision**: Sur la page `/admin/geography/communes`, ajouter deux sélecteurs en cascade :
1. Filtre Province → charge les régions correspondantes
2. Filtre Région → filtre les communes affichées

Le pattern de cascade existe déjà dans la page communes actuelle (via `selectedRegionId`). Il faut ajouter le filtre Province en amont.

**Rationale**:
- `useGeography.fetchProvinces()` et `useGeography.fetchRegions(provinceId)` existent
- `useGeography.fetchCommunes(regionId)` filtre déjà par région
- La page communes actuelle a déjà le filtre région — il suffit d'ajouter le filtre province en amont

**Alternatives considered**:
- Utiliser `fetchHierarchy()` — retourne tout l'arbre, trop lourd pour un filtrage simple
