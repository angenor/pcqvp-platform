# Data Model: Fondations du monorepo

**Branch**: `003-monorepo-foundations` | **Date**: 2026-03-20

## Entities

Cette feature est une fondation d'infrastructure. Aucun modele metier n'est defini (explicitement hors scope). Seul le modele de base SQLAlchemy est etabli.

### Base declarative

- **Base**: Classe declarative SQLAlchemy (`DeclarativeBase`) servant de parent pour tous les futurs modeles.
- Aucune table metier n'est creee dans cette feature.
- Le `target_metadata` d'Alembic pointe vers `Base.metadata` pour la detection automatique des futures migrations.

## Reponse du Health Check

Structure de la reponse du endpoint `GET /health` (pas une entite persistee) :

| Champ    | Type   | Valeurs possibles          | Description                          |
|----------|--------|----------------------------|--------------------------------------|
| `status` | string | `"ok"`                     | Statut du service backend            |
| `db`     | string | `"connected"`, `"disconnected"` | Statut de la connexion PostgreSQL |
| `detail` | string | message d'erreur (optionnel) | Present uniquement si `db = "disconnected"` |

## Configuration

Variables d'environnement (non persistees, documentees dans `.env.example`) :

| Variable          | Type   | Defaut                                              | Description                    |
|-------------------|--------|------------------------------------------------------|--------------------------------|
| `DATABASE_URL`    | string | `postgresql+asyncpg://pcqvp:changeme@localhost:5432/pcqvp` | URL de connexion async         |
| `BACKEND_HOST`    | string | `0.0.0.0`                                           | Host du serveur backend        |
| `BACKEND_PORT`    | int    | `8000`                                               | Port du serveur backend        |
| `CORS_ORIGINS`    | string | `http://localhost:3000`                              | Origines autorisees (comma-separated) |
| `POSTGRES_USER`   | string | `pcqvp`                                              | Utilisateur PostgreSQL         |
| `POSTGRES_PASSWORD`| string | `changeme`                                          | Mot de passe PostgreSQL        |
| `POSTGRES_DB`     | string | `pcqvp`                                              | Nom de la base de donnees      |
