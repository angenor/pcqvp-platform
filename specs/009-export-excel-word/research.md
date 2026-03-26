# Research: Export Excel & Word

**Date**: 2026-03-21 | **Feature**: 009-export-excel-word

## Etat actuel

L'infrastructure d'export existe deja :
- Backend : `export_service.py` avec `generate_excel()` et `generate_word()`
- Router : `GET /{ctype}/{cid}/comptes/{annee}/export?format=xlsx|docx`
- Frontend : boutons de telechargement avec `downloadExport()` dans `usePublicComptes.ts`
- Calculs : tous les services existent (`get_recettes_with_computed`, `get_depenses_with_computed`, `calculate_recettes_recap`, `calculate_depenses_recap`, `calculate_equilibre`)

## Ecarts identifies (export actuel vs template de reference)

### Excel - Colonnes manquantes

| Feuille | Colonnes actuelles (8) | Colonnes requises (10-11) | Manquantes |
|---------|----------------------|-------------------------|------------|
| Recettes | Code, Intitule, Budget primitif, Budget additionnel, Prev. def., OR admis, Recouvrement, Reste a recouvrer | + Modifications +/-, Taux d'Execution | 2 |
| Depenses/Prog | Code, Intitule, Budget primitif, Budget additionnel, Prev. def., Mandat admis, Paiement, Reste a payer | + Modifications +/-, Engagement, Taux d'Execution | 3 |

- Decision: Ajouter les colonnes manquantes pour reproduire le template
- Rationale: Le template officiel malgache les inclut toutes
- Alternative: Garder la structure simplifiee → Rejetee (non conforme FR-004/FR-005)

### Excel - Feuille Recap Depenses par Programme

- Actuel : La feuille "Recap Depenses" ne montre que `mandat_admis` par programme
- Requis : Croisement complet avec 3 groupes (Mandatement, Paiement, Reste a Payer) x programmes + Total
- Decision: Ajouter une feuille "Recap Depenses par Programme" distincte avec le croisement complet, et garder la feuille "Recap Depenses" en synthese
- Rationale: Le template a les deux feuilles separees
- Alternative: Fusionner en une seule feuille → Rejetee (ne reproduit pas le template)

### Excel - Mise en forme

- Actuel : Basique (bold, header fill, section fill, auto-width)
- Requis : Bordures de cellules, largeurs ajustees, retrait par niveau, separation Fonctionnement/Investissement
- Decision: Ameliorer la mise en forme avec bordures thin, largeurs fixes pour les colonnes numeriques, retrait via espaces dans l'intitule
- Rationale: Fidelite au template de reference (FR-009)
- Alternative: Garder le style actuel → Rejetee (non conforme)

### Excel - Nommage de fichier

- Actuel : `compte_{type}_{annee}.{ext}` (cote frontend)
- Requis : `Compte_Administratif_[NomCollectivite]_[Annee].[extension]` (FR-015)
- Decision: Generer le nom cote backend dans le header Content-Disposition, le frontend l'utilise directement
- Rationale: Le backend connait le nom de la collectivite
- Alternative: Construire le nom cote frontend → Rejetee (necessite un appel supplementaire)

### Word - Profondeur des donnees

- Actuel : Filtre aux niveaux 1-2 (ignore niveau 3)
- Requis : FR-014 exige donnees identiques a l'Excel
- Decision: Inclure les 3 niveaux dans le Word
- Rationale: Parite des donnees entre formats
- Alternative: Garder niveaux 1-2 pour lisibilite → Rejetee (contradiction avec FR-014)

### Word - Sections manquantes

- Actuel : Recettes, Depenses par programme, Equilibre
- Requis : + Recapitulatif Recettes, Recapitulatif Depenses
- Decision: Ajouter les sections recap dans le document Word
- Rationale: FR-013 liste toutes les sections

### Frontend - Etat de chargement

- Actuel : Boutons existants, telechargement fonctionnel
- Requis : Indicateur de chargement, desactivation pendant generation, gestion d'erreur
- Decision: Ajouter des etats `downloadingExcel`/`downloadingWord` avec spinner et disabled
- Rationale: FR-018 l'exige

## Donnees disponibles dans les services existants

Les services `account_service.py` fournissent toutes les donnees brutes necessaires :

- `values.modifications` : Disponible dans le JSONB des RecetteLine/DepenseLine
- `values.engagement` : Disponible dans le JSONB des DepenseLine
- `computed.taux_execution` : Deja calcule par `compute_line_values()` (mandat_admis / prev_def ou or_admis / prev_def)
- `calculate_depenses_recap` : Retourne deja `paiement` et `reste_a_payer` par programme

Aucune modification des services de calcul n'est necessaire. Seul l'export_service doit exploiter les champs existants.

## Technologies

- openpyxl >= 3.1.0 : Deja installe, suffisant pour bordures, styles, fusions
- python-docx >= 1.1.0 : Deja installe, suffisant pour tableaux structures
- Aucune nouvelle dependance requise
