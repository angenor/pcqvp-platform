# Implementation Plan: Export des comptes administratifs en Excel et Word

**Branch**: `009-export-excel-word` | **Date**: 2026-03-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-export-excel-word/spec.md`

## Summary

Ameliorer le service d'export existant (`export_service.py`) pour que les fichiers Excel et Word reproduisent fidelement la structure et la mise en forme du template officiel de compte administratif malgache. Les endpoints et boutons frontend existent deja ; cette feature comble les ecarts de colonnes, de feuilles et de style entre l'export actuel et le template de reference.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript strict (frontend)
**Primary Dependencies**: FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, openpyxl>=3.1.0, python-docx>=1.1.0 (backend) ; Nuxt 4.4+, Tailwind CSS 4, @nuxtjs/color-mode (frontend)
**Storage**: PostgreSQL 16+ via asyncpg ; aucune nouvelle table (lecture seule des tables existantes Features 006/007)
**Testing**: pytest (backend)
**Target Platform**: Web (serveur Linux, navigateur desktop/mobile)
**Project Type**: Web application (monorepo backend + frontend)
**Performance Goals**: Generation d'un fichier Excel/Word en moins de 5 secondes pour un compte avec ~300 lignes
**Constraints**: Fichiers generes < 5 Mo, pas de generation asynchrone necessaire
**Scale/Scope**: ~50 collectivites, ~3 annees par collectivite, ~300 lignes par feuille

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principe | Statut | Justification |
|----------|--------|---------------|
| I. Donnees Ouvertes & Transparence | PASSE | Export en formats ouverts (Excel, Word) ; donnees publiques sans restriction ; structure standardisee malgache respectee |
| II. Securite & Confidentialite | PASSE | Endpoints publics (pas d'auth) ; seuls les comptes publies sont exportables ; aucune donnee sensible dans les fichiers |
| III. Simplicite & Maintenabilite | PASSE | Modification de fichiers existants ; pas de nouvelle abstraction ; responsabilite unique du service d'export |
| Contrainte : export DOIT respecter mise en forme institutionnelle | PASSE | Alignement direct avec FR-009 et la constitution |
| Contrainte : useApi point d'entree unique | PASSE | Le composable usePublicComptes utilise deja useApi ; telechargement blob via $fetch natif (acceptable pour les binaires) |

**Re-check post-design** : Aucune violation. Le plan ne modifie que 4 fichiers existants, n'ajoute aucune table ni dependance.

## Project Structure

### Documentation (this feature)

```text
specs/009-export-excel-word/
├── plan.md              # Ce fichier
├── spec.md              # Specification
├── research.md          # Recherche et ecarts identifies
├── data-model.md        # Modele de donnees (lecture seule)
├── quickstart.md        # Guide de demarrage
├── contracts/
│   └── export-endpoints.md  # Contrat d'API
├── checklists/
│   └── requirements.md      # Checklist qualite
└── tasks.md             # Taches (genere par /speckit.tasks)
```

### Source Code (repository root)

```text
apps/backend/
├── app/
│   ├── services/
│   │   └── export_service.py     # MODIFIER : colonnes, feuilles, mise en forme, Word
│   └── routers/
│       └── public_comptes.py     # MODIFIER : Content-Disposition nom de fichier
└── tests/
    └── test_export.py            # CREER : tests unitaires export

apps/frontend/
└── app/
    ├── pages/
    │   └── collectivite/
    │       └── [type]-[id].vue   # MODIFIER : etats loading/disabled/erreur boutons
    └── composables/
        └── usePublicComptes.ts   # MODIFIER : utiliser nom fichier du header
```

**Structure Decision**: Monorepo existant. Aucun nouveau fichier de production a creer (sauf test). Modification de 4 fichiers existants.

## Ecarts a combler

### Backend : export_service.py

**Excel - Colonnes manquantes :**
1. Feuille Recettes : ajouter `Modifications +/-` et `Taux d'Execution` (passer de 8 a 10 colonnes)
2. Feuilles Depenses : ajouter `Modifications +/-`, `Engagement`, `Taux d'Execution` (passer de 8 a 11 colonnes)
3. Source des donnees : `values.modifications`, `values.engagement`, `computed.taux_execution` existent deja dans les retours des services

**Excel - Feuille manquante :**
4. Ajouter la feuille "Recap Depenses par Programme" avec le croisement complet (3 groupes de colonnes : Mandatement/Paiement/Reste par programme + Total). Les donnees sont deja disponibles dans `calculate_depenses_recap()` qui retourne `paiement` et `reste_a_payer` par programme.

**Excel - Mise en forme :**
5. Bordures thin sur toutes les cellules de donnees
6. Largeurs de colonnes fixes pour les colonnes numeriques (12-15 caracteres)
7. Lignes d'en-tete de section "RECETTES DE FONCTIONNEMENT" / "RECETTES D'INVESTISSEMENT" etc.
8. Titre avec nom de la collectivite sur chaque feuille

**Word - Completude :**
9. Inclure les lignes de niveau 3 (actuellement filtre a niv <= 2)
10. Ajouter les sections Recapitulatif Recettes et Recapitulatif Depenses

### Backend : public_comptes.py

11. Mettre a jour le Content-Disposition pour utiliser le format `Compte_Administratif_{NomCollectivite}_{Annee}.{ext}` avec nettoyage des caracteres speciaux

### Frontend : [type]-[id].vue

12. Ajouter les etats `downloadingExcel` / `downloadingWord` (ref boolean)
13. Desactiver le bouton et afficher un spinner pendant le telechargement
14. Afficher un message d'erreur en cas d'echec

### Frontend : usePublicComptes.ts

15. Extraire le nom de fichier du header Content-Disposition de la reponse pour le telechargement
