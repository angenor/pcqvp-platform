#!/bin/bash

# ===========================================
# PCQVP Platform - Deployment Script (Git-based)
# Remplacement de collectivites_territoriales
# ===========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REMOTE_USER="root"
REMOTE_HOST="164.68.112.108"
REMOTE_DIR="/opt/pcqvp"
OLD_DIR="/opt/collectivites_territoriales"

# GitHub repository (monorepo)
REPO_URL="https://github.com/angenor/pcqvp-platform.git"

echo -e "${GREEN}=== PCQVP Platform Deployment ===${NC}"

# -----------------------------------------------
# SETUP: First-time server setup
# -----------------------------------------------
setup() {
    echo -e "${GREEN}[1/6] Verification de Docker sur le serveur...${NC}"
    ssh ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
        # Install Docker if not present
        if ! command -v docker &> /dev/null; then
            echo "Installation de Docker..."
            curl -fsSL https://get.docker.com | sh
            systemctl enable docker
            systemctl start docker
        fi

        # Install Docker Compose plugin if not present
        if ! docker compose version &> /dev/null; then
            echo "Installation de Docker Compose..."
            apt-get update
            apt-get install -y docker-compose-plugin
        fi

        # Install Git if not present
        if ! command -v git &> /dev/null; then
            apt-get update
            apt-get install -y git
        fi

        echo "Docker: $(docker --version)"
        echo "Docker Compose: $(docker compose version)"
        echo "Git: $(git --version)"
ENDSSH

    echo -e "${GREEN}[2/6] Arret et suppression de l'ancien projet (collectivites_territoriales)...${NC}"
    ssh ${REMOTE_USER}@${REMOTE_HOST} << ENDSSH
        if [ -d "${OLD_DIR}" ]; then
            echo "Arret des anciens containers..."
            cd ${OLD_DIR}

            # Arreter avec les deux formats possibles de docker-compose
            docker compose down 2>/dev/null || true
            docker compose -f docker-compose.yml -f docker-compose.prod.yml down 2>/dev/null || true

            # Supprimer les anciens containers nommes ct_*
            docker rm -f ct_db ct_backend ct_frontend ct_migrations 2>/dev/null || true

            # Supprimer les anciens volumes (ATTENTION: perte de donnees ancien projet)
            docker volume rm ct_postgres_data ct_uploads ct_logs 2>/dev/null || true

            # Supprimer les anciennes images
            docker image prune -f

            echo "Ancien projet arrete et nettoye."
        else
            echo "Aucun ancien projet trouve dans ${OLD_DIR}."
        fi
ENDSSH

    echo -e "${GREEN}[3/6] Creation du repertoire projet...${NC}"
    ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_DIR}"

    echo -e "${GREEN}[4/6] Clonage du repository...${NC}"
    ssh ${REMOTE_USER}@${REMOTE_HOST} << ENDSSH
        cd ${REMOTE_DIR}

        if [ ! -d "pcqvp-platform" ]; then
            echo "Clonage du repository..."
            git clone ${REPO_URL}
        else
            echo "Repository deja present, mise a jour..."
            cd pcqvp-platform
            git fetch origin
            git reset --hard origin/main
        fi
ENDSSH

    echo -e "${GREEN}[5/6] Upload des fichiers de configuration...${NC}"
    scp .env.production.example ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/pcqvp-platform/

    echo -e "${GREEN}[6/6] Generation des secrets et creation du .env...${NC}"
    ssh ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
        cd /opt/pcqvp/pcqvp-platform

        if [ -f ".env" ]; then
            echo "⚠️  .env existe deja, pas de modification."
        else
            # Generer des secrets securises
            JWT_SECRET=$(openssl rand -hex 32)
            POSTGRES_PWD=$(openssl rand -hex 16)
            ADMIN_PWD=$(openssl rand -base64 16)

            # Creer .env depuis l'exemple
            cp .env.production.example .env

            # Remplacer les placeholders
            sed -i "s/CHANGE_ME_GENERATE_RANDOM_SECRET/$JWT_SECRET/" .env
            sed -i "s/CHANGE_ME_STRONG_PASSWORD/$POSTGRES_PWD/" .env
            sed -i "s/CHANGE_ME_ADMIN_PASSWORD/$ADMIN_PWD/" .env

            echo ""
            echo "✅ Secrets generes et sauvegardes dans .env"
            echo ""
            echo "Valeurs generees:"
            echo "  POSTGRES_PASSWORD: $POSTGRES_PWD"
            echo "  JWT_SECRET: $JWT_SECRET"
            echo "  FIRST_ADMIN_PASSWORD: $ADMIN_PWD"
            echo ""
            echo "⚠️  Sauvegardez ces valeurs dans un endroit sur!"
        fi
