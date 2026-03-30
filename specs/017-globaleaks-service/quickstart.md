# Quickstart: Service de signalement GlobalLeaks

**Feature**: 017-globaleaks-service | **Date**: 2026-03-30

## Prerequis

- Docker et Docker Compose installes sur le serveur
- Acces SSH au serveur
- Port 8080 et 8443 disponibles (ou 80/443 si pas de reverse proxy)
- Acces internet pour telecharger l'image Docker et les certificats Let's Encrypt

## 1. Deploiement initial

Creer le fichier `docker-compose.globaleaks.yml` sur le serveur :

```yaml
services:
  globaleaks:
    image: globaleaks/globaleaks:latest
    platform: linux/amd64
    restart: unless-stopped
    container_name: globaleaks
    ports:
      - "80:8080"
      - "443:8443"
    volumes:
      - globaleaks-data:/var/globaleaks:rw
    healthcheck:
      test: ["CMD", "curl", "-k", "-f", "https://localhost:8443/api/health"]
      interval: 30s
      timeout: 5s
      retries: 12
      start_period: 60s

  tor:
    image: goldy/tor-hidden-service:latest
    restart: unless-stopped
    container_name: globaleaks-tor
    environment:
      GLOBALEAKS_TOR_SERVICE_HOSTS: "80:globaleaks:8080"
    depends_on:
      - globaleaks
    volumes:
      - tor-keys:/var/lib/tor/hidden_service/

volumes:
  globaleaks-data:
  tor-keys:
```

Lancer :

```bash
docker compose -f docker-compose.globaleaks.yml up -d
```

## 2. Acces initial

- **Avant DNS** : `https://<IP-serveur>:443` (accepter l'avertissement certificat auto-signe)
- **Apres DNS** : `https://alerte.miningobs.mg`

## 3. Wizard d'initialisation

1. Langue par defaut : **Francais**
2. Nom du projet : **Alerte Industries Extractives Madagascar**
3. Compte administrateur : email + mot de passe fort
4. Premier destinataire : nom + email du responsable PCQVP
5. Accepter la licence AGPL
6. Terminer

## 4. Configuration post-wizard

### 4.1 HTTPS & Domaine (Admin > Network > HTTPS)
- Saisir `alerte.miningobs.mg` comme nom de domaine
- Activer Let's Encrypt (necessite DNS configure + ports 80/443 accessibles)

### 4.2 Tor (Admin > Network > Tor)
- Recuperer l'adresse .onion : `docker exec globaleaks-tor cat /var/lib/tor/hidden_service/hostname`
- Saisir l'adresse dans la configuration Tor de GlobalLeaks

### 4.3 Langues (Admin > Settings > Languages)
- Activer le francais (defaut) et le malgache
- Utiliser "Text customization" pour les traductions malgaches

### 4.4 Canaux (Admin > Channels)
Creer 4 canaux :
1. **Fiscalite / Paiements**
2. **Environnement**
3. **Social / Communautaire**
4. **Gouvernance / Corruption**

### 4.5 Questionnaires (Admin > Questionnaires)
Pour chaque canal, configurer les champs :
- Type d'irregularite (selection)
- Localisation geographique (texte)
- Entites impliquees (texte multiligne)
- Periode concernee (plage de dates)
- Description detaillee (texte multiligne)
- Pieces jointes (fichier)

### 4.6 Destinataires (Admin > Users)
- Ajouter les membres de l'equipe PCQVP comme destinataires
- Assigner chaque destinataire aux canaux pertinents
- Recommander l'activation du 2FA

## 5. Integration PCQVP

Configurer l'URL de GlobalLeaks dans le backend PCQVP :
- Via l'interface admin PCQVP : Admin > Configuration > URL GlobalLeaks
- Valeur : `https://alerte.miningobs.mg` (ou `https://<IP>:443` temporairement)
- La page `/signaler` du frontend affichera automatiquement le lien

## 6. Sauvegarde

Mettre en place un cron job quotidien :

```bash
# /etc/cron.daily/globaleaks-backup
#!/bin/bash
docker exec globaleaks gl-admin backup
docker cp globaleaks:/tmp/globaleaks_backup_*.tar.gz /backups/globaleaks/
find /backups/globaleaks -mtime +30 -delete
```

## 7. Verification

- [ ] GlobalLeaks accessible sur `https://alerte.miningobs.mg` (ou IP:443)
- [ ] Adresse .onion fonctionnelle via Tor Browser
- [ ] 4 canaux visibles sur la page d'accueil GlobalLeaks
- [ ] Soumission de test reussie avec code d'acces recu
- [ ] Notification email recue par le destinataire
- [ ] Page `/signaler` sur PCQVP affiche le lien vers GlobalLeaks
- [ ] Backup fonctionnel
