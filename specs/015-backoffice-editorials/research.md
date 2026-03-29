# Research: Section Éditoriaux du Backoffice

**Feature**: 015-backoffice-editorials
**Date**: 2026-03-27

## R1: Modèle de données pour le contenu éditorial

**Decision**: Utiliser 3 modèles distincts plutôt qu'un unique key-value store.

**Rationale**: Le projet possède déjà un modèle `SiteConfiguration` (key/value) mais celui-ci stocke uniquement des valeurs texte simples. Le contenu éditorial nécessite des structures différentes :
- `EditorialContent` : pour les champs texte simples (hero) et contenu riche JSONB (body, footer_about)
- `ContactInfo` : champs structurés spécifiques (email, téléphone, adresse)
- `ResourceLink` : liste ordonnée de liens (titre + URL + sort_order)

**Alternatives considered**:
- Étendre `SiteConfiguration` avec JSONB : rejeté car mélange sémantique et perte de validation au niveau modèle
- Modèle unique avec type discriminant : ajouterait de la complexité inutile pour 3 structures distinctes

## R2: Pattern singleton pour EditorialContent

**Decision**: Utiliser un champ `section_key` unique comme identifiant logique (hero_title, hero_subtitle, hero_description, body_content, footer_about).

**Rationale**: Il n'y a qu'un seul jeu de contenu éditorial pour tout le site. Chaque section est identifiée par sa clé unique. Le pattern existant de `SiteConfiguration` (key unique + value) est réutilisé conceptuellement mais avec des types plus riches.

**Alternatives considered**:
- Un seul enregistrement avec tous les champs : plus simple mais moins flexible pour l'évolution future et les mises à jour partielles
- Table séparée par section (HeroContent, BodyContent, etc.) : trop de tables pour un besoin simple

## R3: Réutilisation des composants EditorJS existants

**Decision**: Réutiliser `RichContentEditor` et `RichContentRenderer` existants sans modification.

**Rationale**: Ces composants sont matures (1000+ lignes), supportent tous les types de blocs requis (titres, textes, images, tableaux, citations, liens), gèrent le dark mode et l'upload d'images. Le schéma `EditorJSData` de validation Pydantic existe déjà dans `schemas/geography.py`.

**Alternatives considered**: Aucune — les composants existants couvrent 100% des besoins.

## R4: Endpoints API — structure

**Decision**: Deux routers distincts : `admin_editorial` (CRUD protégé) et `public_editorial` (lecture seule, non authentifié).

**Rationale**: Cohérent avec le pattern existant (admin_geography / geography, admin_comptes / public_comptes). L'endpoint public retourne tout le contenu éditorial en une seule requête pour minimiser les appels réseau côté frontend.

**Alternatives considered**:
- Un seul router avec des routes mixtes : incohérent avec les conventions du projet

## R5: Organisation de la page admin

**Decision**: Page unique `/admin/editorial` avec composant onglets (tabs) implémenté en Vue natif.

**Rationale**: 3 onglets (Hero Section, Corps de page, Footer) suffisent pour organiser le contenu. Un composant tabs simple est préférable à l'ajout d'une dépendance UI externe. Le formulaire de chaque onglet a son propre bouton "Enregistrer" pour des sauvegardes indépendantes.

**Alternatives considered**:
- Utiliser une lib de tabs (HeadlessUI, etc.) : dépendance supplémentaire non justifiée pour un cas simple

## R6: Chargement dynamique du contenu public

**Decision**: Le contenu éditorial est chargé via un endpoint public unique `/api/editorial` qui retourne tout le contenu en une seule réponse. Côté frontend, `index.vue` et `default.vue` consomment ce contenu.

**Rationale**: Le contenu est petit (quelques Ko) et rarement modifié. Un seul appel API simplifie le frontend. Les valeurs par défaut sont gérées côté frontend si l'API retourne des champs vides.

**Alternatives considered**:
- Endpoints séparés par section : multiplierait les requêtes pour un gain minimal
- SSR avec cache : optimisation prématurée pour ce volume de données
