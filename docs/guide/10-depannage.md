# Chapitre 10 - Depannage

Ce chapitre regroupe les problemes les plus courants rencontres lors de l'utilisation et de la maintenance de la plateforme PCQVP, ainsi que les procedures pour les resoudre.

---

## Problemes de connexion

### Impossible de se connecter

- Verifier l'email et le mot de passe saisis
- Si le compte est verrouille (message "compte verrouille"), attendre 30 minutes que le verrou expire automatiquement
- Verifier que l'utilisateur existe en base de donnees :
  ```sql
  SELECT email, is_active, failed_login_attempts, locked_until
  FROM users
  WHERE email = 'email@example.com';
  ```
- Remettre a zero le compteur de tentatives echouees :
  ```sql
  UPDATE users
  SET failed_login_attempts = 0, locked_until = NULL
  WHERE email = 'email@example.com';
  ```
- Verifier que `is_active = true` ; si ce n'est pas le cas, le compte a ete desactive manuellement

### Session expiree frequemment

- Le token d'acces expire apres 30 minutes (configurable via la variable `ACCESS_TOKEN_EXPIRE_MINUTES` dans `.env`)
- Le refresh token dure 7 jours et permet le renouvellement transparent de la session
- Si le probleme persiste, verifier que les cookies sont actives dans le navigateur
- Verifier que `JWT_SECRET_KEY` n'a pas change entre deux redemarrages du serveur ; un changement de cette cle invalide toutes les sessions en cours

---

## Problemes de base de donnees

### La base ne demarre pas

```bash
docker compose logs postgres          # Consulter les logs du conteneur
docker compose ps                     # Verifier l'etat du conteneur
```

- Verifier que le port 5432 n'est pas deja utilise par un autre service sur la machine hote
- Verifier que les variables `POSTGRES_USER`, `POSTGRES_PASSWORD` et `POSTGRES_DB` dans `.env` correspondent aux valeurs attendues

### Erreur de migration

```bash
cd backend
alembic history                       # Voir l'historique complet des migrations
alembic current                       # Afficher la migration actuellement appliquee
alembic upgrade head                  # Appliquer toutes les migrations manquantes
alembic downgrade -1                  # Annuler la derniere migration appliquee
```

En cas de migration en conflit ou corrompue, examiner le contenu de la table `alembic_version` en base pour identifier la version courante, puis corriger ou recreer la migration problematique.

### Reinitialiser completement la base de donnees

Cette operation est destructive et supprime toutes les donnees existantes.

```bash
docker compose down -v                # Supprimer le conteneur et le volume de donnees
docker compose up -d                  # Recreer le conteneur et initialiser la base
cd backend
alembic upgrade head                  # Reappliquer l'ensemble des migrations
python -m app.seed                    # Re-seeder les donnees initiales
```

---

## Problemes de templates

### Les templates ne se chargent pas

Verifier que des templates existent et sont actifs en base :

```sql
SELECT id, name, type, is_active FROM account_templates;
```

- Verifier qu'au moins un template est actif (`is_active = true`) pour chaque type utilise
- Si aucun template n'existe, relancer le seed : `python -m app.seed`

### Les lignes du template sont vides

```sql
SELECT COUNT(*) FROM account_template_lines WHERE template_id = '<id_du_template>';
```

Valeurs de reference attendues :

- Un template de recettes doit contenir environ 168 lignes
- Un template de depenses doit contenir environ 273 lignes

Si le nombre de lignes est nul ou insuffisant, le template n'a pas ete correctement seede. Relancer le seed ou reinserter les lignes manuellement.

---

## Problemes de comptes administratifs

### Impossible de creer un compte

- Verifier que la collectivite ciblee existe bien dans la table de geographie
- Verifier la contrainte d'unicite : un seul compte peut exister par combinaison (type, collectivite, annee d'exercice) :
  ```sql
  SELECT *
  FROM comptes_administratifs
  WHERE collectivite_id = '<id>'
    AND annee_exercice = 2023;
  ```
- Verifier que l'annee saisie est bien un entier numerique valide

### Les calculs automatiques ne fonctionnent pas

