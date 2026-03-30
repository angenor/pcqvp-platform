# Deploiement - Collectivites Territoriales

## Serveur Contabo (Partage avec site_principale)

| Caracteristique | Valeur |
|-----------------|--------|
| IP | `164.68.112.108` |
| OS | Ubuntu Linux |
| Plan | Cloud VPS 10 SSD |
| Stockage | 150 GB |
| RAM | 8 GB |
| Docker | Pre-installe |

---

## Repositories GitHub

| Composant | Repository |
|-----------|------------|
| Frontend | `https://github.com/angenor/frontend_collectivites_territoriales.git` |
| Backend | `https://github.com/angenor/backend_collectivites_territoriales.git` |

---

## Architecture des Ports

| Projet | Frontend | Backend | Base de donnees |
|--------|----------|---------|-----------------|
| site_principale (MOM) | Port 80 | Interne | Port 5432 |
| **collectivites_territoriales** | **Port 8080** | **Port 8081** | **Port 5433** |

**URLs d'acces (avant configuration domaine):**
- Frontend: `http://164.68.112.108:8080`
- Backend API: `http://164.68.112.108:8081`
- Swagger Docs: `http://164.68.112.108:8081/docs`

**URLs finales (apres configuration domaine et SSL):**
- Frontend: `https://kaominina-mangarahara.mg`
- Backend API: `https://kaominina-mangarahara.mg/api`
- Swagger Docs: `https://kaominina-mangarahara.mg/docs`

---

## Procedure de Deploiement

### Etape 1: Connexion SSH au serveur

```bash
ssh root@164.68.112.108
```

### Etape 2: Creer la structure et cloner les repos

```bash
# Creer le dossier principal
mkdir -p /opt/collectivites_territoriales
cd /opt/collectivites_territoriales

# Cloner les deux repos
git clone https://github.com/angenor/frontend_collectivites_territoriales.git
git clone https://github.com/angenor/backend_collectivites_territoriales.git
```

