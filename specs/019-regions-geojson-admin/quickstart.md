# Quickstart — feature 019-regions-geojson-admin

**Cible** : developpeur qui implemente ou teste localement la feature.

---

## 0. Prerequis

- Repo clone, branche `019-regions-geojson-admin` checkee.
- Docker + pnpm + Python 3.12 + venv installes (cf. `CLAUDE.md`).
- PostgreSQL lance : `docker compose up -d`.
- Backend venv pret : `cd backend && source .venv/bin/activate && pip install -e ".[dev]"`.
- Frontend deps installees : `cd frontend && pnpm install`.

---

## 1. Mise a jour du backend pour cette feature

```bash
cd backend
source .venv/bin/activate

# Ajouter les nouvelles deps (puis pin dans pyproject.toml et reinstaller -e .)
pip install "shapely>=2.0" "simplification>=0.7" "ijson>=3.2"

# Appliquer les nouvelles migrations
alembic upgrade head

# Verifier que la version initiale (23 regions) est bien active
psql -h localhost -U pcqvp -d pcqvp_dev -c \
  "SELECT id, original_filename, features_count, is_active FROM geodata_versions;"
# Attendu : 1 ligne, is_active=true, features_count=23,
# original_filename='madagascar_regions_v1.geojson'
```

---

## 2. Lancer la stack

```bash
# Terminal 1 — backend
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — frontend
cd frontend && pnpm dev
```

- Health backend : http://localhost:8000/health
- Frontend : http://localhost:3000
- Carte d'accueil : http://localhost:3000

---

## 3. Smoke tests endpoint public

```bash
# Premier hit — 200 + ETag
curl -i http://localhost:8000/api/geography/regions/geojson | head -20
# Attendu : HTTP/1.1 200 ; ETag: W/"<uuid>" ; Cache-Control: public, max-age=3600

# Deuxieme hit avec If-None-Match — 304
ETAG=$(curl -sI http://localhost:8000/api/geography/regions/geojson \
       | awk -F': ' 'tolower($1)=="etag"{gsub(/\r/,""); print $2}')
curl -i -H "If-None-Match: $ETAG" http://localhost:8000/api/geography/regions/geojson
# Attendu : HTTP/1.1 304 Not Modified, pas de corps

# Verifier la taille (< 1 Mo)
curl -s http://localhost:8000/api/geography/regions/geojson | wc -c
# Attendu : < 1048576
```

---

## 4. Smoke test back-office admin

1. Login : http://localhost:3000/admin/login (admin seed).
2. Aller sur `/admin/geodata/regions`.
3. Verifier qu'une version active est listee (23 regions).
4. Cliquer « Televerser une nouvelle version », drag-drop d'un GeoJSON Overpass.
5. Suivre la progression (synchrone si < 5 s ; sinon polling automatique).
6. Une fois `done`, cliquer « Previsualiser » — la mini-carte doit s'afficher.
7. Cliquer « Activer » → confirmation → la version courante change.
8. Recharger http://localhost:3000 — la carte doit refleter les nouvelles regions.

---

## 5. Tests automatises

```bash
# Backend — pipeline + integration
cd backend && source .venv/bin/activate
pytest tests/unit/test_geodata_pipeline.py -v
pytest tests/integration/test_admin_geodata.py -v
pytest tests/integration/test_public_geojson.py -v

# Frontend — composable + E2E
cd frontend
pnpm test:unit -- useGeodataAdmin
pnpm test:e2e -- geodata-admin
```

---

## 6. Rollback (test manuel)

1. Avoir au moins deux versions historiques.
2. Sur `/admin/geodata/regions`, dans le tableau, cliquer « Activer » sur une version anterieure.
3. Confirmer.
4. Le `version_id` retourne par `GET /api/geography/regions/geojson` doit changer.
5. Le navigateur, sur la home, doit voir la carte se mettre a jour apres expiration du cache (ou rechargement force).

---

## 7. Reinitialiser

```bash
docker compose down -v
docker compose up -d
cd backend && source .venv/bin/activate && alembic upgrade head
```

---

## 8. Pieges connus

- **Memoire** : un upload de 22 Mo sans `ijson` peut faire un pic RAM > 200 Mo. Verifier que le service utilise bien le streaming.
- **Index partiel** : si deux versions sont marquees `is_active=true` simultanement, PostgreSQL doit lever `IntegrityError` sur `uq_geodata_version_one_active` — c'est la garantie INV-1.
- **`MadagascarMap.vue`** : doit fallback gracieusement si l'endpoint repond 503 (carte masquee + message). Tester avec `kill -STOP <uvicorn_pid>` pour simuler.
- **Bundle frontend** : verifier que `@amcharts/amcharts5-geodata/madagascarRegionHigh` n'est plus importe par `MadagascarMap.vue` apres refactor (sinon perte du gain de bundle).
