# Research: Comptes administratifs par région

**Date**: 2026-03-27

## R1 - Support backend des régions dans les comptes administratifs

**Decision**: Aucune modification backend nécessaire.

**Rationale**: Le modèle `CompteAdministratif` utilise déjà un design polymorphe avec `collectivite_type` (enum: province/region/commune) et `collectivite_id` (UUID). Les routers admin (`admin_comptes.py`) et public (`public_comptes.py`) acceptent déjà "region" comme type valide. Le service `compte_service.py` résout le nom de la collectivité via `get_collectivite_name()` qui gère les 3 types.

**Alternatives considered**: Aucune - le backend est déjà prêt.

## R2 - Pattern de pré-remplissage des filtres via query params

**Decision**: Réutiliser le pattern existant de `new.vue` (lignes 49-64) pour `accounts/index.vue`.

**Rationale**: Le formulaire de création (`new.vue`) lit déjà `route.query.collectivite_type` et `route.query.collectivite_id` pour pré-remplir les sélections en cascade (province → région). Ce même mécanisme doit être reproduit sur la page de liste pour que le lien "Voir les comptes" fonctionne. Le pattern inclut : (1) détecter le type, (2) pour une région, récupérer le détail pour trouver la province parente, (3) charger les options en cascade, (4) pré-sélectionner les valeurs.

**Alternatives considered**:
- Créer une sous-page dédiée `/admin/geography/regions/[id]/comptes` → Rejeté car duplication de la logique de liste existante.
- Utiliser un store Pinia pour passer le contexte → Surdimensionné pour ce besoin simple.

## R3 - API publique pour les années de comptes

**Decision**: Utiliser l'endpoint existant `GET /api/public/collectivites/region/{id}/annees`.

**Rationale**: L'API publique expose déjà un endpoint par type de collectivité qui retourne les années d'exercice des comptes publiés. Le format de réponse est `{ annees: number[] }`. Aucun nouvel endpoint n'est nécessaire.

**Alternatives considered**: Aucune - l'API est déjà prête.

## R4 - Templates de comptes pour les régions

**Decision**: Les mêmes templates (recettes/dépenses) s'appliquent aux régions et aux communes.

**Rationale**: Le modèle `AccountTemplate` n'a pas de champ `collectivite_type` - les templates sont génériques. Lors de la création d'un compte, le template actif est utilisé indépendamment du type de collectivité. Ceci est cohérent avec la structure comptable standardisée de Madagascar.

**Alternatives considered**: Ajouter des templates spécifiques par type → Rejeté car pas demandé et le modèle ne le supporte pas.

## R5 - Régions sans communes

**Decision**: Aucune modification nécessaire.

**Rationale**: Le modèle `Region` n'a pas de contrainte imposant des communes. La relation `communes` est un `relationship` côté Region qui retourne simplement une liste vide si aucune commune n'existe. La page publique utilise `v-if="region.communes?.length"` ce qui gère déjà le cas d'une liste vide.

**Alternatives considered**: Aucune - le comportement est déjà correct.
