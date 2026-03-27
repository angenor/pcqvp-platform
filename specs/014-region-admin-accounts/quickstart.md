# Quickstart: Comptes administratifs par région

**Date**: 2026-03-27

## Prérequis

- Docker (PostgreSQL 16)
- Python 3.12+ avec venv
- Node.js + pnpm

## Démarrage

```bash
# 1. Base de données
docker compose up -d

# 2. Backend
cd backend
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Frontend (dans un autre terminal)
cd frontend
pnpm install
pnpm dev
```

## Vérification

1. **Backend** : http://localhost:8000/health
2. **Frontend** : http://localhost:3000
3. **Admin** : http://localhost:3000/admin (login requis)

## Fichiers à modifier

| Fichier | Modification |
|---------|-------------|
| `frontend/app/pages/admin/accounts/index.vue` | Lire query params pour pré-remplir les filtres |
| `frontend/app/pages/admin/geography/regions/[id]/index.vue` | Ajouter bouton "Voir les comptes" |
| `frontend/app/pages/regions/[id].vue` | Ajouter tableau des comptes publiés |

## Tests manuels

1. Aller sur `/admin/geography/regions/{id}` → vérifier le bouton "Voir les comptes"
2. Cliquer → vérifier que `/admin/accounts?collectivite_type=region&collectivite_id={id}` affiche les comptes filtrés
3. Créer un compte pour une région → vérifier qu'il apparaît dans la liste
4. Publier le compte → vérifier qu'il apparaît sur `/regions/{id}`
5. Tester avec une région sans commune → vérifier l'absence d'erreurs
