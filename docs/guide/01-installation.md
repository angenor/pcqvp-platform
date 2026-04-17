# Chapitre 1 — Installation et demarrage

Ce chapitre decrit les etapes necessaires pour installer et demarrer la plateforme PCQVP en environnement de developpement local.

---

## Prerequis

Avant de commencer, verifiez que les logiciels suivants sont installes sur votre machine :

| Composant | Version minimale | Role |
|---|---|---|
| Docker et Docker Compose | Docker 24+ | Hebergement de PostgreSQL |
| Python | 3.12+ | Backend FastAPI |
| Node.js | 18+ | Runtime frontend |
| pnpm | 8+ | Gestionnaire de paquets frontend |
| PostgreSQL | 16 (via Docker) | Base de donnees principale |

---

## Demarrage de la base de donnees

La base de donnees PostgreSQL est fournie sous forme de conteneur Docker. Elle doit etre demarree avant le backend.

```bash
docker compose up -d        # Demarrer PostgreSQL en arriere-plan
docker compose down         # Arreter le conteneur (les donnees sont preservees)
docker compose down -v      # Arreter le conteneur et supprimer les donnees
```

Points importants :

- Les donnees sont persistees dans un volume Docker nomme `pcqvp_pgdata`. La commande `docker compose down` seule ne supprime pas ce volume.
- Pour repartir d'une base vide, utilisez `docker compose down -v` puis relancez `docker compose up -d`.
- Un health check automatique est execute toutes les 10 secondes sur le conteneur. Le backend ne doit etre demarre qu'une fois ce check reussi.

---

## Installation du backend

Le backend est une application Python (FastAPI). Depuis la racine du depot :

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

La commande `pip install -e ".[dev]"` installe le projet en mode editable ainsi que toutes les dependances de developpement (tests, linters, etc.).

---

## Configuration de l'environnement

La configuration est chargee depuis un fichier `.env` situe dans le **dossier parent** du depot (un niveau au-dessus de `pcqvp-platform-new-version/`). Ce positionnement est intentionnel : il permet de ne pas versionner les secrets.

Exemple de chemin attendu :

```
~/projets/pcqvp/              <-- dossier parent
    .env                      <-- fichier de configuration
    pcqvp-platform-new-version/
        backend/
        frontend/
        ...
```

### Variables essentielles

```dotenv
# Base de donnees
DATABASE_URL=postgresql+asyncpg://pcqvp:password@localhost:5432/pcqvp
POSTGRES_USER=pcqvp
POSTGRES_PASSWORD=password
POSTGRES_DB=pcqvp

# Securite JWT
JWT_SECRET_KEY=une-cle-secrete-longue-et-aleatoire

# Compte administrateur initial
FIRST_ADMIN_EMAIL=admin@example.com
FIRST_ADMIN_PASSWORD=motdepasse-securise

# Fichiers uploades
UPLOAD_DIR=/chemin/absolu/vers/les/uploads
```

> **Attention :** Ne committez jamais le fichier `.env` dans le depot. Il est exclu par le `.gitignore`.

---

## Migrations et seed

Une fois la base de donnees demarree et le fichier `.env` en place, appliquez les migrations et initialisez les donnees de reference :

```bash
cd backend
alembic upgrade head        # Appliquer toutes les migrations
python -m app.seed          # Creer l'admin initial et les donnees exemple
```

Le script de seed cree les elements suivants :

- **Un utilisateur administrateur** : adresse email et mot de passe issus des variables `FIRST_ADMIN_EMAIL` et `FIRST_ADMIN_PASSWORD` du fichier `.env`.
- **Les templates de lignes budgetaires** : 168 lignes de recettes et 273 lignes de depenses par programme, conformes au cadre comptable malgache.
- **Un exemple de hierarchie geographique** : Province Antsiranana > Region Diana > Commune Andrafiabe.
- **Un compte administratif exemple** : Andrafiabe, exercice 2023, avec les templates appliques.

Ces donnees permettent de tester l'interface immediatement apres l'installation.

---

## Installation du frontend

Le frontend est une application Nuxt 4. Depuis la racine du depot :

```bash
cd frontend
pnpm install
pnpm dev                    # Lancer le serveur de developpement (port 3000)
```

La commande `pnpm dev` demarre un serveur avec rechargement a chaud. Toute modification des fichiers Vue, TypeScript ou CSS est prise en compte sans redemarrage manuel.

---

## Verification de l'installation

Une fois le backend et le frontend demarres, verifiez que chaque service repond correctement :

| Service | URL | Reponse attendue |
|---|---|---|
| Frontend | http://localhost:3000 | Page d'accueil de la plateforme |
| Backend (health check) | http://localhost:8000/health | `{"status": "ok", "db": "connected"}` |
| Interface d'administration | http://localhost:3000/admin/login | Formulaire de connexion administrateur |

Si le health check du backend retourne une erreur de connexion a la base de donnees, verifiez que le conteneur Docker est bien demarre et que les variables `DATABASE_URL` et `POSTGRES_*` sont correctement renseignees dans le fichier `.env`.

---

## Proxy frontend

En mode developpement, le frontend Nuxt fait office de proxy transparent pour les appels vers le backend. Deux prefixes sont concernes :

| Prefixe | Cible |
|---|---|
| `/api/**` | `http://localhost:8000` |
| `/uploads/**` | `http://localhost:8000` |

Ce comportement est configure dans `frontend/nuxt.config.ts` via la propriete `routeRules`. Il n'y a aucune configuration CORS a effectuer en developpement : toutes les requetes passent par le port 3000 du frontend.

En production, ce proxy est remplace par une configuration Nginx ou equivalente. Ce point est traite dans le chapitre consacre au deploiement.
