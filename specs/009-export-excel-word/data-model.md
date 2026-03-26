# Data Model: Export Excel & Word

**Date**: 2026-03-21 | **Feature**: 009-export-excel-word

## Aucune nouvelle table

Cette feature est en lecture seule. Elle exploite les entites existantes des Features 006 et 007 :

## Entites existantes utilisees

### CompteAdministratif
- `id` (UUID, PK)
- `collectivite_type` (enum: province/region/commune)
- `collectivite_id` (UUID)
- `annee_exercice` (int)
- `status` (enum: draft/published)
- Relations : `recette_lines`, `depense_programs`

### RecetteLine
- `id` (UUID, PK)
- `compte_admin_id` (UUID, FK → comptes_administratifs)
- `template_line_id` (UUID, FK → account_template_lines)
- `values` (JSONB) : `{budget_primitif, budget_additionnel, modifications, or_admis, recouvrement}`

### DepenseProgram
- `id` (UUID, PK)
- `compte_admin_id` (UUID, FK → comptes_administratifs)
- `numero` (int)
- `intitule` (str)
- Relations : `depense_lines`

### DepenseLine
- `id` (UUID, PK)
- `programme_id` (UUID, FK → depense_programs)
- `template_line_id` (UUID, FK → account_template_lines)
- `values` (JSONB) : `{budget_primitif, budget_additionnel, modifications, engagement, mandat_admis, paiement}`

### AccountTemplateLine
- `compte_code` (str)
- `intitule` (str)
- `level` (int: 1, 2, 3)
- `parent_code` (str | null)
- `section` (enum: fonctionnement/investissement)
- `sort_order` (int)

### Geographie (Province / Region / Commune)
- `id` (UUID, PK)
- `name` (str) — utilise pour le nommage des fichiers exportes

## Flux de donnees pour l'export

```
CompteAdministratif (publie)
    │
    ├── get_recettes_with_computed()
    │   └── lines[] + hierarchical_sums{} + computed{taux_execution}
    │
    ├── get_depenses_with_computed()
    │   └── programmes[].lines[] + hierarchical_sums{} + computed{taux_execution}
    │
    ├── calculate_recettes_recap()
    │   └── sections[].categories[] + total_section{}
    │
    ├── calculate_depenses_recap()
    │   └── sections[].categories[].programmes[] + total_section{}
    │
    ├── calculate_equilibre()
    │   └── fonctionnement/investissement{depenses, recettes, excedent} + resultat_definitif
    │
    └── get_collectivite_name()
        └── nom de la collectivite pour le titre et le nom de fichier
```

## Colonnes calculees (pas de formules Excel)

| Champ | Formule | Applicable a |
|-------|---------|-------------|
| previsions_definitives | budget_primitif + budget_additionnel + modifications | Recettes, Depenses |
| reste_a_recouvrer | or_admis - recouvrement | Recettes |
| reste_a_payer | mandat_admis - paiement | Depenses |
| taux_execution (recettes) | or_admis / previsions_definitives | Recettes |
| taux_execution (depenses) | mandat_admis / previsions_definitives | Depenses |

Les totaux hierarchiques sont calcules par agregation (niv3 → niv2 → niv1), excluant `taux_execution` de l'agregation.
