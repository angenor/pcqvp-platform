# API Contract: Export Endpoints

**Date**: 2026-03-21 | **Feature**: 009-export-excel-word

## Endpoints existants (a modifier)

Les endpoints existent deja dans `public_comptes.py`. Cette feature les ameliore sans changer l'interface.

### GET /api/public/collectivites/{ctype}/{cid}/comptes/{annee}/export

**Description**: Telecharge un compte administratif publie au format Excel ou Word.

**Parametres de chemin**:
| Param | Type | Description |
|-------|------|-------------|
| ctype | string | Type de collectivite : `province`, `region`, `commune` |
| cid | UUID | Identifiant de la collectivite |
| annee | int | Annee d'exercice |

**Parametres de requete**:
| Param | Type | Requis | Description |
|-------|------|--------|-------------|
| format | string | oui | Format d'export : `xlsx` ou `docx` |

**Reponse succes (200)**:
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (xlsx) ou `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (docx)
- Content-Disposition: `attachment; filename="Compte_Administratif_{NomCollectivite}_{Annee}.{ext}"`
- Body: Fichier binaire (StreamingResponse)

**Reponses erreur**:
| Code | Condition |
|------|-----------|
| 400 | Format invalide (ni xlsx ni docx) |
| 404 | Collectivite ou annee inexistante, ou compte non publie |

**Notes**:
- Aucune authentification requise (endpoint public)
- Le nom du fichier dans Content-Disposition est nettoye (caracteres speciaux remplaces)
- Les colonnes calculees sont des valeurs statiques (pas de formules Excel)

## Structure du fichier Excel genere

```
Classeur.xlsx
├── Recettes                    (10 colonnes)
├── Recap Recettes              (6 colonnes)
├── Depenses Programme I        (11 colonnes, si existe)
├── Depenses Programme II       (11 colonnes, si existe)
├── Depenses Programme III      (11 colonnes, si existe)
├── Recap Depenses par Prog     (3 groupes x N programmes + Total)
├── Recap Depenses              (5 colonnes)
└── Equilibre                   (colonnes Depenses + Recettes en vis-a-vis)
```

### Colonnes par feuille

**Recettes** (10 colonnes):
Compte | Intitules | Budget Primitif | Budget Additionnel | Modifications +/- | Previsions Definitives | OR Admis | Recouvrement | Reste a Recouvrer | Taux d'Execution

**Depenses Programme N** (11 colonnes):
Compte | Intitules | Budget Primitif | Budget Additionnel | Modifications +/- | Previsions Definitives | Engagement | Mandat Admis | Paiement | Reste a Payer | Taux d'Execution

**Recap Recettes** (6 colonnes):
Compte | Intitules | Previsions Definitives | OR Admis | Recouvrement | Reste a Recouvrer

**Recap Depenses par Programme** (colonnes dynamiques):
Compte | Intitules | Mandatement Prog I | Mandatement Prog II | ... | Total Mandatement | Paiement Prog I | ... | Total Paiement | Reste Prog I | ... | Total Reste

**Recap Depenses** (5 colonnes):
Compte | Intitules | Mandat Admis | Paiement | Reste a Payer

**Equilibre** (10 colonnes en vis-a-vis):
Compte (D) | Intitules (D) | Mandat Admis | Paiement | Reste a Payer | Compte (R) | Intitules (R) | OR Admis | Recouvrement | Reste a Recouvrer

## Structure du document Word genere

```
Document.docx
├── Titre : "Compte administratif - {Collectivite} - Exercice {Annee}"
├── Section Recettes (tableau)
├── Section Depenses Programme I (tableau, si existe)
├── Section Depenses Programme II (tableau, si existe)
├── Section Depenses Programme III (tableau, si existe)
├── Section Recapitulatif Recettes (tableau)
├── Section Recapitulatif Depenses (tableau)
└── Section Equilibre budgetaire (tableau)
```