- Les calculs sont effectues cote serveur lors de la sauvegarde de la ligne ; sauvegarder explicitement avant de consulter le resultat
- Recharger la page apres la sauvegarde pour afficher les valeurs recalculees
- Verifier dans le template que les colonnes concernees ont bien `is_computed = true`

### Un compte ne s'affiche pas sur le site public

- Verifier que le statut du compte est "publie" ; seul un administrateur peut effectuer cette action
- Verifier l'etat du compte via l'API : `GET /api/admin/comptes/<id>` et controler le champ `status` dans la reponse

---

## Problemes d'upload d'images

### L'upload echoue

- Verifier que le type de fichier est accepte : JPEG, PNG, WebP ou GIF uniquement
- Verifier que la taille du fichier est inferieure a 5 Mo
- Verifier que le repertoire `uploads/images` existe sur le serveur et que le processus backend dispose des permissions d'ecriture sur ce repertoire
- Consulter les logs du backend pour obtenir le message d'erreur detaille

### L'image ne s'affiche pas apres l'upload

- Verifier que le proxy Nuxt est bien configure pour rediriger les requetes `/uploads/**` vers le backend
- Verifier que le fichier est physiquement present sur le disque dans le repertoire d'uploads configure
- Verifier que l'URL retournee par l'API est correcte et accessible depuis le navigateur

---

## Problemes de geographie

### Impossible de supprimer une province ou une region

- Une reponse HTTP 409 (Conflict) indique que l'entite possede des entites enfants
- L'ordre de suppression doit respecter la hierarchie : supprimer d'abord les communes, puis les regions, puis les provinces
- Les contraintes `RESTRICT` sur les cles etrangeres empechent toute suppression en cascade involontaire

### La recherche geographique ne trouve rien

- L'index de recherche plein texte utilise la configuration linguistique francaise (TSVECTOR)
- En cas de probleme, reconstruire l'index GIN :
  ```sql
  REINDEX INDEX idx_provinces_search;
  ```

---

## Problemes du frontend

### Le serveur de developpement ne demarre pas

```bash
cd frontend
rm -rf node_modules .nuxt
pnpm install
pnpm dev
```

Cette sequence supprime les caches et reinstalle les dependances, ce qui resout la majorite des problemes de demarrage.

### Erreur de proxy API (requetes `/api/**` echouent)

- Verifier que le serveur backend est bien demarre et ecoute sur le port 8000
- Verifier la configuration `routeRules` dans `nuxt.config.ts` pour s'assurer que le proxy est correctement defini
- En production, verifier que la variable d'environnement `NUXT_BACKEND_URL` pointe vers l'URL correcte du backend

### Le mode sombre ne fonctionne pas

- Le color mode utilise la strategie `class` via le module `@nuxtjs/color-mode` ; la classe `dark` doit etre presente sur l'element `<html>`
- Verifier que les classes utilitaires `dark:` de Tailwind sont bien presentes dans les composants concernes
- Le bouton de bascule entre les modes est situe dans le header de l'interface d'administration

---

## Commandes utiles de reference

### Backend

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000  # Demarrer le serveur
pytest                                                      # Lancer tous les tests
pytest tests/test_auth.py -v                                # Tester un fichier specifique
ruff check .                                                # Verifier le style du code
ruff check . --fix                                          # Corriger automatiquement les erreurs
```

### Frontend

```bash
pnpm dev                              # Demarrer le serveur de developpement (port 3000)
pnpm build                            # Compiler pour la production
```

### Docker

```bash
docker compose up -d                  # Demarrer PostgreSQL en arriere-plan
docker compose down                   # Arreter les services (donnees preservees)
docker compose logs -f postgres       # Afficher les logs en temps reel
docker compose ps                     # Verifier l'etat de tous les services
```

### Base de donnees

```bash
psql -h localhost -U pcqvp -d pcqvp   # Connexion directe a la base de donnees
alembic upgrade head                  # Appliquer les migrations en attente
alembic history                       # Afficher l'historique des migrations
python -m app.seed                    # Reinitialiser les donnees de reference
```
