# Quickstart: Export Excel & Word

**Date**: 2026-03-21 | **Feature**: 009-export-excel-word

## Prerequis

- PostgreSQL 16 en cours d'execution (`docker compose up -d`)
- Backend avec migrations appliquees et au moins un compte publie
- Frontend Nuxt en cours d'execution

## Demarrage rapide

### Backend

```bash
cd apps/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd apps/frontend
pnpm dev
```

### Test rapide de l'export

```bash
# Export Excel (remplacer {ctype}, {cid}, {annee} par des valeurs reelles)
curl -o test_export.xlsx "http://localhost:8000/api/public/collectivites/commune/{cid}/comptes/{annee}/export?format=xlsx"

# Export Word
curl -o test_export.docx "http://localhost:8000/api/public/collectivites/commune/{cid}/comptes/{annee}/export?format=docx"
```

### Via l'interface

1. Ouvrir http://localhost:3000
2. Selectionner une collectivite avec un compte publie
3. Cliquer sur "Telecharger Excel" ou "Telecharger Word"

## Fichiers a modifier

### Backend (apps/backend/)

| Fichier | Modification |
|---------|-------------|
| `app/services/export_service.py` | Ajouter colonnes manquantes, feuille Recap Dep par Prog, bordures, mise en forme template |
| `app/routers/public_comptes.py` | Mettre a jour le Content-Disposition avec le nom de fichier normalise |

### Frontend (apps/frontend/)

| Fichier | Modification |
|---------|-------------|
| `app/pages/collectivite/[type]-[id].vue` | Ameliorer boutons (etats loading/disabled/erreur) |
| `app/composables/usePublicComptes.ts` | Utiliser le nom de fichier du header Content-Disposition |

### Aucun fichier a creer

Tous les fichiers existent deja. Cette feature est une amelioration de l'existant.

## Verification

- Comparer le fichier Excel genere avec `specs/002-suivi-revenus-miniers/data/Template_Tableaux_de_Compte_Administratif.xlsx` (structure des feuilles et colonnes)
- Comparer la mise en forme avec `specs/002-suivi-revenus-miniers/data/COMPTE_ADMINISTRATIF_COMMUNE_ANDRAFIABE_2023.xlsx` (style visuel)
