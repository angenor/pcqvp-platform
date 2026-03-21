# Data Model: 006-account-templates

**Date**: 2026-03-20 | **Branch**: `006-account-templates`

## Entities

### AccountTemplate

Represente un modele standardise de tableau de compte administratif.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto-generated | Herite de UUIDBase |
| name | string(255) | NOT NULL | Ex: "Recettes", "Depenses" |
| type | enum | NOT NULL, values: recette/depense | TemplateType enum |
| version | integer | NOT NULL, default 1 | Pour versionning futur |
| is_active | boolean | NOT NULL, default true | Un seul actif par type |
| created_at | timestamp | auto | Herite de UUIDBase |
| updated_at | timestamp | auto on update | |

**Constraints**:
- Unique sur (name, version)
- Index sur type

**Relationships**:
- has_many AccountTemplateLine (cascade delete)
- has_many AccountTemplateColumn (cascade delete)

---

### AccountTemplateLine

Represente un compte dans la hierarchie du template.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto-generated | Herite de UUIDBase |
| template_id | UUID | FK → AccountTemplate.id, NOT NULL | CASCADE delete |
| compte_code | string(10) | NOT NULL | Ex: "70", "708", "7080" |
| intitule | string(500) | NOT NULL | Ex: "IMPOTS SUR LES REVENUS" |
| level | integer | NOT NULL, check 1/2/3 | 1=2 chiffres, 2=3 chiffres, 3=4 chiffres |
| parent_code | string(10) | NULL pour Niv1 | Code du parent (pas FK, reference logique) |
| section | enum | NOT NULL, values: fonctionnement/investissement | SectionType enum |
| sort_order | integer | NOT NULL | Ordre d'affichage dans le template |
| created_at | timestamp | auto | Herite de UUIDBase |

**Constraints**:
- Unique sur (template_id, compte_code)
- Index sur (template_id, level)
- Index sur (template_id, parent_code)
- Index sur (template_id, section)
- Check: level IN (1, 2, 3)

**Validation rules**:
- Si level = 1, parent_code DOIT etre NULL
- Si level = 2, parent_code DOIT exister et correspondre a un code de level 1
- Si level = 3, parent_code DOIT exister et correspondre a un code de level 2
- compte_code unique au sein d'un template

---

### AccountTemplateColumn

Definit une colonne du tableau de compte.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto-generated | Herite de UUIDBase |
| template_id | UUID | FK → AccountTemplate.id, NOT NULL | CASCADE delete |
| name | string(255) | NOT NULL | Ex: "Budget primitif" |
| code | string(50) | NOT NULL | Ex: "budget_primitif", "or_admis" |
| data_type | enum | NOT NULL, values: number/text/percentage | ColumnDataType enum |
| is_computed | boolean | NOT NULL, default false | True pour les colonnes calculees |
| formula | string(500) | NULL | Ex: "budget_primitif + budget_additionnel + modifications" |
| sort_order | integer | NOT NULL | Ordre d'affichage de gauche a droite |
| created_at | timestamp | auto | Herite de UUIDBase |

**Constraints**:
- Unique sur (template_id, code)
- Index sur template_id
- Check: si is_computed = true, formula NOT NULL

**Column definitions per template type**:

#### Recettes (8 colonnes)

| sort | code | name | data_type | is_computed | formula |
|------|------|------|-----------|-------------|---------|
| 1 | budget_primitif | Budget primitif | number | false | - |
| 2 | budget_additionnel | Budget additionnel | number | false | - |
| 3 | modifications | Modifications +/- | number | false | - |
| 4 | previsions_definitives | Previsions definitives | number | true | budget_primitif + budget_additionnel + modifications |
| 5 | or_admis | OR admis | number | false | - |
| 6 | recouvrement | Recouvrement | number | false | - |
| 7 | reste_a_recouvrer | Reste a recouvrer | number | true | or_admis - recouvrement |
| 8 | taux_execution | Taux d'execution | percentage | true | or_admis / previsions_definitives |

#### Depenses (9 colonnes)

| sort | code | name | data_type | is_computed | formula |
|------|------|------|-----------|-------------|---------|
| 1 | budget_primitif | Budget primitif | number | false | - |
| 2 | budget_additionnel | Budget additionnel | number | false | - |
| 3 | modifications | Modifications +/- | number | false | - |
| 4 | previsions_definitives | Previsions definitives | number | true | budget_primitif + budget_additionnel + modifications |
| 5 | engagement | Engagement | number | false | - |
| 6 | mandat_admis | Mandat admis | number | false | - |
| 7 | paiement | Paiement | number | false | - |
| 8 | reste_a_payer | Reste a payer | number | true | mandat_admis - paiement |
| 9 | taux_execution | Taux d'execution | percentage | true | mandat_admis / previsions_definitives |

---

## Enums

```
TemplateType: recette | depense
SectionType: fonctionnement | investissement
ColumnDataType: number | text | percentage
```

## Relationships Diagram

```
AccountTemplate (1)
├── (N) AccountTemplateLine
│   ├── template_id → AccountTemplate.id
│   └── parent_code → (logical ref to sibling line's compte_code)
└── (N) AccountTemplateColumn
    └── template_id → AccountTemplate.id
```

## Aggregation Rules (computed at display time, not stored)

1. **Niv3 → Niv2**: Pour chaque colonne numerique, la valeur d'une ligne Niv2 = SUM des valeurs de ses enfants Niv3 (lignes ayant parent_code = ce Niv2)
2. **Niv2 → Niv1**: Pour chaque colonne numerique, la valeur d'une ligne Niv1 = SUM des valeurs de ses enfants Niv2 (lignes ayant parent_code = ce Niv1)
3. **Section subtotals**: TOTAL Fonctionnement = SUM des Niv1 de section fonctionnement ; TOTAL Investissement = SUM des Niv1 de section investissement
4. **Computed columns**: Appliquees apres l'aggregation (ex: taux = valeur calculee / valeur calculee)

## Migration

Fichier: `003_create_account_template_tables.py`

3 tables a creer:
- `account_templates`
- `account_template_lines`
- `account_template_columns`

Reversible: downgrade supprime les 3 tables dans l'ordre inverse (columns, lines, templates).
