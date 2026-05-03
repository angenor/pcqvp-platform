# Phase 0 — Research

**Feature**: 019-regions-geojson-admin
**Date**: 2026-05-03

Toutes les zones grises issues de la spec ont été levées par `/speckit.clarify` (5 questions). Cette phase documente uniquement les décisions techniques.

---

## R1. Bibliothèque de simplification géométrique

**Decision** : `shapely>=2.0` (validation, surface, auto-intersection, multi-polygon merge) **+** `simplification>=0.7` (Visvalingam-weighted optimisé en Rust via PyO3).

**Rationale** :
- `simplification` implémente Visvalingam-weighted natif Rust → 5-10× plus rapide que pur Python sur 22 Mo.
- `shapely` est l'outillage géométrique standard de l'écosystème Python ; il fournit `is_valid`, `area`, `simplify` (Douglas-Peucker fallback) et la résolution des auto-intersections via `make_valid`.
- Les deux libs sont déclaratives, sans état global, compatibles avec un service stateless.

**Alternatives considered** :
- `topojson` (Python) : produit du TopoJSON et fait de la simplification topologique. La spec demande du GeoJSON en sortie ; conversion supplémentaire ; lib plus jeune.
- `geopandas` : trop lourd (pulls pandas, fiona, pyproj) pour un seul service de simplification.
- `mapshaper-cli` (Node) : excellent outil mais introduit une dépendance Node côté backend Python — rejeté pour la simplicité opérationnelle.
- `shapely.simplify` (Douglas-Peucker uniquement) seul : qualité visuelle inférieure à Visvalingam-weighted ; spec impose Visvalingam-weighted.

---

## R2. Parsing du fichier 22 Mo (mémoire)

**Decision** : streaming via `ijson>=3.2` pour la première passe (filtrage `admin_level=4`), puis matérialisation en mémoire des seules features retenues (~150-300 Ko).

**Rationale** :
- `json.loads()` sur 22 Mo coûte 150-200 Mo RAM transients. Sur un worker FastAPI partagé, ce pic peut déclencher OOM.
- `ijson` est itératif et ne charge que les tokens en cours ; consommation < 10 Mo pour le streaming.
- Une fois le filtrage appliqué (typiquement 23-30 features sur des milliers), la matérialisation devient triviale et permet l'usage normal de `shapely`.

**Alternatives considered** :
- Charger tout en `json.loads()` : simple mais risque OOM.
- `orjson` : très rapide mais charge tout en RAM aussi → ne résout pas le problème mémoire.

---

## R3. Stratégie synchrone vs asynchrone

**Decision** : exécution synchrone tant que le pipeline complet aboutit en < 5 s (mesuré via `time.perf_counter` côté serveur). Au-delà, FastAPI `BackgroundTasks` + registre in-memory `geodata_jobs.py` (`{job_id: JobState}`) ; endpoint admin de polling (cf. clarification spec).

**Rationale** :
- `BackgroundTasks` est natif FastAPI, sans broker externe ; suffit pour 5-30 s de traitement à faible concurrence (10 uploads/h max via rate-limit).
- Registre in-memory acceptable : (a) un seul worker uvicorn en prod ; (b) volatilité acceptable — si le worker redémarre, le client re-upload ; opération rare.
- Pas de besoin de durabilité de tâche : pipeline idempotent.

**Alternatives considered** :
- Celery / Dramatiq + Redis : robuste mais sur-dimensionné. Coût opérationnel disproportionné.
- Long-polling HTTP : bloque un connecteur ASGI 30 s, mauvaise UX si timeout proxy/CDN.
- SSE / WebSocket : surdimensionnés et déjà tranchés en clarification.

**Implémentation du seuil 5 s** : on lance le pipeline dans `asyncio.wait_for(run_in_executor(...), timeout=5.0)` ; sur `TimeoutError`, la coroutine continue dans le pool et l'endpoint répond `202 Accepted` avec `job_id`.

---

## R4. Stratégie de cache HTTP / ETag

**Decision** : `Cache-Control: public, max-age=3600` + ETag faible `W/"<version_id_uuid>"`. Support `If-None-Match` → `304 Not Modified`.

