# Plateforme PCQVP

Plateforme de transparence des industries extractives - Publiez Ce Que Vous Payez (Madagascar).

## Prerequisites

- Python 3.12+
- Node.js 20+ et [pnpm](https://pnpm.io/)
- Docker et Docker Compose

## Demarrage rapide

### 1. Variables d'environnement

```bash
cp .env.example .env
# Modifier .env si necessaire (mot de passe PostgreSQL, ports)
```

### 2. Base de donnees

```bash
docker compose up -d
```

### 3. Backend

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
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

- **Frontend** : http://localhost:3000 - affiche "Plateforme PCQVP" et le statut du backend
- **Backend health** : http://localhost:8000/health - `{"status": "ok", "db": "connected"}`

## Structure du projet

```
pcqvp-platform/
├── apps/
│   ├── backend/          # FastAPI + SQLAlchemy async
│   └── frontend/         # Nuxt 4 + Tailwind CSS 4
├── docker-compose.yml    # PostgreSQL 16
├── .env.example          # Variables d'environnement
└── README.md
```

## Commandes utiles

| Commande | Description |
|----------|-------------|
| `docker compose up -d` | Demarrer PostgreSQL |
| `docker compose down` | Arreter PostgreSQL (donnees preservees) |
| `docker compose down -v` | Arreter et supprimer les donnees |
| `alembic revision --autogenerate -m "desc"` | Creer une migration |
| `alembic upgrade head` | Appliquer les migrations |
| `alembic downgrade -1` | Annuler la derniere migration |
# pcqvp-platform
