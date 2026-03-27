# Implementation Plan: Comptes administratifs par région

**Branch**: `014-region-admin-accounts` | **Date**: 2026-03-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/014-region-admin-accounts/spec.md`

## Summary

Activer la gestion complète des comptes administratifs pour les régions. Le backend supporte déjà les régions (`CollectiviteType.region`), le formulaire de création aussi. Les modifications portent sur : (1) pré-remplissage des filtres via query params sur la page de liste admin, (2) ajout du lien "Voir les comptes" sur la fiche région admin, (3) affichage d'un tableau des comptes publiés sur la page publique des régions, (4) validation du bon fonctionnement des régions sans communes.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 async, Nuxt 4, Vue 3.5, Tailwind CSS 4
**Storage**: PostgreSQL 16 via asyncpg
**Testing**: pytest + pytest-asyncio + httpx (backend)
**Target Platform**: Web (serveur Linux, navigateurs modernes)
**Project Type**: Web application (monorepo backend + frontend)
**Performance Goals**: < 2s pour le filtrage des comptes
**Constraints**: Dark/light mode obligatoire, composable `useApi` pour les appels API
**Scale/Scope**: ~22 régions de Madagascar, ~1600 communes

## Constitution Check

*GATE: Constitution non configurée (template vide). Pas de gates à vérifier.*

## Project Structure

### Documentation (this feature)

```text
specs/014-region-admin-accounts/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   └── compte_administratif.py  # Existant - aucune modification nécessaire
│   ├── routers/
│   │   ├── admin_comptes.py         # Existant - supporte déjà les régions
│   │   └── public_comptes.py        # Existant - supporte déjà les régions
│   └── services/
│       ├── compte_service.py        # Existant - supporte déjà les régions
│       └── public_service.py        # Existant - supporte déjà les régions
└── tests/

frontend/
└── app/
    ├── pages/
    │   ├── admin/
    │   │   ├── accounts/
    │   │   │   └── index.vue        # MODIFIER - lire query params pour pré-filtrage
    │   │   └── geography/
    │   │       └── regions/
    │   │           └── [id]/
    │   │               └── index.vue  # MODIFIER - ajouter lien "Voir les comptes"
    │   └── regions/
    │       └── [id].vue             # MODIFIER - ajouter tableau comptes publiés
    └── composables/
        └── useComptes.ts            # Existant - aucune modification nécessaire
```

**Structure Decision**: Monorepo existant backend/frontend. Aucun nouveau fichier nécessaire : uniquement des modifications sur 3 fichiers frontend existants. Le backend ne nécessite aucun changement.

## Fichiers à modifier

### 1. `frontend/app/pages/admin/accounts/index.vue`

**Objectif** : Lire les query params `collectivite_type` et `collectivite_id` au montage pour pré-remplir les filtres.

**Changements** :
- Dans `onMounted`, lire `route.query.collectivite_type` et `route.query.collectivite_id`
- Si `collectivite_type=region` et `collectivite_id` présents : trouver la province parente, charger les régions, pré-sélectionner le type et la région
- Pattern identique à celui déjà utilisé dans `new.vue` (lignes 49-64)

### 2. `frontend/app/pages/admin/geography/regions/[id]/index.vue`

**Objectif** : Ajouter un bouton "Voir les comptes" sur la page d'édition d'une région.

**Changements** :
- Ajouter un `UiButton` avec lien vers `/admin/accounts?collectivite_type=region&collectivite_id=${route.params.id}`
- Placement : dans la zone d'actions en haut de page (à côté de "Annuler") ou sous le formulaire

### 3. `frontend/app/pages/regions/[id].vue`

**Objectif** : Afficher un tableau des comptes administratifs publiés sur la page publique de la région.

**Changements** :
- Appeler l'API publique `GET /api/public/collectivites/region/{id}/annees` pour récupérer les années disponibles
- Afficher un tableau : colonne "Année d'exercice" + colonne "Action" avec lien "Consulter"
- Le lien "Consulter" pointe vers la page de détail du compte publié (pattern existant à vérifier sur les pages communes/provinces)
- Gérer l'état vide (aucun compte publié)
- Respecter dark/light mode avec les classes Tailwind `dark:`

## Risques et mitigations

| Risque | Probabilité | Mitigation |
|--------|-------------|------------|
| Les filtres query params interfèrent avec les watchers existants | Faible | Initialiser les valeurs avant d'activer les watchers (même pattern que `new.vue`) |
| Page publique région sans gestion du cas "0 comptes" | Faible | Afficher un message "Aucun compte disponible" |
| Régions sans communes causent des erreurs | Très faible | Le code actuel gère déjà ce cas (`v-if="region.communes?.length"`) |
