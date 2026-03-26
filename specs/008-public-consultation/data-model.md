# Data Model: 008-public-consultation

## Overview

Cette feature ne cree PAS de nouvelles tables en base de donnees. Elle expose en lecture seule les donnees existantes des Features 006 (templates) et 007 (comptes administratifs). Le modele de donnees ci-dessous documente les entites lues et les projections calculees.

## Entites lues (existantes)

### CompteAdministratif (table: comptes_administratifs)
- `id` UUID PK
- `collectivite_type` enum(province, region, commune)
- `collectivite_id` UUID → FK vers Province/Region/Commune
- `annee_exercice` int
- `status` enum(draft, published) — **filtre: seuls "published" sont exposes**
- `created_at` datetime
- `updated_at` datetime | null
- Unique: (collectivite_type, collectivite_id, annee_exercice)

### RecetteLine (table: recette_lines)
- `id` UUID PK
- `compte_admin_id` UUID → FK CompteAdministratif
- `template_line_id` UUID → FK AccountTemplateLine
- `values` JSONB {budget_primitif, budget_additionnel, modifications, or_admis, recouvrement}
- Unique: (compte_admin_id, template_line_id)

### DepenseProgram (table: depense_programs)
- `id` UUID PK
- `compte_admin_id` UUID → FK CompteAdministratif
- `numero` int
- `intitule` str
- Unique: (compte_admin_id, numero)

### DepenseLine (table: depense_lines)
- `id` UUID PK
- `programme_id` UUID → FK DepenseProgram
- `template_line_id` UUID → FK AccountTemplateLine
- `values` JSONB {budget_primitif, budget_additionnel, modifications, engagement, mandat_admis, paiement}
- Unique: (programme_id, template_line_id)

### AccountTemplate (table: account_templates)
- `id` UUID PK
- `name` str
- `template_type` enum(recette, depense)
- `version` int
- `is_active` bool

### AccountTemplateLine (table: account_template_lines)
- `id` UUID PK
- `template_id` UUID → FK AccountTemplate
- `compte_code` str
- `intitule` str
- `level` int (1, 2, 3)
- `parent_code` str | null
- `section` str (fonctionnement, investissement)
- `sort_order` int

### AccountTemplateColumn (table: account_template_columns)
- `id` UUID PK
- `template_id` UUID → FK AccountTemplate
- `name` str
- `code` str
- `data_type` enum(number, text, percentage)
- `is_computed` bool
- `formula` str | null
- `sort_order` int

### Province / Region / Commune (tables geographiques)
- `id` UUID PK
- `name` str
- `code` str (unique)
- `description_json` JSONB (blocs de contenu riche)

## Projections calculees (non stockees)

### Colonnes derivees (par ligne)
- **Recettes**: previsions_definitives = budget_primitif + budget_additionnel + modifications ; reste_a_recouvrer = or_admis - recouvrement ; taux_execution = or_admis / previsions_definitives
- **Depenses**: previsions_definitives = budget_primitif + budget_additionnel + modifications ; reste_a_payer = mandat_admis - paiement ; taux_execution = mandat_admis / previsions_definitives

### Sommes hierarchiques
- Niv2 = somme de ses enfants Niv3
- Niv1 = somme de ses enfants Niv2

### Recapitulatif recettes
- Par section (fonctionnement, investissement) → par categorie Niv1 → sous-totaux reelles/ordre/section

### Recapitulatif depenses
- Croisement categories Niv1 × programmes → mandat_admis, paiement, reste_a_payer

### Equilibre
- Par section → recettes vs depenses → operations reelles vs ordre → excedent/deficit

## Relations

```
Province 1──N Region 1──N Commune
    |              |            |
    └──────────────┴────────────┘
                   |
    CompteAdministratif (collectivite_type + collectivite_id)
         |                    |
         N RecetteLine        N DepenseProgram
              |                    |
              |                    N DepenseLine
              |                         |
              └─────────┬───────────────┘
                        |
                AccountTemplateLine ──N── AccountTemplate
```