ENDSSH

    echo -e "${GREEN}=== Setup Termine ===${NC}"
    echo ""
    echo -e "${YELLOW}Prochaine etape:${NC}"
    echo "  ./deploy.sh deploy"
    echo ""
    echo -e "${YELLOW}Optionnel - Editer .env pour personnaliser (SMTP, CORS, etc.):${NC}"
    echo "  ./deploy.sh connect"
    echo "  nano .env"
}

# -----------------------------------------------
# DEPLOY: Full deployment (pull + rebuild + restart)
# -----------------------------------------------
deploy() {
    echo -e "${GREEN}[1/4] Pull du code depuis GitHub...${NC}"
    ssh ${REMOTE_USER}@${REMOTE_HOST} << ENDSSH
        cd ${REMOTE_DIR}/pcqvp-platform
        echo "Mise a jour du code..."
        git fetch origin
        git reset --hard origin/main
ENDSSH

    echo -e "${GREEN}[2/4] Build et demarrage des containers...${NC}"
    ssh ${REMOTE_USER}@${REMOTE_HOST} << ENDSSH
        cd ${REMOTE_DIR}/pcqvp-platform

        # Verifier que .env existe
        if [ ! -f ".env" ]; then
            echo "ERREUR: .env introuvable!"
            echo "Executez d'abord: ./deploy.sh setup"
            exit 1
        fi

        # Demarrer nginx en premier (affiche la page maintenance pendant le build)
        docker compose -f docker-compose.prod.yml up -d nginx 2>/dev/null || true

        # Build et demarrage de tous les services
        docker compose -f docker-compose.prod.yml up -d --build db backend frontend nginx

        # Nettoyage des anciennes images
        docker image prune -f
ENDSSH

    echo -e "${GREEN}[3/4] Execution des migrations...${NC}"
    ssh ${REMOTE_USER}@${REMOTE_HOST} << ENDSSH
        cd ${REMOTE_DIR}/pcqvp-platform
        docker compose -f docker-compose.prod.yml run --rm migrations
ENDSSH

    echo -e "${GREEN}[4/4] Verification du deploiement...${NC}"
    ssh ${REMOTE_USER}@${REMOTE_HOST} << ENDSSH
        cd ${REMOTE_DIR}/pcqvp-platform

        echo "Status des containers:"
        docker compose -f docker-compose.prod.yml ps

        echo ""
        echo "Attente du demarrage des services..."
        sleep 15

        echo ""
        echo "Health checks:"
        curl -sf http://localhost:8080/health && echo " - Backend OK" || echo " - Backend pas encore pret"
        curl -sf http://localhost:8080/ > /dev/null && echo " - Frontend OK" || echo " - Frontend pas encore pret"
ENDSSH

    echo -e "${GREEN}=== Deploiement Termine ===${NC}"
    echo -e "Site accessible: http://${REMOTE_HOST}:8080"
}

