# Quickstart: Authentification et gestion des rôles

**Feature**: 004-auth-roles

## Prérequis

- Python 3.12+
- Node.js 20+
- PostgreSQL 16+ (ou Docker)
- pnpm

## Variables d'environnement

Ajouter dans `.env` à la racine :

```env
# Existants
DATABASE_URL=postgresql+asyncpg://pcqvp:changeme@localhost:5432/pcqvp

# Nouveaux (auth)
JWT_SECRET=your-secret-key-min-32-chars-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
FIRST_ADMIN_EMAIL=admin@pcqvp.mg
FIRST_ADMIN_PASSWORD=changeme123
```

## Installation des dépendances

### Backend

```bash
cd apps/backend
source .venv/bin/activate
pip install -e ".[dev]"
```

Les nouvelles dépendances ajoutées à `pyproject.toml` :
- `python-jose[cryptography]`
- `passlib[bcrypt]`
- `python-multipart` (pour les formulaires FastAPI)
- `httpx` (dev, pour les tests)
- `email-validator` (pour EmailStr Pydantic)

### Frontend

```bash
cd apps/frontend
pnpm install
```

Nouveau module ajouté : `@nuxtjs/color-mode`

## Migration base de données

```bash
cd apps/backend
alembic upgrade head
```

## Seed admin initial

```bash
cd apps/backend
python -m scripts.seed_admin
```

Utilise `FIRST_ADMIN_EMAIL` et `FIRST_ADMIN_PASSWORD` depuis `.env`. Idempotent (ne crée pas de doublon).

## Lancer le projet

```bash
# Terminal 1 : Backend
cd apps/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 : Frontend
cd apps/frontend
pnpm dev
```

## Vérification

1. Ouvrir http://localhost:3000/admin → redirigé vers /admin/login
2. Se connecter avec les identifiants du seed admin
3. Vérifier l'accès au dashboard admin
4. Tester le toggle dark/light mode
5. Tester la déconnexion

## Tests

```bash
# Backend
cd apps/backend
pytest tests/test_auth.py -v

# Frontend (quand implémenté)
cd apps/frontend
pnpm test
```
