# Feature Specification: Comptes administratifs par région

**Feature Branch**: `014-region-admin-accounts`
**Created**: 2026-03-27
**Status**: Draft
**Input**: User description: "Les régions ont également des comptes administratifs par année d'exercice. On peut soumettre les comptes administratifs par région, Ajouter 'Voir les comptes' qui renvoie vers les comptes de la région. Ce qui sous-entend qu'une région peut ne pas être liée à une commune."

## Clarifications

### Session 2026-03-27

- Q: Où le lien "Voir les comptes" doit-il pointer ? → A: Vers la page existante `/admin/accounts` avec des query params de filtre (`collectivite_type=region&collectivite_id=<id>`), cohérent avec le pattern de query params déjà utilisé dans le formulaire de création.
- Q: Comment les comptes publiés doivent-ils être présentés sur la page publique d'une région ? → A: Tableau listant les années d'exercice avec un lien "Consulter" vers le détail de chaque compte.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Soumettre un compte administratif pour une région (Priority: P1)

Un administrateur souhaite créer et soumettre un compte administratif pour une région donnée, pour une année d'exercice spécifique. Il sélectionne la région (au lieu d'une commune) lors de la création du compte, remplit les recettes et dépenses selon le template applicable, puis soumet le compte.

**Why this priority**: C'est la fonctionnalité centrale demandée. Sans la possibilité de soumettre des comptes par région, la feature n'a pas de raison d'être.

**Independent Test**: Peut être testé en créant un nouveau compte administratif en sélectionnant une région, en saisissant les données de recettes/dépenses, puis en vérifiant que le compte est bien enregistré et visible.

**Acceptance Scenarios**:

1. **Given** un administrateur connecté sur la page de création de compte, **When** il sélectionne le type de collectivité "Région" et choisit une région, **Then** le formulaire de saisie s'adapte et permet la création du compte pour cette région.
2. **Given** un compte administratif déjà existant pour une région et une année donnée, **When** l'administrateur tente de créer un nouveau compte pour la même région et la même année, **Then** le système refuse la création et affiche un message d'erreur explicite.
3. **Given** un administrateur sur la page de création de compte, **When** il sélectionne une région qui n'a aucune commune rattachée, **Then** la création du compte fonctionne normalement sans erreur.

---

### User Story 2 - Voir les comptes d'une région depuis la fiche région (Priority: P1)

Un administrateur consulte la fiche d'une région dans le backoffice. Il voit un lien/bouton "Voir les comptes" qui le redirige vers la page existante des comptes administratifs, pré-filtrée pour cette région via query params.

**Why this priority**: C'est la navigation essentielle pour accéder aux comptes depuis le contexte géographique, explicitement demandée par l'utilisateur.

**Independent Test**: Peut être testé en naviguant vers la fiche d'une région et en vérifiant la présence et le fonctionnement du lien "Voir les comptes".

**Acceptance Scenarios**:

1. **Given** un administrateur sur la page de détail d'une région, **When** il consulte la page, **Then** il voit un bouton/lien "Voir les comptes" clairement visible.
2. **Given** un administrateur sur la page de détail d'une région, **When** il clique sur "Voir les comptes", **Then** il est redirigé vers `/admin/accounts?collectivite_type=region&collectivite_id=<id>` affichant uniquement les comptes de cette région.
3. **Given** une région sans aucun compte administratif soumis, **When** l'administrateur clique sur "Voir les comptes", **Then** il voit une liste vide avec un message invitant à créer un premier compte.

---

### User Story 3 - Consulter publiquement les comptes d'une région (Priority: P2)

Un visiteur public accède à la page d'une région sur le site. Il voit un tableau listant les années d'exercice des comptes administratifs publiés, chacun avec un lien "Consulter" vers le détail du compte.

**Why this priority**: La consultation publique est importante pour la transparence (mission de PCQVP) mais vient après la capacité d'administrer les données.

**Independent Test**: Peut être testé en accédant à la page publique d'une région et en vérifiant l'affichage des comptes publiés sous forme de tableau.

**Acceptance Scenarios**:

1. **Given** un visiteur sur la page publique d'une région ayant des comptes publiés, **When** il consulte la page, **Then** il voit un tableau des comptes administratifs publiés listant les années d'exercice avec un lien "Consulter" pour chaque compte.
2. **Given** une région avec des comptes en brouillon uniquement, **When** un visiteur consulte la page publique, **Then** aucun compte n'est affiché (seuls les comptes publiés sont visibles).

