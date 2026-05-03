# Phase 1 — Data Model

**Feature**: 019-regions-geojson-admin
**Date**: 2026-05-03

---

## Entité principale : `GeodataVersion`

Persistée en table `geodata_versions`. Hérite de `UUIDBase` (UUID PK + `created_at` auto, cf. `app/models/base.py`).

### Schéma SQLAlchemy

| Colonne                  | Type                          | Nullable | Défaut       | Notes |
|--------------------------|-------------------------------|----------|--------------|-------|
| `id`                     | `UUID`                        | non      | `gen_random_uuid()` (héritage `UUIDBase`) | PK |
| `created_at`             | `timestamp with tz`           | non      | `now()` (héritage `UUIDBase`) | indexable |
| `created_by_user_id`     | `UUID`                        | non      | —            | FK `users.id` ON DELETE RESTRICT |
| `original_filename`      | `varchar(255)`                | non      | —            | nom du fichier source téléversé |
| `original_size_bytes`    | `bigint`                      | non      | —            | taille du fichier reçu |
| `processed_size_bytes`   | `bigint`                      | non      | —            | taille après pipeline |
| `features_count`         | `integer`                     | non      | —            | nb de features finales |
| `region_names`           | `JSONB`                       | non      | `'[]'`       | array de strings (noms canoniques) |
| `geojson_processed`      | `JSONB`                       | non      | —            | `FeatureCollection` traitée |
| `is_active`              | `boolean`                     | non      | `false`      | invariant : au plus une ligne `true` |
| `notes`                  | `text`                        | oui      | `null`       | libre, défini à l'upload, non modifiable après |
| `warnings`               | `JSONB`                       | non      | `'[]'`       | array d'objets `{code, message, details}` |

### Index

| Nom                                | Colonnes / Filtre                             | Type    | Justification |
|------------------------------------|-----------------------------------------------|---------|---------------|
| `pk_geodata_versions`              | `id`                                          | unique (PK) | identification |
| `uq_geodata_version_one_active`    | `is_active` WHERE `is_active IS TRUE`         | partial unique | invariant FR-012 (R6) |
| `ix_geodata_versions_active_lookup`| `is_active` WHERE `is_active IS TRUE`         | btree (1 ligne) | accélère `GET /api/geography/regions/geojson` |
| `ix_geodata_versions_created_at`   | `created_at DESC`                             | btree   | listing paginé + LRU purge |
| `ix_geodata_versions_created_by`   | `created_by_user_id, created_at DESC`         | btree   | filtrage par auteur |

### Contraintes de validation applicatives (Pydantic v2 + service)

