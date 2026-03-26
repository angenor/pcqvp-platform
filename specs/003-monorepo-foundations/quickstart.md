# Quickstart: Fondations du monorepo

**Branch**: `003-monorepo-foundations` | **Date**: 2026-03-20

## Prerequisites

- Python 3.12+
- Node.js 20+ et pnpm
- Docker et Docker Compose

## Demarrage

### 1. Variables d'environnement

```bash
cp .env.example .env
# Modifier .env si necessaire (mot de passe PostgreSQL, ports)
```

### 2. Base de donnees

```bash
docker compose up -d
# Attendre que PostgreSQL soit pret (healthcheck integre)
```

### 3. Backend

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend

```bash
cd apps/frontend
pnpm install
pnpm dev
```

### 5. Verification

- Frontend : http://localhost:3000 → affiche "Plateforme PCQVP" et le statut du backend
- Backend health : http://localhost:8000/health → `{"status": "ok", "db": "connected"}`

## Commandes utiles

| Commande | Description |
|----------|-------------|
| `docker compose up -d` | Demarrer PostgreSQL |
| `docker compose down` | Arreter PostgreSQL (donnees preservees) |
| `docker compose down -v` | Arreter PostgreSQL et supprimer les donnees |
| `alembic revision --autogenerate -m "description"` | Creer une migration |
| `alembic upgrade head` | Appliquer les migrations |
| `alembic downgrade -1` | Annuler la derniere migration |

## Structure des fichiers

```
pcqvp-platform/
├── apps/
│   ├── backend/
│   │   ├── .venv/                  # Environnement virtuel Python
│   │   ├── app/
│   │   │   ├── main.py             # Point d'entree FastAPI
│   │   │   └── core/
│   │   │       ├── config.py       # Pydantic Settings
│   │   │       └── database.py     # SQLAlchemy async engine + session
│   │   ├── alembic/
│   │   │   ├── env.py              # Config async
│   │   │   └── versions/           # Fichiers de migration
│   │   ├── alembic.ini
│   │   └── pyproject.toml
│   └── frontend/
│       ├── app/
│       │   ├── pages/
│       │   │   └── index.vue       # Page d'accueil
│       │   ├── composables/
│       │   │   └── useApi.ts       # Composable API (createUseFetch)
│       │   └── assets/
│       │       └── css/
│       │           └── main.css    # @import "tailwindcss"
│       ├── nuxt.config.ts          # Config Nuxt + proxy + Tailwind
│       └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```
