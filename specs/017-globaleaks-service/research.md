# Research: Service de signalement GlobalLeaks

**Feature**: 017-globaleaks-service | **Date**: 2026-03-30

## R1: Deploiement Docker de GlobalLeaks

**Decision**: Utiliser l'image officielle `globaleaks/globaleaks:latest` (v5.0.89) avec un `docker-compose.globaleaks.yml` dedie.

**Rationale**: L'image officielle est maintenue par l'equipe GlobalLeaks, inclut toutes les dependances, et utilise SQLite integre (pas de base externe). Le fichier compose est separe car l'instance est partagee entre plusieurs sites.

**Configuration cle**:
- Image : `globaleaks/globaleaks:latest` (linux/amd64 uniquement)
- Ports internes : 8080 (HTTP), 8443 (HTTPS)
- Volume : `/var/globaleaks` contient TOUT (DB SQLite, fichiers, cles, config Tor, certificats)
- Sante : `https://localhost:8443/api/health`
- Ressources minimales : 1 vCPU, 1 GB RAM, 20 GB stockage

**Alternatives considerees**:
- Installation native (script shell) : rejetee car Docker offre meilleure isolation et portabilite
- Ajout au docker-compose.yml principal du projet : rejete car l'instance est partagee entre sites

## R2: Configuration Tor (.onion)

**Decision**: Utiliser un conteneur Tor sidecar (ex: `goldy/tor-hidden-service`) lie au conteneur GlobalLeaks.

**Rationale**: L'image Docker officielle n'inclut pas Tor par defaut. Un sidecar dedie est plus propre et permet de gerer le cycle de vie Tor independamment.

**Configuration**:
- Le sidecar genere automatiquement l'adresse .onion
- Les cles Tor sont persistees dans un volume dedie
- L'adresse .onion est ensuite configuree dans Admin > Network > Tor

**Alternatives considerees**:
- Tor installe sur l'hote : rejete pour isolation et portabilite
- Tor integre dans un Dockerfile custom : rejete pour eviter de maintenir une image custom

## R3: Domaine personnalise (alerte.miningobs.mg)

**Decision**: Configurer le domaine dans l'interface Admin > Network > HTTPS de GlobalLeaks, avec Let's Encrypt pour les certificats.

**Rationale**: GlobalLeaks integre nativement Let's Encrypt. En phase initiale (avant DNS), acces par IP:port (8443).

**Etapes**:
1. Deployer avec acces IP:8443 / IP:8080
2. Completer le wizard d'initialisation
3. Configurer le DNS A record vers le serveur
4. Activer HTTPS avec Let's Encrypt dans Admin > Network

**Alternatives considerees**:
- Reverse proxy nginx avec TLS termination : possible mais ajoute de la complexite; Let's Encrypt integre est suffisant pour ce cas d'usage

## R4: Sauvegarde et restauration

**Decision**: Script de backup periodique du volume Docker + commande `gl-admin backup` integree.

**Rationale**: Le volume `/var/globaleaks` contient toutes les donnees. Un simple tar du volume suffit.

**Procedure**:
```bash
# Backup
docker exec globaleaks gl-admin backup
docker cp globaleaks:/tmp/globaleaks_backup_*.tar.gz ./backups/

# Restore
docker cp backup.tar.gz globaleaks:/tmp/
docker exec globaleaks gl-admin restore /tmp/backup.tar.gz
```

**Automatisation** : cron job quotidien recommande.

## R5: Canaux thematiques

**Decision**: Creer 4 canaux dans Admin > Channels, chacun avec un questionnaire dedie.

**Rationale**: GlobalLeaks supporte nativement les canaux multiples avec routage vers des destinataires differents.

**Canaux prevus**:
1. **Fiscalite / Paiements** : irregularites fiscales, flux financiers opaques
2. **Environnement** : pollution, exploitation illegale, non-respect des normes
3. **Social / Communautaire** : impact sur les communautes, deplacements, droits
4. **Gouvernance / Corruption** : abus de pouvoir, conflits d'interet, corruption

**Questionnaire commun (champs de base)** : type d'irregularite, localisation geographique, entites impliquees, periode concernee, description detaillee, pieces jointes.

## R6: Multilinguisme (francais + malgache)

**Decision**: Francais comme langue par defaut. Malgache via la fonctionnalite "Text customization" de GlobalLeaks.

**Rationale**: Le francais est disponible nativement dans GlobalLeaks (70+ langues). Le malgache n'est probablement pas dans les traductions Transifex. La fonctionnalite de personnalisation de texte permet de fournir des traductions manuelles pour chaque chaine de caracteres.

**Alternatives considerees**:
- Contribuer une traduction malgache sur Transifex : bon a long terme mais trop lent pour le lancement initial

## R7: Integration frontend PCQVP existante

**Decision**: Reutiliser l'infrastructure existante (page `signaler.vue`, composable `useSiteConfig`, endpoint API `/api/public/config/globalleaks`).

**Rationale**: Le frontend dispose deja d'une page de signalement complete avec lien vers GlobalLeaks. Il suffit de configurer l'URL dans le backend via l'endpoint de config existant.

**Aucun changement de code frontend necessaire** si l'URL est correctement configuree dans la base de donnees de config du backend PCQVP.
