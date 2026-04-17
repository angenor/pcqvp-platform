# Chapitre 9 - Configuration et GlobalLeaks

## Configuration systeme

### Acces

La page de configuration est accessible a l'URL `/admin/config`. Elle est reservee aux administrateurs disposant du role `admin`.

### Parametres disponibles

- **URL GlobalLeaks** : adresse de l'instance de signalement (exemple : `https://alerte.miningobs.mg`). Ce parametre est stocke sous la cle `globalleaks_url` dans la table `site_config`.

Les parametres sont stockes en base de donnees dans la table `site_config` selon un modele cle/valeur, ce qui permet de les modifier sans redeployer l'application.

### Variables d'environnement

Les parametres systeme de bas niveau sont configures via le fichier `.env` situe dans le dossier parent du depot. Ces variables ne sont pas modifiables depuis l'interface d'administration.

| Variable | Description | Exemple |
|----------|-------------|---------|
| `DATABASE_URL` | Connexion PostgreSQL | `postgresql+asyncpg://pcqvp:pass@localhost:5432/pcqvp` |
| `JWT_SECRET_KEY` | Cle secrete pour les tokens | (chaine aleatoire longue) |
| `JWT_ALGORITHM` | Algorithme JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duree du token d'acces | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Duree du refresh token | `7` |
| `FIRST_ADMIN_EMAIL` | Email du premier administrateur | `admin@example.com` |
| `FIRST_ADMIN_PASSWORD` | Mot de passe du premier administrateur | `SecurePassword123!` |
| `POSTGRES_USER` | Utilisateur PostgreSQL | `pcqvp` |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | `password` |
| `POSTGRES_DB` | Nom de la base de donnees | `pcqvp` |
| `UPLOAD_DIR` | Repertoire des fichiers uploades | `./uploads/images` |
| `MAX_IMAGE_SIZE` | Taille maximale des images (en octets) | `5242880` |
| `ALLOWED_IMAGE_TYPES` | Types MIME autorises pour les images | `image/jpeg,image/png,image/webp,image/gif` |

Toute modification du fichier `.env` necessite un redemarrage du serveur backend pour prendre effet.

---

## GlobalLeaks - Plateforme de signalement

### Presentation

GlobalLeaks est une plateforme open source de signalement anonyme integree a PCQVP. Elle permet aux citoyens et lanceurs d'alerte de signaler des irregularites liees aux industries extractives de maniere anonyme et securisee, sans creer de compte ni divulguer leur identite.

### Instance

| Parametre | Valeur |
|-----------|--------|
| Domaine | `alerte.miningobs.mg` |
| Logiciel | GlobalLeaks 5.0.89 |
| Deploiement | Docker (`globaleaks/globaleaks:latest`) |
| Base de donnees | SQLite interne (volume Docker `globaleaks-data`) |

L'instance GlobalLeaks est independante de la base de donnees PostgreSQL principale de PCQVP. Elle gere ses propres donnees via un volume Docker dedie.

### Fonctionnalites pour les lanceurs d'alerte

- Soumission anonyme de signalements sans compte requis
- Pieces jointes possibles (documents, images)
- Code d'acces unique genere automatiquement pour le suivi du signalement
- Communication bidirectionnelle anonyme avec les destinataires du signalement

### Fonctionnalites pour les administrateurs et destinataires

- Tableau de bord listant l'ensemble des signalements recus
- Telechargement des pieces jointes soumises par les lanceurs d'alerte
- Gestion du cycle de vie des signalements avec les statuts suivants : nouveau, en cours, resolu, archive
- Envoi de messages aux lanceurs d'alerte via le canal anonyme integre

### Questionnaire thematique

GlobalLeaks est configure avec quatre canaux de signalement correspondant aux domaines prioritaires de la transparence extractive :

1. Irregularites fiscales et paiements
2. Environnement
3. Social et communautaire
4. Gouvernance et corruption

Chaque canal dispose d'un questionnaire adapte au type d'irregularite signale.

### Securite

GlobalLeaks integre plusieurs mecanismes de protection des sources :

- Chiffrement des donnees au repos et en transit
- Acces via le reseau Tor (adresse .onion) pour un anonymat renforce
- Interface disponible en francais et en malgache
- Conservation indefinie des signalements (la suppression est effectuee manuellement par un administrateur)
- Notifications par email aux destinataires lors de la reception d'un nouveau signalement

### Integration avec la plateforme PCQVP

GlobalLeaks est integre a PCQVP de la maniere suivante :

- Lien de navigation present dans l'en-tete et le pied de page du site public
- Page d'explication dediee decrivant le fonctionnement du dispositif de signalement
- URL de l'instance configurable depuis l'interface d'administration via `/admin/config` (cle `globalleaks_url`)

Cette architecture permet de modifier l'URL de l'instance GlobalLeaks sans intervention technique directe dans le code ou les fichiers de configuration.

### Configuration Docker GlobalLeaks

L'instance GlobalLeaks est deployee via un fichier Docker Compose distinct de celui de PCQVP. Les points de configuration specifiques sont les suivants :

- Le port interne 80 de GlobalLeaks est remappes sur le port 8880 de l'hote afin d'eviter les conflits avec nginx
- Un volume Docker nomme `globaleaks-data` assure la persistance des donnees entre les redemarrages du conteneur
- Le service Tor est integre directement dans le conteneur GlobalLeaks, aucune configuration externe n'est necessaire pour l'acces .onion
