# Data Model: Comptes administratifs par région

**Date**: 2026-03-27

## Entités existantes (aucune modification)

### CompteAdministratif

Déjà polymorphe - supporte `collectivite_type = "region"`.

| Champ | Type | Description |
|-------|------|-------------|
| id | UUID | Clé primaire |
| collectivite_type | Enum (province/region/commune) | Type de collectivité |
| collectivite_id | UUID | Référence vers la collectivité |
| annee_exercice | Integer | Année d'exercice |
| status | Enum (draft/published) | Statut de publication |
| created_by | UUID (FK → users) | Créateur |
| created_at | DateTime | Date de création |
| updated_at | DateTime | Dernière modification |

**Contrainte d'unicité** : `(collectivite_type, collectivite_id, annee_exercice)`

**Relations** : recette_lines, depense_programs, change_logs

### Region

| Champ | Type | Description |
|-------|------|-------------|
| id | UUID | Clé primaire |
| name | String(255) | Nom de la région |
| code | String(20) | Code unique |
| province_id | UUID (FK → provinces) | Province parente |
| description_json | JSONB | Contenu riche |
| search_vector | TSVECTOR | Index de recherche |

**Relations** : province (parent), communes (enfants - peut être vide)

### AccountTemplate

Templates génériques sans lien au type de collectivité.

| Champ | Type | Description |
|-------|------|-------------|
| id | UUID | Clé primaire |
| name | String(255) | Nom du template |
| type | Enum (recette/depense) | Type |
| version | Integer | Version |
| is_active | Boolean | Actif |

## Migrations

**Aucune migration nécessaire.** Toutes les entités et contraintes existent déjà.

## Diagramme de relations (contexte feature)

```
Province 1──*  Region 1──*  Commune
                 │
                 │ (via collectivite_type="region" + collectivite_id)
                 │
            CompteAdministratif 1──*  RecetteLine
                 │                         │
                 │                    AccountTemplateLine
                 │
                 └──*  DepenseProgram 1──*  DepenseLine
                                              │
                                         AccountTemplateLine
```
