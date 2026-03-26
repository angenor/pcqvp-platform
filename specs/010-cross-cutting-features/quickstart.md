# Quickstart: Fonctionnalites transverses

**Date**: 2026-03-21
**Feature**: 010-cross-cutting-features

## Prerequis

- PostgreSQL 16+ avec extensions `unaccent`
- Service SMTP accessible (ou MailHog pour le dev local)
- Backend et frontend existants fonctionnels

## Nouvelles dependances backend

```bash
cd apps/backend
source .venv/bin/activate
pip install slowapi>=0.1.9 fastapi-mail>=1.4.0 itsdangerous>=2.1.0
```

Ajouter dans `pyproject.toml` :
```toml
"slowapi>=0.1.9",
"fastapi-mail>=1.4.0",
"itsdangerous>=2.1.0",
```

## Variables d'environnement (.env)

```env
# Email (newsletter)
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=noreply@pcqvp.mg
MAIL_SERVER=localhost
MAIL_PORT=587
FRONTEND_URL=http://localhost:3000

# GlobalLeaks (valeur par defaut, configurable en admin)
GLOBALLEAKS_URL=
```

## Migration Alembic

```bash
cd apps/backend
alembic revision --autogenerate -m "add newsletter_subscribers visit_logs site_configurations search_vectors"
alembic upgrade head
```

La migration doit inclure :
1. `CREATE EXTENSION IF NOT EXISTS unaccent`
2. Creation de la config `fr_unaccent`
3. Tables `newsletter_subscribers`, `visit_logs`, `site_configurations`
4. Colonnes `search_vector` sur `provinces`, `regions`, `communes`
5. Index GIN sur les `search_vector`
6. Seed de `site_configurations` avec `globalleaks_url`

## Dev local (email)

Pour tester les emails en local, utiliser MailHog :
```bash
# Via Docker
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# Config .env
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USERNAME=
MAIL_PASSWORD=
```

Interface web MailHog : http://localhost:8025

## Ordre d'implementation recommande

1. Migration DB (tables + extensions + search vectors)
2. Recherche full-text (backend endpoint + frontend dropdown)
3. Newsletter (modele + inscription + confirmation + admin)
4. Suivi visites (middleware + dashboard admin)
5. GlobalLeaks (config admin + page publique)

## Verification

```bash
# Backend
cd apps/backend
pytest

# Verification recherche
curl "http://localhost:8000/api/search?q=Antananarivo"

# Verification newsletter
curl -X POST http://localhost:8000/api/newsletter/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'

# Frontend
cd apps/frontend
pnpm dev
# Verifier le champ de recherche dans le header
# Verifier le formulaire newsletter dans le footer
```