# -----------------------------------------------
# UPDATE: Quick update (pull + rebuild)
# -----------------------------------------------
update() {
    echo -e "${GREEN}Pull du code et redemarrage...${NC}"
    ssh ${REMOTE_USER}@${REMOTE_HOST} << ENDSSH
        cd ${REMOTE_DIR}/pcqvp-platform

        # Pull le code
        git fetch origin
        git reset --hard origin/main

        # Rebuild et restart (nginx reste up pendant le build)
        docker compose -f docker-compose.prod.yml up -d --build backend frontend

        # Migrations
        docker compose -f docker-compose.prod.yml run --rm migrations

        # Reload nginx
        docker exec pcqvp_nginx nginx -s reload || true

        echo ""
        echo "Attente du demarrage..."
        sleep 10

        echo "Health checks:"
        curl -sf http://localhost:8080/health && echo " - Backend OK" || echo " - Backend pas encore pret"
ENDSSH
    echo -e "${GREEN}Mise a jour terminee!${NC}"
}

# -----------------------------------------------
# LOGS: View logs
# -----------------------------------------------
logs() {
    SERVICE=${2:-}
    if [ -n "$SERVICE" ]; then
        ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_DIR}/pcqvp-platform && docker compose -f docker-compose.prod.yml logs -f ${SERVICE}"
    else
        ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_DIR}/pcqvp-platform && docker compose -f docker-compose.prod.yml logs -f"
    fi
}

# -----------------------------------------------
# RESTART: Restart services
# -----------------------------------------------
restart() {
    SERVICE=${2:-}
    if [ -n "$SERVICE" ]; then
        ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_DIR}/pcqvp-platform && docker compose -f docker-compose.prod.yml restart ${SERVICE}"
    else
        ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_DIR}/pcqvp-platform && docker compose -f docker-compose.prod.yml restart"
    fi
}

# -----------------------------------------------
# STOP: Stop all services
# -----------------------------------------------
stop() {
    ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_DIR}/pcqvp-platform && docker compose -f docker-compose.prod.yml down"
}

# -----------------------------------------------
# STATUS: Show status
# -----------------------------------------------
status() {
    ssh ${REMOTE_USER}@${REMOTE_HOST} << ENDSSH
        cd ${REMOTE_DIR}/pcqvp-platform

        echo "=== Status des Containers ==="
        docker compose -f docker-compose.prod.yml ps

        echo ""
        echo "=== Git Status ==="
        git log -1 --oneline

        echo ""
        echo "=== Utilisation Disque ==="
        df -h / | tail -1

        echo ""
        echo "=== Utilisation Memoire ==="
        free -h | head -2

        echo ""
        echo "=== Health Checks ==="
        curl -sf http://localhost:8080/health && echo " - Backend OK" || echo " - Backend KO"
        curl -sf http://localhost:8080/ > /dev/null && echo " - Frontend OK" || echo " - Frontend KO"
ENDSSH
}

