# Research: Fonctionnalites transverses

**Date**: 2026-03-21
**Feature**: 010-cross-cutting-features

## R1: Recherche full-text PostgreSQL avec unaccent

**Decision**: Utiliser `tsvector` genere (stored) + GIN index + extension `unaccent` via une configuration de recherche personnalisee `fr_unaccent`.

**Rationale**: Les colonnes tsvector generees evitent de recalculer a chaque requete. GIN est le choix canonique pour tsvector. La config personnalisee integre unaccent nativement. Aucune dependance externe.

**Implementation**:
- Migration Alembic : `CREATE EXTENSION IF NOT EXISTS unaccent;` + creation d'une config `fr_unaccent` (copie de `french` avec `unaccent` + `french_stem`)
- Colonne `search_vector` generee sur Province, Region, Commune (sur `name`)
- Pour les comptes : recherche sur le nom de la commune associee + `annee_exercice::text`
- Requete cross-table via UNION SQL ou recherche sequentielle par type
- Index GIN sur chaque `search_vector`

**Alternatives rejetees**:
- Trigram (`pg_trgm`) : meilleur pour typos mais moins performant pour le ranking. Peut completer mais pas remplacer.
- Elasticsearch/Meilisearch : surdimensionne pour le volume attendu.
- Unaccent applicatif (Python `unidecode`) : fragile, necessite de normaliser donnees et requetes.

## R2: Rate limiting sur FastAPI

**Decision**: Utiliser `slowapi` avec stockage en memoire.

**Rationale**: slowapi est le standard de facto pour FastAPI, wrapper leger autour de `limits`. Le stockage memoire suffit pour un deploiement mono-processus. Passage a Redis possible avec un changement d'une ligne.

**Limites recommandees**:
- Recherche publique : 30 requetes/minute par IP
- Inscription newsletter : 5 requetes/minute par IP
- Endpoints d'export : 10 requetes/minute par IP

**Alternatives rejetees**:
- fastapi-limiter : necessite Redis obligatoirement.
- Nginx rate limiting : pas de granularite par endpoint facilement.
- Middleware custom : plus de travail, moins teste.

## R3: Envoi d'emails (double opt-in newsletter)

**Decision**: Utiliser `fastapi-mail` (wrapper aiosmtplib) avec `BackgroundTasks` de FastAPI + `itsdangerous` pour la signature de tokens.

**Rationale**: fastapi-mail est async-natif, supporte les templates Jinja2 pour les emails HTML. `itsdangerous.URLSafeTimedSerializer` permet une verification stateless des tokens (pas besoin de stocker le token de confirmation en DB). BackgroundTasks renvoie la reponse immediatement.

**Flow**:
1. Soumission email → generer token signe (expiration 24h) → stocker abonne avec statut "en_attente"
2. Envoyer email de confirmation via BackgroundTasks avec lien `/api/newsletter/confirm?token=xxx`
3. GET `/api/newsletter/confirm?token=xxx` → verifier signature + expiration → statut passe a "actif"

**Alternatives rejetees**:
- aiosmtplib brut : reinventer ce que fastapi-mail fournit deja.
- Celery + Redis : surdimensionne pour des emails de confirmation.
- Services transactionnels (SendGrid, etc.) : a considerer en production pour la delivrabilite, swappable plus tard.

## R4: Logging des visites (non-bloquant)

**Decision**: Middleware HTTP avec `response.background` (BackgroundTask de Starlette) pour inserer en DB apres envoi de la reponse.

**Rationale**: Zero impact sur le temps de reponse. Le middleware capture toutes les requetes uniformement. `response.background` fait partie du design de Starlette. Pour le volume attendu, des inserts individuels suffisent.

**Pattern**:
- Middleware intercepte chaque requete publique
- Apres envoi de la reponse, `BackgroundTask` insere en DB
- Filtrage des bots par User-Agent dans le middleware (avant l'insert)
- Filtrage des routes admin/API-only (ne logger que les pages publiques)

**Alternatives rejetees**:
- Dependency injection (`Depends`) : necessite de decorer chaque endpoint.
- asyncio.Queue + worker batch : optimisation prematuree pour le volume attendu.
- BaseHTTPMiddleware class : problemes de performance connus avec streaming.

## R5: Nouvelles dependances requises

| Package | Version | Usage |
|---------|---------|-------|
| slowapi | >=0.1.9 | Rate limiting par IP |
| fastapi-mail | >=1.4.0 | Envoi emails async (confirmation, desinscription) |
| itsdangerous | >=2.1.0 | Signature/verification de tokens pour opt-in |

## R6: Nouvelles variables de configuration

| Variable | Type | Default | Usage |
|----------|------|---------|-------|
| MAIL_USERNAME | str | "" | Identifiant SMTP |
| MAIL_PASSWORD | str | "" | Mot de passe SMTP |
| MAIL_FROM | str | "noreply@pcqvp.mg" | Adresse expediteur |
| MAIL_SERVER | str | "localhost" | Serveur SMTP |
| MAIL_PORT | int | 587 | Port SMTP |
| FRONTEND_URL | str | "http://localhost:3000" | URL frontend pour les liens dans les emails |
| GLOBALLEAKS_URL | str | "" | URL par defaut de l'instance GlobalLeaks |
