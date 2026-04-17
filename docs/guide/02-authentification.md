# Chapitre 2 - Authentification et gestion des utilisateurs

## Connexion

L'interface d'administration est accessible via la page de connexion a l'adresse `/admin/login`.

Le formulaire de connexion requiert deux champs :

- **Email** : l'adresse email associee au compte utilisateur
- **Mot de passe** : le mot de passe du compte

Apres une connexion reussie, l'utilisateur est automatiquement redirige vers le tableau de bord d'administration.

**Compte verrouille**

Si le compte a ete verrouille suite a plusieurs tentatives echouees, le serveur retourne une erreur HTTP 423. Dans ce cas, il est necessaire d'attendre 30 minutes avant de tenter une nouvelle connexion. Aucune action manuelle de deverrouillage n'est requise : le verrouillage expire automatiquement.

---

## Systeme de tokens JWT

L'authentification repose sur une architecture a deux tokens :

### Access token

- Duree de validite : 30 minutes
- Stockage : en memoire (non persistant entre les rechargements de page)
- Usage : transmis dans l'en-tete `Authorization` de chaque requete API protegee

### Refresh token

- Duree de validite : 7 jours
- Stockage : cookie HTTP-only securise (inaccessible depuis JavaScript)
- Usage : permet de renouveler l'access token expire sans que l'utilisateur ait a se reconnecter

### Renouvellement automatique

Lorsque l'access token expire, le frontend tente automatiquement de le renouveler a l'aide du refresh token. Ce processus est transparent pour l'utilisateur. Si le refresh token est lui-meme expire ou invalide, l'utilisateur est redirige vers la page de connexion.

### Algorithme de signature

Les tokens sont signes avec l'algorithme HMAC-SHA256 (HS256), en utilisant une cle secrete definie dans la configuration du backend (`SECRET_KEY`).

---

## Securite des mots de passe

### Hashage

Les mots de passe sont hashes avec l'algorithme bcrypt, qui integre un sel aleatoire pour chaque hash. Le mot de passe en clair n'est jamais stocke en base de donnees.

### Longueur minimale

La longueur minimale d'un mot de passe est de 8 caracteres, conformement aux recommandations NIST SP 800-63B.

### Verrouillage de compte

Pour proteger contre les attaques par force brute, un mecanisme de verrouillage progressif est en place :

- Apres **5 tentatives de connexion echouees consecutives**, le compte est verrouille
- La duree de verrouillage est de **30 minutes** (valeur configurable dans le fichier `.env`)
- Une connexion reussie remet le compteur d'echecs a zero

---

## Roles utilisateurs

La plateforme distingue deux roles d'utilisateurs : `admin` et `editor`. Les permissions sont exclusives et non cumulatives.

### Administrateur (`admin`)

L'administrateur dispose de l'ensemble des droits sur la plateforme :

- Creer, modifier et gerer les comptes utilisateurs
- Attribuer ou modifier les roles des utilisateurs
- Activer et desactiver des comptes utilisateurs
- Publier et depublier les comptes administratifs
- Purger les donnees analytiques (statistiques de visites)
- Gerer la configuration systeme
- Acceder a toutes les fonctionnalites disponibles pour le role editeur

### Editeur (`editor`)

L'editeur dispose d'un perimetre fonctionnel limite aux contenus :

- Creer et saisir les comptes administratifs (sans pouvoir les publier)
- Gerer le contenu geographique : descriptions textuelles et images des provinces, regions et communes
- Gerer le contenu editorial : section hero, pied de page

**Restrictions du role editeur :**

- Ne peut pas publier ni depublier les comptes administratifs
- Ne peut pas creer, modifier ou desactiver des comptes utilisateurs
- Ne peut pas acceder aux sections de configuration systeme et d'analytique

---

## Gestion des utilisateurs

**Acces reserve aux administrateurs.**

La gestion des utilisateurs est disponible a l'adresse `/admin/users`.

### Liste des utilisateurs

La page affiche l'ensemble des comptes utilisateurs enregistres, avec pour chacun :

- L'adresse email
- Le role attribue (`admin` ou `editor`)
- Le statut du compte (actif ou desactive)

### Creer un nouvel utilisateur

Pour creer un compte, l'administrateur renseigne :

- L'adresse email (doit etre unique)
- Le mot de passe initial (minimum 8 caracteres)
- Le role : `admin` ou `editor`

Il est recommande de communiquer le mot de passe initial par un canal securise et d'inviter l'utilisateur a le changer des sa premiere connexion.

### Activer et desactiver un compte

Un administrateur peut activer ou desactiver n'importe quel compte utilisateur, a l'exception du sien propre (il n'est pas possible de se desactiver soi-meme). Un utilisateur dont le compte est desactive ne peut plus se connecter a la plateforme.

---

## Premier administrateur

Le premier compte administrateur est cree via le script de seeding inclus dans le backend :

```bash
cd backend
source .venv/bin/activate
python -m app.seed
```

Ce script lit les variables d'environnement suivantes depuis le fichier `.env` :

| Variable | Description |
|---|---|
| `FIRST_ADMIN_EMAIL` | Adresse email du premier administrateur |
| `FIRST_ADMIN_PASSWORD` | Mot de passe du premier administrateur |

**Comportement idempotent :** si un compte avec l'adresse email specifiee existe deja en base de donnees, le script ne cree pas de doublon et ne modifie pas le compte existant.

---

## Protection des routes

Toutes les pages de l'espace d'administration (`/admin/*`), a l'exception de `/admin/login`, sont protegees par un middleware d'authentification cote frontend.

### Flux de verification

A chaque navigation vers une route protegee, le middleware suit le processus suivant :

1. **Verification de l'access token en memoire** : si un token valide est present, la navigation est autorisee.
2. **Tentative de recuperation de l'utilisateur** : si aucun token n'est present en memoire, le middleware tente de recuperer les informations de l'utilisateur courant via l'API.
3. **Tentative de renouvellement du token** : si la recuperation echoue (token expire), le middleware tente de renouveler l'access token via le refresh token stocke dans le cookie.
4. **Redirection vers la page de connexion** : si toutes les etapes precedentes echouent, l'utilisateur est redirige vers `/admin/login`.

### Layout d'administration

Les routes de l'espace admin utilisent le layout `admin`, qui integre la barre laterale de navigation (sidebar) et l'en-tete (header). Ce layout n'est pas charge pour la page de connexion.