---

### User Story 4 - Régions sans communes (Priority: P2)

Le système permet qu'une région existe sans être nécessairement liée à des communes. La hiérarchie géographique reste Province > Région > Commune, mais une région peut ne pas avoir de communes rattachées et fonctionner de manière autonome pour la gestion des comptes.

**Why this priority**: C'est une contrainte structurelle nécessaire pour que les régions puissent avoir des comptes indépendamment des communes.

**Independent Test**: Peut être testé en créant une région sans commune et en vérifiant que toutes les fonctionnalités (comptes, navigation, affichage) fonctionnent correctement.

**Acceptance Scenarios**:

1. **Given** une région sans commune rattachée, **When** un administrateur accède à sa fiche, **Then** la page s'affiche normalement sans erreur, la section communes est vide ou indique qu'il n'y a pas de communes.
2. **Given** une région sans commune rattachée, **When** un administrateur crée un compte administratif pour cette région, **Then** le compte est créé sans problème.

---

### Edge Cases

- Que se passe-t-il si une région est supprimée alors qu'elle a des comptes administratifs associés ? Le système doit empêcher la suppression et informer l'utilisateur.
- Comment le système gère-t-il le filtrage des comptes quand on navigue entre les vues "par commune" et "par région" ? La page `/admin/accounts` doit supporter les query params `collectivite_type` et `collectivite_id` pour filtrer dynamiquement.
- Que se passe-t-il si un template de compte (recettes/dépenses) n'existe pas encore pour le type "région" ? Les templates sont génériques (non liés à un type de collectivité), donc les mêmes templates s'appliquent aux régions et aux communes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT permettre la création de comptes administratifs pour le type de collectivité "région", avec les mêmes mécanismes que pour les communes (recettes, dépenses, templates).
- **FR-002**: Le système DOIT afficher un lien "Voir les comptes" sur la fiche administration d'une région, pointant vers `/admin/accounts` avec les query params `collectivite_type=region&collectivite_id=<id>`.
- **FR-003**: La page de liste des comptes (`/admin/accounts`) DOIT supporter le filtrage par query params `collectivite_type` et `collectivite_id` pour afficher uniquement les comptes d'une collectivité donnée.
- **FR-004**: Le système DOIT accepter qu'une région existe sans aucune commune rattachée, sans provoquer d'erreur dans l'interface ou les traitements.
- **FR-005**: La page publique d'une région DOIT afficher un tableau des comptes administratifs publiés, listant les années d'exercice avec un lien "Consulter" vers le détail de chaque compte.
- **FR-006**: Le système DOIT respecter la contrainte d'unicité : un seul compte administratif par région et par année d'exercice.
- **FR-007**: Le formulaire de sélection de collectivité DOIT permettre de choisir entre "Commune" et "Région" lors de la création d'un compte.

### Key Entities

- **Compte Administratif (existant)**: Représente un compte annuel d'une collectivité. Déjà polymorphe via `collectivite_type` (province/region/commune) et `collectivite_id`. La feature exploite le type "region" déjà prévu dans le modèle.
- **Région (existant)**: Entité géographique rattachée à une province. Peut avoir zéro ou plusieurs communes. Devient une collectivité éligible aux comptes administratifs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un administrateur peut créer un compte administratif pour une région en moins de 3 minutes.
- **SC-002**: Le lien "Voir les comptes" est accessible en un seul clic depuis la fiche d'une région.
- **SC-003**: 100% des comptes administratifs de régions publiés sont visibles sur la page publique de la région correspondante.
- **SC-004**: Les régions sans communes rattachées fonctionnent sans erreur dans toutes les interfaces (admin et publique).
- **SC-005**: Le filtrage des comptes par type de collectivité (commune/région) retourne les résultats corrects en moins de 2 secondes.

## Assumptions

- Le modèle `CompteAdministratif` existant supporte déjà le type `collectivite_type = "region"` via l'enum `CollectiviteType`, donc aucune migration de schéma majeure n'est nécessaire.
- Les templates de comptes (recettes/dépenses) sont génériques et s'appliquent indifféremment aux communes et aux régions.
- La relation commune-région reste optionnelle côté région (une région peut exister sans communes), ce qui est déjà le cas dans le modèle actuel.
- Les rôles d'accès (admin/editor) existants s'appliquent de la même manière pour la gestion des comptes par région.