### Etape 3: Creer le fichier docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
# ===========================================
# Docker Compose - Collectivites Territoriales
# Production - Serveur Contabo
# ===========================================

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: ct_db
    restart: unless-stopped
    ports:
      - "5433:5432"
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-ct_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB:-collectivites_db}
    volumes:
      - ct_postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-ct_user} -d ${POSTGRES_DB:-collectivites_db}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - ct_network

  # FastAPI Backend
  backend:
    build:
      context: ./backend_collectivites_territoriales
      dockerfile: Dockerfile
    container_name: ct_backend
    restart: unless-stopped
    ports:
      - "8081:8000"
    environment:
      - APP_NAME=Plateforme Collectivites Territoriales
      - APP_VERSION=1.0.0
      - DEBUG=${DEBUG:-False}
      - ENVIRONMENT=${ENVIRONMENT:-production}
      - POSTGRES_USER=${POSTGRES_USER:-ct_user}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_SERVER=db
      - POSTGRES_PORT=5432
      - POSTGRES_DB=${POSTGRES_DB:-collectivites_db}
      - SECRET_KEY=${SECRET_KEY}
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES:-30}
      - REFRESH_TOKEN_EXPIRE_MINUTES=${REFRESH_TOKEN_EXPIRE_MINUTES:-10080}
      - BACKEND_CORS_ORIGINS=["http://kaominina-mangarahara.mg","https://kaominina-mangarahara.mg","http://www.kaominina-mangarahara.mg","https://www.kaominina-mangarahara.mg","http://164.68.112.108:8080"]
      - FRONTEND_URL=${FRONTEND_URL:-https://kaominina-mangarahara.mg}
      - BACKEND_URL=${BACKEND_URL:-https://kaominina-mangarahara.mg/api}
      - MAX_UPLOAD_SIZE_MB=${MAX_UPLOAD_SIZE_MB:-20}
      - UPLOAD_DIR=/app/uploads
      - FIRST_SUPERUSER_EMAIL=${FIRST_SUPERUSER_EMAIL:-admin@ti-madagascar.org}
      - FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD:-changeme123}
    volumes:
      - ct_uploads:/app/uploads
      - ct_logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - ct_network

  # Nuxt Frontend
  frontend:
    build:
      context: ./frontend_collectivites_territoriales
      dockerfile: Dockerfile
      args:
        - NUXT_PUBLIC_API_BASE_URL=${NUXT_PUBLIC_API_BASE_URL:-https://kaominina-mangarahara.mg/api}
    container_name: ct_frontend
    restart: unless-stopped
    ports:
      - "8080:3000"
    environment:
      - NODE_ENV=production
      - NUXT_PUBLIC_API_BASE_URL=${NUXT_PUBLIC_API_BASE_URL:-https://kaominina-mangarahara.mg/api}
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - ct_network

  # Migrations (run once)
  migrations:
    build:
      context: ./backend_collectivites_territoriales
      dockerfile: Dockerfile
    container_name: ct_migrations
    command: alembic upgrade head
    environment:
      - POSTGRES_USER=${POSTGRES_USER:-ct_user}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_SERVER=db
      - POSTGRES_PORT=5432
      - POSTGRES_DB=${POSTGRES_DB:-collectivites_db}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
    networks:
      - ct_network
    profiles:
      - migrate

volumes:
  ct_postgres_data:
  ct_uploads:
  ct_logs:

networks:
  ct_network:
    driver: bridge
EOF
```

### Etape 4: Creer le fichier .env

```bash
cat > .env << 'EOF'
# ===========================================
# Production Environment - Collectivites Territoriales
# ===========================================

# PostgreSQL
POSTGRES_USER=ct_user
POSTGRES_PASSWORD=VotreMotDePasseSecurise123!
POSTGRES_DB=collectivites_db

# Application
DEBUG=False
ENVIRONMENT=production

# Secret key - Generer avec: openssl rand -hex 32
SECRET_KEY=REMPLACEZ_PAR_VOTRE_CLE_SECRETE

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080

# Upload
MAX_UPLOAD_SIZE_MB=20

# Admin initial
FIRST_SUPERUSER_EMAIL=admin@ti-madagascar.org
FIRST_SUPERUSER_PASSWORD=VotreMotDePasseAdmin123!
EOF

# Generer une cle secrete automatiquement
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/REMPLACEZ_PAR_VOTRE_CLE_SECRETE/$SECRET_KEY/" .env

# Editer pour personnaliser les mots de passe
nano .env
```

### Etape 5: Demarrer les services

```bash
# Build et demarrage
docker compose up -d --build

# Executer les migrations (premiere fois)
docker compose --profile migrate up migrations

# Verifier les logs
docker compose logs -f
```

### Etape 6: Verifier le deploiement

```bash
# Verifier les conteneurs
docker compose ps

# Tester le backend
curl http://164.68.112.108:8081/health

# Tester le frontend
curl -I http://164.68.112.108:8080
```

---

## Structure sur le Serveur

```
/opt/collectivites_territoriales/
├── backend_collectivites_territoriales/   # Clone du repo backend
├── frontend_collectivites_territoriales/  # Clone du repo frontend
├── docker-compose.yml                      # Fichier compose (cree manuellement)
└── .env                                    # Variables d'environnement
```

---

## Commandes Utiles

```bash
cd /opt/collectivites_territoriales

# Voir les logs
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend

# Redemarrer
docker compose restart
docker compose restart backend

# Arreter
docker compose down

# Mise a jour
git -C backend_collectivites_territoriales pull
git -C frontend_collectivites_territoriales pull
docker compose up -d --build
```

---

## Base de Donnees

### Acces PostgreSQL

```bash
docker exec -it ct_db psql -U ct_user -d collectivites_db
```

### Sauvegarde

```bash
docker exec ct_db pg_dump -U ct_user collectivites_db > backup_ct_$(date +%Y%m%d).sql
```

### Restauration

```bash
docker exec -i ct_db psql -U ct_user collectivites_db < backup_ct_YYYYMMDD.sql
```

---

## Configuration Firewall

```bash
ufw allow 8080/tcp comment 'CT Frontend'
ufw allow 8081/tcp comment 'CT Backend API'
ufw status
```

---

## Depannage

### Le backend ne demarre pas
```bash
docker compose logs backend
docker exec ct_backend python -c "from app.database import engine; print('DB OK')"
```

### Le frontend ne se connecte pas au backend
1. Verifier: `curl http://164.68.112.108:8081/health`
2. Verifier les CORS dans les logs backend
3. Reconstruire le frontend: `docker compose up -d --build frontend`

### Problemes de migrations
```bash
docker exec ct_backend alembic current
docker exec ct_backend alembic upgrade head
```

---

## Resume des Conteneurs

| Conteneur | Image | Port Interne | Port Expose |
|-----------|-------|--------------|-------------|
| ct_db | postgres:15-alpine | 5432 | 5433 |
| ct_backend | python:3.11-slim | 8000 | 8081 |
| ct_frontend | node:20-alpine | 3000 | 8080 |

---

## Configuration du Domaine kaominina-mangarahara.mg

### Informations DNS

| Element | Valeur |
|---------|--------|
| Domaine | kaominina-mangarahara.mg |
| IP VPS Contabo | 164.68.112.108 |
| Frontend | Port 8080 |
| Backend API | Port 8081 |

### Etape 1: Installer Nginx (si pas deja fait)

```bash
sudo apt update
sudo apt install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### Etape 2: Copier la configuration Nginx

```bash
# Copier le fichier de configuration depuis le repo
sudo cp /opt/collectivites_territoriales/nginx/kaominina-mangarahara.mg.conf \
       /etc/nginx/sites-available/kaominina-mangarahara.mg

# Activer le site
sudo ln -sf /etc/nginx/sites-available/kaominina-mangarahara.mg \
            /etc/nginx/sites-enabled/

# Tester la configuration
sudo nginx -t

# Recharger Nginx
sudo systemctl reload nginx
```

### Etape 3: Configurer SSL avec Let's Encrypt

```bash
# Installer Certbot
sudo apt install -y certbot python3-certbot-nginx

# Generer le certificat SSL
sudo certbot --nginx -d kaominina-mangarahara.mg -d www.kaominina-mangarahara.mg

# Verifier le renouvellement automatique
sudo certbot renew --dry-run
```

### Etape 4: Mettre a jour les variables d'environnement pour HTTPS

Editer `/opt/collectivites_territoriales/.env`:

```bash
# Mettre a jour les URLs pour HTTPS
FRONTEND_URL=https://kaominina-mangarahara.mg
BACKEND_URL=https://kaominina-mangarahara.mg/api
BACKEND_CORS_ORIGINS=["https://kaominina-mangarahara.mg","https://www.kaominina-mangarahara.mg"]
```

Puis redemarrer les containers:

```bash
cd /opt/collectivites_territoriales
docker compose down
docker compose up -d --build
```

### Etape 5: Configurer le Firewall

```bash
# Autoriser HTTP/HTTPS
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# Verifier
sudo ufw status
```

### Verifications

```bash
# Tester la resolution DNS
dig +short kaominina-mangarahara.mg
# Doit retourner: 164.68.112.108

# Tester l'acces HTTP
curl -I http://kaominina-mangarahara.mg

# Tester l'acces HTTPS (apres SSL)
curl -I https://kaominina-mangarahara.mg

# Tester l'API
curl https://kaominina-mangarahara.mg/api/v1/health
```

### URLs Finales

| Service | URL |
|---------|-----|
| Frontend | https://kaominina-mangarahara.mg |
| API | https://kaominina-mangarahara.mg/api |
| Swagger Docs | https://kaominina-mangarahara.mg/docs |
| ReDoc | https://kaominina-mangarahara.mg/redoc |

---

## Logs et Debugging

### Logs Nginx

```bash
# Logs d'acces
sudo tail -f /var/log/nginx/access.log

# Logs d'erreur
sudo tail -f /var/log/nginx/error.log
```

### Tester SSL

- SSL Labs: https://www.ssllabs.com/ssltest/analyze.html?d=kaominina-mangarahara.mg
- Propagation DNS: https://dnschecker.org/#A/kaominina-mangarahara.mg