- `original_size_bytes <= 50 * 1024 * 1024`
- `processed_size_bytes <= 5 * 1024 * 1024` (marge sur l'objectif < 1 Mo)
- `features_count BETWEEN 1 AND 100` (la fourchette 20-30 est un *warning*, pas un *constraint*)
- `region_names` : tableau de strings, longueur == `features_count`
- `geojson_processed.type == "FeatureCollection"`
- Chaque feature de `geojson_processed.features` a `properties` réduit à `{name, name_official?, region_code, admin_level}`.

### Relations

- `created_by_user_id` → `users.id` (RESTRICT — empêche la suppression d'un user ayant uploadé une version, conformément au pattern de `audit_logs`).
- Aucune relation directe vers `regions` : la résolution région ↔ feature se fait au runtime côté frontend par nom normalisé (FR-026).

### États (lifecycle)

```text
                ┌────────────┐
   upload OK ──▶│  inactive  │◀──── désactivation par activation d'une autre version
                └─────┬──────┘
                      │ activate (admin)
                      ▼
                ┌────────────┐
                │   active   │ ◀── unique à un instant donné
                └─────┬──────┘
                      │ activate(another) → revient à inactive
                      ▼
                ┌────────────┐
   delete OK ──▶│  supprimée │ (uniquement si inactive)
                └────────────┘
```

Transitions :
- `inactive → active` : endpoint `POST /admin/geodata/regions/versions/{id}/activate` (FR-014, FR-015)
- `active → inactive` : effet de bord d'une activation d'une autre version (jamais directement)
- `inactive → supprimée` : endpoint `DELETE /admin/geodata/regions/versions/{id}` (FR-014, FR-016)
- `active → supprimée` : INTERDIT (FR-014, retour `409 Conflict`)
- Auto-purge : `inactive → supprimée` automatique lors de l'insertion d'une nouvelle version dépassant le quota 50 (FR-016, R7)

### Invariants

| Invariant | Garantie |
|-----------|----------|
| INV-1 : au plus une version active | Index partiel unique + transaction `FOR UPDATE` (R6) |
| INV-2 : une version active existe toujours après seed | Migration de seed 010 marque la version initiale `is_active=true` (FR-021) |
| INV-3 : ≤ 50 versions en base | Purge LRU dans la transaction d'insertion (R7) |
| INV-4 : `features_count` cohérent avec `len(region_names)` et `len(geojson_processed.features)` | Calculé une fois à la fin du pipeline ; aucune modification a posteriori |
| INV-5 : `geojson_processed` ne contient que les properties autorisées | Pipeline drop systématique (FR-006, FR-028) |

---

## Entité éphémère : `GeodataJob` (in-memory)

Pour le suivi des uploads asynchrones (R3). **Non persistée en DB** — registre Python en mémoire process.

```python
@dataclass(frozen=True)
class GeodataJob:
    id: UUID                    # job_id retourné par l'upload
    status: Literal["pending", "running", "done", "failed"]
    submitted_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    version_id: UUID | None     # rempli quand status == "done"
    error_message: str | None   # rempli quand status == "failed"
```

Stockage : `dict[UUID, GeodataJob]` protégé par `asyncio.Lock`. TTL 30 min après `completed_at` (purge à la prochaine création).

---

## Réutilisation : `AuditLog`

Aucun nouveau modèle. Trois actions ajoutées (R12) :

| Action                          | `target_type`       | `target_id`     | `payload` (JSONB) |
|---------------------------------|---------------------|-----------------|-------------------|
| `geodata_version.uploaded`      | `geodata_version`   | `version.id`    | `{result, failure_reason?, features_count, processed_size_bytes}` |
| `geodata_version.activated`     | `geodata_version`   | `version.id`    | `{result, previous_active_id?, features_count, processed_size_bytes}` |
| `geodata_version.deleted`       | `geodata_version`   | `version.id`    | `{result, features_count, processed_size_bytes}` |

`actor_user_id` = utilisateur admin courant (FK `users.id`).

---

## Configuration applicative

Ajouts dans `app/core/config.py` :

```python
class Settings(BaseSettings):
    # ... existant ...
    GEODATA_MAX_UPLOAD_BYTES: int = 50 * 1024 * 1024
    GEODATA_MAX_VERSIONS: int = 50
    GEODATA_SIMPLIFY_RATIO: float = 0.04         # Visvalingam-weighted
    GEODATA_MIN_FEATURE_AREA_DEG2: float = 0.001
    GEODATA_FEATURES_MIN_WARN: int = 20
    GEODATA_FEATURES_MAX_WARN: int = 30
    GEODATA_SYNC_TIMEOUT_SECONDS: float = 5.0
    GEODATA_RATE_LIMIT_UPLOADS_PER_HOUR: int = 10
    GEODATA_NAME_ALIASES: dict[str, str] = {
        "matsiatra ambony": "Haute Matsiatra",
    }
    GEODATA_COORDINATE_PRECISION: int = 4
    GEODATA_PUBLIC_CACHE_MAX_AGE: int = 3600
    GEODATA_REGION_CODE_PREFIX: str = "MG-"
```

---

## Codes d'avertissements (warnings)

Format normalisé pour `geodata_versions.warnings` (synthétique, illustratif) :

```json
[
  {"code": "FEATURE_COUNT_OUT_OF_RANGE", "message": "31 features (expected 20-30)", "details": {"count": 31}},
  {"code": "REGION_NOT_IN_DATABASE", "message": "Region 'Vatovavy' has no match in regions table", "details": {"name": "Vatovavy"}},
  {"code": "DUPLICATE_NAME_DROPPED", "message": "Duplicate 'Analanjirofo' — kept feature with largest area", "details": {"name": "Analanjirofo", "kept_area_deg2": 0.45}},
  {"code": "FEATURE_TOO_SMALL_DROPPED", "message": "Feature 'X' dropped after simplification (area < 0.001 deg²)", "details": {"name": "X", "area_deg2": 0.0008}},
  {"code": "GEOMETRY_FIXED", "message": "Self-intersection auto-repaired", "details": {"name": "Y"}}
]
```

---

## Migration Alembic

**`009_create_geodata_versions.py`** :
- `CREATE TABLE geodata_versions` (cf. schéma ci-dessus).
- 5 index (PK + 4 explicites).
- `downgrade` = `DROP TABLE geodata_versions` (réversible).

**`010_seed_geodata_initial.py`** :
- Charge un fichier statique `backend/alembic/seed/madagascar_regions_v1.geojson` (livré dans le repo, ~400 Ko, 23 régions, déjà passé par le pipeline localement).
- Insert avec `is_active=true`, `created_by_user_id` = ID utilisateur seed (cf. `seed_admin.py`).
- `downgrade` = `DELETE FROM geodata_versions WHERE original_filename = 'madagascar_regions_v1.geojson'`.

---

## Diagramme de relations

```text
users.id ─────┐
              │ FK RESTRICT
              ▼
       geodata_versions
              │
              │ (référencée par target_id)
              ▼
        audit_logs (target_type='geodata_version')
              ▲
              │ FK RESTRICT
users.id ─────┘ (actor_user_id)
```

Pas de FK depuis ou vers `regions` / `provinces` / `communes` : la table `regions` est une référence métier indépendante. Le rapprochement geometry ↔ région se fait au runtime par nom normalisé.