# -----------------------------------------------
# SSL: Setup Let's Encrypt
# -----------------------------------------------
ssl() {
    DOMAIN=${2:-kaominina-mangarahara.mg}
    echo -e "${GREEN}Configuration SSL pour ${DOMAIN}...${NC}"
    ssh ${REMOTE_USER}@${REMOTE_HOST} << ENDSSH
        apt-get update
        apt-get install -y certbot

        # Arreter nginx temporairement
        docker stop pcqvp_nginx || true

        # Obtenir le certificat
        certbot certonly --standalone -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos --email admin@pcqvp.mg

        # Copier les certificats
        mkdir -p ${REMOTE_DIR}/pcqvp-platform/nginx/ssl
        cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem ${REMOTE_DIR}/pcqvp-platform/nginx/ssl/
        cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem ${REMOTE_DIR}/pcqvp-platform/nginx/ssl/

        # Redemarrer nginx
        docker start pcqvp_nginx

        # Cron pour renouvellement auto
        (crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --post-hook 'docker restart pcqvp_nginx'") | crontab -

        echo ""
        echo "Certificats SSL installes!"
        echo "Mettez a jour nginx.conf pour activer HTTPS, puis: ./deploy.sh restart nginx"
ENDSSH
}

# -----------------------------------------------
# BACKUP: Backup database
# -----------------------------------------------
backup() {
    BACKUP_DIR="backups"
    mkdir -p ${BACKUP_DIR}
    BACKUP_FILE="${BACKUP_DIR}/backup_pcqvp_$(date +%Y%m%d_%H%M%S).sql"
    echo -e "${GREEN}Sauvegarde de la base de donnees...${NC}"
    ssh ${REMOTE_USER}@${REMOTE_HOST} "docker exec pcqvp_db pg_dump -U pcqvp pcqvp" > ${BACKUP_FILE}
    echo -e "${GREEN}Sauvegarde enregistree: ${BACKUP_FILE}${NC}"
}

# -----------------------------------------------
# CONNECT: SSH into server
# -----------------------------------------------
connect() {
    ssh ${REMOTE_USER}@${REMOTE_HOST} -t "cd ${REMOTE_DIR}/pcqvp-platform && bash"
}

# -----------------------------------------------
# CLEANUP-OLD: Remove old project completely
# -----------------------------------------------
cleanup-old() {
    echo -e "${YELLOW}Suppression complete de l'ancien projet collectivites_territoriales...${NC}"
    ssh ${REMOTE_USER}@${REMOTE_HOST} << ENDSSH
        # Arreter et supprimer les anciens containers
        if [ -d "${OLD_DIR}" ]; then
            cd ${OLD_DIR}
            docker compose down 2>/dev/null || true
            docker compose -f docker-compose.yml -f docker-compose.prod.yml down 2>/dev/null || true
        fi

        # Supprimer les containers nommes ct_*
        docker rm -f ct_db ct_backend ct_frontend ct_migrations 2>/dev/null || true

        # Supprimer les volumes
        docker volume rm ct_postgres_data ct_uploads ct_logs 2>/dev/null || true

        # Supprimer aussi les anciens volumes avec le nom revenus_miniers
        docker rm -f revenus_miniers_db revenus_miniers_backend revenus_miniers_frontend revenus_miniers_db_init revenus_miniers_migrations 2>/dev/null || true
        docker volume rm revenus_miniers_postgres_data revenus_miniers_uploads revenus_miniers_logs 2>/dev/null || true

        # Supprimer le repertoire
        rm -rf ${OLD_DIR}

        # Nettoyage Docker
        docker image prune -f
        docker network prune -f

        echo "✅ Ancien projet completement supprime."
ENDSSH
    echo -e "${GREEN}Nettoyage termine.${NC}"
}

# -----------------------------------------------
# MAIN
# -----------------------------------------------
case "$1" in
    setup)
        setup
        ;;
    deploy)
        deploy
        ;;
    update)
        update
        ;;
    logs)
        logs "$@"
        ;;
    restart)
        restart "$@"
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    ssl)
        ssl "$@"
        ;;
    backup)
        backup
        ;;
    connect)
        connect
        ;;
    cleanup-old)
        cleanup-old
        ;;
    *)
        echo "Usage: $0 {commande} [options]"
        echo ""
        echo "Commandes:"
        echo "  setup          - Installation initiale (Docker, clone repo, supprime ancien projet)"
        echo "  deploy         - Deploiement complet (pull, rebuild, migrations, restart)"
        echo "  update         - Mise a jour rapide (pull, rebuild, migrations)"
        echo "  logs [service] - Voir les logs (optionnel: backend, frontend, db, nginx)"
        echo "  restart [svc]  - Redemarrer les services (optionnel: service specifique)"
        echo "  stop           - Arreter tous les services"
        echo "  status         - Afficher le status (containers, git, ressources)"
        echo "  ssl [domain]   - Configurer SSL (defaut: kaominina-mangarahara.mg)"
        echo "  backup         - Sauvegarder la base de donnees en local"
        echo "  connect        - Connexion SSH au serveur"
        echo "  cleanup-old    - Supprimer completement l'ancien projet"
        echo ""
        echo "Exemples:"
        echo "  $0 setup                              # Installation initiale"
        echo "  $0 deploy                             # Deployer/mettre a jour"
        echo "  $0 logs backend                       # Logs du backend"
        echo "  $0 restart frontend                   # Redemarrer le frontend"
        echo "  $0 ssl kaominina-mangarahara.mg       # Configurer SSL"
        echo "  $0 backup                             # Sauvegarder la BDD"
        exit 1
        ;;
esac
