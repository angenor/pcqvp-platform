# Research: Saisie et stockage des comptes administratifs

**Date**: 2026-03-21 | **Branch**: `007-admin-accounts-entry`

## R1 : Stockage polymorphique de collectivite_id

**Decision**: Utiliser un couple `collectivite_type` (Enum) + `collectivite_id` (UUID) sans FK reelle en base, avec validation applicative dans le service.

**Rationale**: Le modele existant (Province, Region, Commune) utilise 3 tables distinctes sans table commune. Une FK polymorphique vers 3 tables n'est pas supportee nativement par PostgreSQL. La validation au niveau service (lookup de l'entite avant creation) est le pattern le plus simple et le projet l'utilise deja pour d'autres validations metier.

**Alternatives considered**:
- Table `collectivites` commune avec heritage (STI) : trop de refactoring sur le modele geographique existant
- FK conditionnelles (province_id, region_id, commune_id nullable) : 3 colonnes dont 2 toujours NULL, complexite inutile
- Generic FK avec content_type : sur-ingenierie pour ce cas d'usage

## R2 : Auto-save ligne par ligne

**Decision**: Endpoint PUT par ligne (upsert). Le frontend envoie un PUT avec `template_line_id` et les valeurs JSONB a chaque blur de cellule. Le backend fait un upsert (INSERT ON CONFLICT UPDATE).

**Rationale**: L'auto-save cellule par cellule genererait trop de requetes (5-6 colonnes editables par ligne). Le save par ligne est le bon compromis : une requete par changement de ligne, coherence des donnees d'une ligne garantie.

**Alternatives considered**:
- Save par cellule : trop de requetes reseau, risque d'incoherence intra-ligne
- Save par section complete (toutes les lignes) : trop lourd pour 289 lignes, mauvais UX pour auto-save
- WebSocket pour sync temps reel : sur-ingenierie, pas de collaboration simultanee prevue

## R3 : Calculs dynamiques cote serveur

**Decision**: Tous les calculs (colonnes derivees, sommes hierarchiques, recapitulatifs, equilibre) sont effectues dans `account_service.py` a chaque requete GET, jamais persistes.

**Rationale**: Conforme a la spec (FR-009, FR-010). Les donnees sources (values JSONB) sont les seules a etre stockees. Cela garantit la coherence et evite les problemes de desynchronisation entre donnees brutes et calculs.

**Alternatives considered**:
- Materialized views PostgreSQL : complexite d'invalidation pour l'auto-save, pas necessaire pour <300 lignes
- Calculs cote frontend : risque de divergence avec le backend, impossible pour les recapitulatifs

## R4 : Pattern JSONB pour les valeurs

**Decision**: Stocker les valeurs de chaque ligne dans une colonne JSONB `values` avec les codes de colonnes comme cles (ex: `{"budget_primitif": 1017922, "budget_additionnel": 0}`).

**Rationale**: Pattern identique a celui specifie dans la description de la feature. Flexible pour des colonnes qui varient entre recettes et depenses. Les cles correspondent aux `code` des `AccountTemplateColumn` existantes.

**Alternatives considered**:
- Colonnes individuelles (budget_primitif INT, budget_additionnel INT, ...) : rigide, necessite une migration a chaque ajout de colonne
- Table de pivot (ligne_id, colonne_code, valeur) : surcharge de lignes, jointures complexes

## R5 : Journal des modifications (FR-020)

**Decision**: Table `account_change_logs` avec colonnes simples : compte_admin_id, user_id, change_type, detail (JSONB), created_at. Le journal est alimente uniquement quand le compte est en statut "published".

**Rationale**: Conforme a la clarification spec : tracer les modifications sur comptes publies uniquement. Le JSONB permet de stocker le detail heterogene (recette vs depense vs programme vs status).

**Alternatives considered**:
- Trigger PostgreSQL : opaque et difficile a tester
- Event sourcing complet : sur-ingenierie pour ce besoin simple

## R6 : Distinction operations reelles vs operations d'ordre

**Decision**: Utiliser la structure du template existant. Les lignes de template ont deja un `sort_order` et une `section`. Les operations d'ordre sont les lignes positionnees apres le sous-total des operations reelles dans chaque section. Le service de calcul utilise cette position pour separer reelles/ordre dans l'equilibre.

**Rationale**: Conforme a la clarification spec et au document officiel Andrafiabe. La structure du template (Feature 006) encode deja cette information par l'ordonnancement des lignes.

**Alternatives considered**:
- Ajouter un champ `operation_type` (reelle/ordre) sur AccountTemplateLine : modification de la Feature 006, augmente le scope
- Convention par code comptable (comptes 10x, 11x = ordre) : fragile et non explicite

## R7 : Composant de saisie reutilisable

**Decision**: Un composant `AccountDataTable.vue` partage entre recettes et depenses. Il recoit les lignes du template, les colonnes editables, et les valeurs. Il emet un evenement `@save-line` quand une ligne est modifiee.

**Rationale**: Les tableaux de recettes et depenses ont la meme structure hierarchique et le meme comportement (lignes editables Niv3, sommes Niv1/Niv2, colonnes calculees). Seules les colonnes different. Un composant partage evite la duplication.

**Alternatives considered**:
- Deux composants distincts (RecetteTable, DepenseTable) : duplication de 90% du code
- Librairie tierce de data grid : dependance lourde, pas necessaire pour un tableau de saisie simple
