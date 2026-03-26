# Data Model: Saisie et stockage des comptes administratifs

**Date**: 2026-03-21 | **Branch**: `007-admin-accounts-entry`

## Entity Relationship Diagram (textual)

```
User (existing)
  |
  |-- created_by
  v
CompteAdministratif ──> Province/Region/Commune (polymorphic, validated at service level)
  |
  |-- 1:N
  ├── RecetteLine ──> AccountTemplateLine (existing, FK)
  |
  |-- 1:N
  ├── DepenseProgram
  |     |-- 1:N
  |     └── DepenseLine ──> AccountTemplateLine (existing, FK)
  |
  |-- 1:N
  └── AccountChangeLog ──> User (FK)
```

## Entities

### CompteAdministratif

Represente le document comptable annuel d'une collectivite territoriale.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto | Herite de UUIDBase |
| collectivite_type | Enum('province', 'region', 'commune') | NOT NULL, indexed | Type de la collectivite |
| collectivite_id | UUID | NOT NULL, indexed | ID polymorphique (pas de FK DB, validation service) |
| annee_exercice | Integer | NOT NULL | Annee du compte |
| status | Enum('draft', 'published') | NOT NULL, default='draft' | Cycle de vie |
| created_by | UUID | FK → users.id, NOT NULL | Utilisateur createur |
| created_at | DateTime | auto (UUIDBase) | |
| updated_at | DateTime | nullable, onupdate | |

**Constraints**:
- UNIQUE(collectivite_type, collectivite_id, annee_exercice) — un seul compte par collectivite et annee
- Index composite sur (collectivite_type, collectivite_id)
- Index sur annee_exercice

**State Transitions**:
```
draft ←→ published (admin only, bidirectionnel)
```
La saisie reste possible dans les deux etats. Les modifications en etat "published" sont tracees dans AccountChangeLog.

### RecetteLine

Valeurs financieres saisies pour une ligne de recette.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto | Herite de UUIDBase |
| compte_admin_id | UUID | FK → comptes_administratifs.id, CASCADE, NOT NULL | |
| template_line_id | UUID | FK → account_template_lines.id, RESTRICT, NOT NULL | Reference la structure |
| values | JSONB | NOT NULL, default={} | Cles: budget_primitif, budget_additionnel, modifications, or_admis, recouvrement |
| created_at | DateTime | auto | |
| updated_at | DateTime | nullable, onupdate | |

**Constraints**:
- UNIQUE(compte_admin_id, template_line_id) — une seule valeur par ligne de template par compte

**Validation rules**:
- Les cles du JSONB values doivent correspondre aux codes des colonnes non-calculees du template recettes
- Les valeurs doivent etre des entiers (Ariary, pas de decimales)
- template_line_id doit referencer une ligne du template actif de type "recette"

### DepenseProgram

Programme budgetaire au sein d'un compte administratif.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto | Herite de UUIDBase |
| compte_admin_id | UUID | FK → comptes_administratifs.id, CASCADE, NOT NULL | |
| numero | Integer | NOT NULL | Numero d'ordre (1, 2, 3, ...) |
| intitule | String(255) | NOT NULL | Nom du programme |
| created_at | DateTime | auto | |
| updated_at | DateTime | nullable, onupdate | |

**Constraints**:
- UNIQUE(compte_admin_id, numero) — un seul programme par numero par compte

**Default programs** (crees automatiquement a la creation du compte):
1. "Administration et Coordination"
2. "Developpement economique et social"
3. "Sante"

### DepenseLine

Valeurs financieres saisies pour une ligne de depense au sein d'un programme.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto | Herite de UUIDBase |
| programme_id | UUID | FK → depense_programs.id, CASCADE, NOT NULL | |
| template_line_id | UUID | FK → account_template_lines.id, RESTRICT, NOT NULL | Reference la structure |
| values | JSONB | NOT NULL, default={} | Cles: budget_primitif, budget_additionnel, modifications, engagement, mandat_admis, paiement |
| created_at | DateTime | auto | |
| updated_at | DateTime | nullable, onupdate | |

**Constraints**:
- UNIQUE(programme_id, template_line_id) — une seule valeur par ligne de template par programme

**Validation rules**:
- Les cles du JSONB values doivent correspondre aux codes des colonnes non-calculees du template depenses
- Les valeurs doivent etre des entiers
- template_line_id doit referencer une ligne du template actif de type "depense"

### AccountChangeLog

Journal des modifications effectuees sur un compte publie.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID | PK, auto | Herite de UUIDBase |
| compte_admin_id | UUID | FK → comptes_administratifs.id, CASCADE, NOT NULL | |
| user_id | UUID | FK → users.id, NOT NULL | Auteur de la modification |
| change_type | String(50) | NOT NULL | recette_update, depense_update, status_change, programme_add, programme_update, programme_delete |
| detail | JSONB | NOT NULL | Contenu variable selon change_type |
| created_at | DateTime | auto | |

**Constraints**:
- Index sur (compte_admin_id, created_at) pour requetes chronologiques

**Detail JSONB examples**:
```json
// recette_update
{"template_line_id": "uuid", "compte_code": "7080", "column": "budget_primitif", "old_value": 0, "new_value": 1017922}

// depense_update
{"programme_id": "uuid", "template_line_id": "uuid", "compte_code": "6010", "column": "mandat_admis", "old_value": 0, "new_value": 5000000}

// status_change
{"old_status": "published", "new_status": "draft"}

// programme_add
{"programme_id": "uuid", "numero": 4, "intitule": "Nouveau programme"}

// programme_delete
{"programme_id": "uuid", "numero": 2, "intitule": "Developpement economique et social"}
```

## Enums

```
CollectiviteType: province | region | commune
CompteStatus: draft | published
```

Note: `TemplateType` (recette | depense), `SectionType` (fonctionnement | investissement), et `ColumnDataType` (number | text | percentage) existent deja dans le modele AccountTemplate (Feature 006).

## Computed Fields (non persistes)

Les champs suivants sont calcules dynamiquement par `account_service.py` a chaque GET :

### Par ligne (RecetteLine / DepenseLine)
- `previsions_definitives` = budget_primitif + budget_additionnel + modifications
- `reste_a_recouvrer` (recettes) = or_admis - recouvrement
- `reste_a_payer` (depenses) = mandat_admis - paiement
- `taux_execution` (recettes) = or_admis / previsions_definitives (ou null si denominateur = 0)
- `taux_execution` (depenses) = mandat_admis / previsions_definitives (ou null si denominateur = 0)

### Sommes hierarchiques
- Lignes Niv2 = somme des Niv3 enfants
- Lignes Niv1 = somme des Niv2 enfants
- Sous-total section = somme des Niv1 de la section

### Recapitulatifs
- Recap recettes : agregation Niv1 par section
- Recap depenses : croisement comptes (Niv1) x programmes (mandat, paiement, reste a payer)
- Equilibre : recettes vs depenses par section, avec separation operations reelles / operations d'ordre