**Rationale** :
- L'identifiant de version est immuable : utiliser son UUID directement comme ETag évite de hacher le payload (économie CPU sur chaque hit).
- ETag faible (`W/"..."`) signale qu'il s'agit d'une équivalence sémantique, suffisante ici.
- `max-age=3600` aligné avec la fréquence d'activation (rare) ; à l'activation, l'admin sait que la propagation peut prendre jusqu'à 1 h pour navigateurs/CDN.

**Alternatives considered** :
- ETag fort SHA-256 sur le payload : recalcul coûteux à chaque requête sans bénéfice (l'invalidation est déjà couverte par `version_id`).
- `must-revalidate` ou `no-cache` : forcerait les visiteurs à toucher le backend → augmente la charge sans bénéfice.
- Compression gzip/brotli : laissée à la couche reverse-proxy.

---

## R5. Génération du `region_code`

**Decision** : `MG-` + slugify ASCII basé sur Unicode NFD : décomposer, supprimer marques diacritiques, casefold, garder `[a-z0-9]`, séparateur `-`. Exemple : `Haute Matsiatra` → `MG-haute-matsiatra` ; `Atsimo-Andrefana` → `MG-atsimo-andrefana`.

**Rationale** :
- Stable : NFD est déterministe ; le code reste identique tant que le nom canonique ne change pas.
- ASCII pur : compatible avec n'importe quel système (URL, attribut HTML, comparaison stricte).
- Préfixe `MG-` : prépare l'extension multi-pays (clarification spec : générique pour réutilisation future).

**Alternatives considered** :
- ID numérique opaque : plus court mais pas lisible, fragile si l'ordre de traitement change.
- Code ISO 3166-2 (ex. `MG-T`) : couverture incomplète et figée par l'ISO ; ne suit pas les nouvelles régions immédiatement.
- Lib `python-slugify` : ajoute une dépendance pour 10 lignes de code.

---

## R6. Invariant « une seule version active »

**Decision** : index partiel unique au niveau PostgreSQL + transaction avec `SELECT ... FOR UPDATE` lors d'une activation.

```sql
CREATE UNIQUE INDEX uq_geodata_version_one_active
  ON geodata_versions (is_active)
  WHERE is_active IS TRUE;
```

Procédure d'activation :

```text
BEGIN;
SELECT id, is_active FROM geodata_versions
  WHERE id IN (:current_active_id, :target_id)
  FOR UPDATE;
UPDATE geodata_versions SET is_active = false WHERE is_active = true;
UPDATE geodata_versions SET is_active = true  WHERE id = :target_id;
COMMIT;
```

**Rationale** :
- L'index partiel garantit l'invariant côté DB indépendamment du code (défense en profondeur).
- `FOR UPDATE` sérialise les activations concurrentes : la deuxième transaction attend la première et peut détecter l'obsolescence et retourner `409 Conflict`.

**Alternatives considered** :
- Verrou pessimiste applicatif (mutex Python) : insuffisant en multi-worker.
- Verrou optimiste (`updated_at`) : lourd pour un cas où la concurrence est de toute façon rare.

---

## R7. Purge LRU au-delà de 50 versions

**Decision** : exécutée dans la même transaction que l'insertion d'une nouvelle version. Sélection par `created_at ASC` parmi les versions inactives, suppression jusqu'à `count <= 49` avant `INSERT`.

**Rationale** :
- Atomique : aucune fenêtre où l'on aurait > 50 versions.
- Préserve la version active par construction (sélection exclut `is_active = true`).
- Si toutes les inactives sont récentes, on supprime tout de même la plus ancienne (acceptable : pas de garantie de durée de rétention au-delà du quota).

**Alternatives considered** :
- Job cron de purge périodique : laisse temporairement > 50 versions, plus complexe.
- Purge à l'activation plutôt qu'à l'upload : moins prévisible.

---

## R8. Table de correspondance des noms

**Decision** : table en configuration applicative (`config.py`), constante `GEODATA_NAME_ALIASES: dict[str, str]`. Clé = nom source normalisé (NFD + lowercase), valeur = nom canonique.

```python
GEODATA_NAME_ALIASES = {
    "matsiatra ambony": "Haute Matsiatra",
    # ajouter d'autres alias OSM ↔ canonique au besoin
}
```

**Rationale** :
- Clarification spec : table gérée par les admins techniques en config — pas exposée comme entité administrable.
- Dict immuable triviale, testable, versionnable avec le code (revue PR).
- Pas de migration DB pour ajouter un alias.

**Alternatives considered** :
- Table SQL `geodata_name_aliases` : surdimensionné pour usage statique.
- Fichier YAML séparé : ajoute un point de chargement sans bénéfice.

---

## R9. Précision des coordonnées

**Decision** : arrondi à 4 décimales (`round(x, 4)`) après simplification, appliqué directement sur les `coordinates` du GeoJSON sérialisé.

**Rationale** :
- 4 décimales ≈ 11 m à l'équateur — largement suffisant pour rendu de régions à l'échelle d'un pays (pixel < 100 m).
- Réduction de taille additionnelle de 30-50 % par rapport à la précision native (souvent 7+ décimales).
- Conforme aux pratiques de tile-serving (Mapbox, Leaflet).

**Alternatives considered** :
- 5 décimales : ~1.1 m, gain perceptible nul, +10-15 % de taille.
- 3 décimales : ~110 m, peut introduire des artefacts visibles sur les côtes accidentées.

---

## R10. Validation post-simplification

**Decision** : pour chaque feature après simplification :
1. Reconstruction `shapely.geometry.shape(feature.geometry)`.
2. `geom.is_valid` ; sinon `make_valid(geom)`.
3. `geom.area > 0.001` (degrés²) ; sinon feature évincée + warning.
4. `geom.is_simple` ; sinon warning (sans éviction).

**Rationale** :
- Garantit que le rendu navigateur ne reçoit pas de polygones dégénérés (point, ligne).
- 0.001 deg² ≈ 12 km² à l'équateur — seuil prudent (la plus petite région malgache fait > 16 000 km²).

---

## R11. Frontend : remplacement du package figé

**Decision** : `MadagascarMap.vue` charge le GeoJSON via `useApi('/api/geography/regions/geojson')` au `onMounted`, gère `pending` / `error` / `success` localement, et garde l'API amCharts inchangée pour le rendu (injection du GeoJSON dans `am5map.MapPolygonSeries.geoJSON`).

**Rationale** :
- Aucun ajout de dépendance frontend.
- amCharts accepte indifféremment un import statique ou un objet GeoJSON dynamique.
- Le mapping figé `amchartsToRegionName` est supprimé : la lookup se fait sur `properties.name` normalisé (NFD + lowercase) contre la liste `/api/geography/regions`.
- Bundle frontend réduit (amCharts geodata package non chargé sur la home), absorbant la croissance liée aux modals admin.

**Alternatives considered** :
- Fetch côté SSR Nuxt avec `useFetch` : la home est déjà CSR pour les interactions amCharts ; passer en SSR introduirait une hydratation conflictuelle.
- Service worker cache : sur-dimensionné, le navigateur fait déjà du cache ETag.

---

## R12. Audit log : type d'action et payload

**Decision** : on réutilise la table `audit_logs` existante (`AuditLog` dans `app/models/audit_log.py`). Trois `action` codifiés :
- `geodata_version.uploaded`
- `geodata_version.activated`
- `geodata_version.deleted`

`target_type = "geodata_version"`, `target_id = version.id`, `payload` contient les champs définis par la clarification (B) :

```json
{
  "result": "success",
  "failure_reason": null,
  "features_count": 23,
  "processed_size_bytes": 412000
}
```

**Rationale** :
- Aligné avec les conventions actuelles (`record_compte_deletion` dans `services/audit_log.py`).
- Pas de migration : la table existe déjà.
- Statistiques résumées seulement (clarification spec) — pas de snapshot GeoJSON ni diff détaillé.

---

## Synthèse des dépendances ajoutées

```toml
# backend/pyproject.toml — section [project.dependencies]
"shapely>=2.0",
"simplification>=0.7",
"ijson>=3.2",
```

Aucune dépendance frontend ajoutée.
