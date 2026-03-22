# Quickstart: EditorJS Rich Content

## Prérequis

- Docker (PostgreSQL)
- Python 3.12+ avec venv
- Node.js 18+ avec pnpm

## Setup rapide

### 1. Base de données
```bash
docker compose up -d
```

### 2. Backend
```bash
cd apps/backend
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
# Créer le répertoire uploads si nécessaire
mkdir -p uploads/images
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend
```bash
cd apps/frontend
pnpm install
pnpm dev
```

### 4. Migration des données existantes (si nécessaire)
```bash
cd apps/backend
python scripts/migrate_description_format.py
```

## Vérification

1. Accéder à http://localhost:3000/admin/geography/provinces
2. Créer ou éditer une province
3. L'éditeur EditorJS doit apparaître dans la section description
4. Ajouter un titre, paragraphe, image (upload), tableau et liste
5. Sauvegarder et vérifier que le contenu persiste
6. Consulter la page publique pour vérifier le rendu

## Nouveaux packages frontend

```bash
cd apps/frontend
pnpm add @editorjs/editorjs @editorjs/header @editorjs/image @editorjs/table @editorjs/list
```

## Structure des fichiers modifiés/créés

### Backend
- `app/schemas/geography.py` - Nouveaux schémas EditorJS
- `app/routers/upload.py` - Endpoint upload d'images (nouveau)
- `app/main.py` - Montage StaticFiles + routeur upload
- `app/core/config.py` - Settings upload (UPLOAD_DIR, MAX_IMAGE_SIZE)
- `scripts/migrate_description_format.py` - Script migration (nouveau)

### Frontend
- `app/components/RichContentEditor.vue` - Réécriture avec EditorJS
- `app/components/RichContentRenderer.vue` - Support nouveaux blocs
- `packages/shared/types/geography.ts` - Types EditorJS

### Tests
- `tests/test_upload.py` - Tests endpoint upload (nouveau)
- `tests/test_geography.py` - Mise à jour pour format EditorJS
