# Phase 1 — Data Model: Correctifs UX back-office (lot 018)

Ce document décrit les évolutions de schéma nécessaires. Aucune modification aux modèles existants autre que documentée ici.

## Nouvelle entité : `CollectivityDocument`

Table PostgreSQL : `collectivity_documents`
Modèle SQLAlchemy : `backend/app/models/collectivity_document.py` (nouveau)

### Champs

| Colonne | Type | Nullable | Défaut | Description |
|---------|------|----------|--------|-------------|
| `id` | UUID | non | `uuid.uuid4()` | Clé primaire (hérité de `UUIDBase`) |
| `province_id` | UUID | oui | null | FK vers `provinces.id`, `ON DELETE CASCADE` |
| `region_id` | UUID | oui | null | FK vers `regions.id`, `ON DELETE CASCADE` |
| `commune_id` | UUID | oui | null | FK vers `communes.id`, `ON DELETE CASCADE` |
| `title` | VARCHAR(255) | non | — | Titre affiché publiquement (saisi par l'admin) |
| `file_path` | VARCHAR(500) | non | — | Chemin relatif du fichier (ex. `/uploads/documents/ab12c3.pdf`) |
| `file_mime` | VARCHAR(127) | non | — | MIME renvoyé par l'upload, validé côté serveur |
| `file_size_bytes` | BIGINT | non | — | Taille en octets (auto-dérivée à l'upload) |
| `position` | INTEGER | non | 0 | Ordre d'affichage au sein du parent (0 = premier) |
| `created_at` | TIMESTAMPTZ | non | `now()` | Hérité de `UUIDBase` |
| `updated_at` | TIMESTAMPTZ | non | `now()` | Mis à jour à chaque `PUT` / remplacement de fichier |

### Contraintes

1. **CHECK `parent_exclusive`** :
   ```sql
   ((province_id IS NOT NULL)::int + (region_id IS NOT NULL)::int + (commune_id IS NOT NULL)::int) = 1
   ```
   Garantit qu'un document a **exactement un** parent parmi les trois.

2. **Index** :
   - `ix_collectivity_documents_province_position (province_id, position) WHERE province_id IS NOT NULL`
   - `ix_collectivity_documents_region_position (region_id, position) WHERE region_id IS NOT NULL`
   - `ix_collectivity_documents_commune_position (commune_id, position) WHERE commune_id IS NOT NULL`

3. **Validation applicative** (Pydantic / service) :
   - `title` : 1–255 caractères, trimé, ne peut être vide après trim.
   - `position` : ≥ 0.
   - `file_mime` ∈ `{application/pdf, application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document, application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet}`.
   - `file_size_bytes` ≤ 20 971 520 (20 Mo).

### Relations

- `province: Mapped[Province | None]` — `selectin`
- `region: Mapped[Region | None]` — `selectin`
- `commune: Mapped[Commune | None]` — `selectin`

### Transitions d'état / cycle de vie

Aucune machine d'états. Cycle simple :

1. **Création** : `POST /api/admin/collectivity-documents` (après upload qui retourne `file_path`, `file_mime`, `file_size_bytes`).
2. **Mise à jour titre seul** : `PUT /api/admin/collectivity-documents/{id}`.
3. **Remplacement de fichier** (FR-009a) : `PUT /api/admin/collectivity-documents/{id}/file` — écrase `file_path`, `file_mime`, `file_size_bytes`, met à jour `updated_at`. L'ancien fichier est supprimé du disque.
4. **Réordonnancement** : `PATCH /api/admin/collectivity-documents/reorder` — accepte `{parent_type, parent_id, ordered_ids: [UUID]}` et réécrit les positions.
5. **Suppression** : `DELETE /api/admin/collectivity-documents/{id}` — supprime la ligne + fichier du disque.
6. **Publication** : aucun champ `status` — visibilité publique dérivée de la collectivité parent (FR-011a).

### Règles de cascade

- Suppression d'une collectivité (`Province` / `Region` / `Commune`) → CASCADE sur `collectivity_documents` (FK `ON DELETE CASCADE`). Les fichiers sur disque ne sont **pas** supprimés automatiquement par la DB ; une tâche applicative dans le endpoint de suppression de la collectivité doit d'abord nettoyer les fichiers. **Hors scope 018** (la suppression de collectivité n'est pas modifiée par ce lot), à documenter comme dette dans la section Complexity Tracking si rencontré.

---

## Évolution d'entité existante : `CompteAdministratif`

Fichier : `backend/app/models/compte_administratif.py` (modification mineure).

### Modifications

**Aucune modification de schéma.** La suppression s'appuie sur les FK cascade existantes :
- `recette_lines` — cascade delete
- `depense_programs` — cascade delete (et leurs `programme_lines`, etc.)
- `change_logs` — cascade delete

### Règle métier ajoutée (FR-006 / FR-006a)

Le endpoint `DELETE /api/admin/comptes/{id}` doit :

1. Charger le compte, vérifier permissions (`admin` uniquement).
2. Si `compte.status == "published"` → répondre **409 Conflict** avec payload :
   ```json
   {
     "error": "compte_published",
     "message": "Ce compte est publié et peut être référencé publiquement. Repassez-le en brouillon avant suppression.",
     "required_action": "set_status_draft"
   }
   ```
3. Sinon, ouvrir une transaction :
   - Capturer un snapshot (id, titre, collectivity_type, collectivity_id, annee_exercice, status) pour l'audit.
   - Insérer une ligne dans `audit_logs` (voir ci-dessous).
   - Supprimer le compte (cascade automatique sur les enfants).
   - Commit.

---

## Nouvelle entité : `AuditLog`

Table PostgreSQL : `audit_logs`
Modèle SQLAlchemy : `backend/app/models/audit_log.py` (nouveau)

### Champs

| Colonne | Type | Nullable | Défaut | Description |
|---------|------|----------|--------|-------------|
| `id` | UUID | non | `uuid.uuid4()` | Clé primaire (`UUIDBase`) |
| `actor_user_id` | UUID | non | — | FK vers `users.id`, `ON DELETE RESTRICT` |
| `action` | VARCHAR(100) | non | — | Identifiant d'action (ex. `compte_administratif.deleted`) |
| `target_type` | VARCHAR(100) | non | — | Type de cible (ex. `compte_administratif`) |
| `target_id` | UUID | non | — | ID de la ressource ciblée (non FK — cible peut ne plus exister) |
| `payload` | JSONB | non | `{}` | Snapshot ou contexte structuré |
| `created_at` | TIMESTAMPTZ | non | `now()` | Hérité de `UUIDBase` |

### Index

- `ix_audit_logs_action_created (action, created_at DESC)`
- `ix_audit_logs_actor_created (actor_user_id, created_at DESC)`

### Règles d'usage dans ce lot

Le service `audit_log.record_compte_deletion(actor, compte)` est le seul point d'insertion utilisé par 018. L'audit des opérations sur documents officiels est **explicitement hors scope** (Q4 = C) ; la table reste néanmoins extensible pour les lots futurs.

---

## Migration Alembic

**Fichier** : `backend/alembic/versions/NNN_018_documents_audit.py` (numéro à attribuer au moment du commit, après `alembic heads`).

**Opérations** (ordre) :

1. `CREATE TABLE audit_logs ...`
2. `CREATE TABLE collectivity_documents ...` avec CHECK constraint et index partiels.
3. Aucun ALTER sur `provinces`, `regions`, `communes`, `comptes_administratifs`.

**Downgrade** :
1. `DROP TABLE collectivity_documents`
2. `DROP TABLE audit_logs`

---

## Impacts sur les schémas Pydantic et types partagés

- `backend/app/schemas/collectivity_document.py` (nouveau) :
  - `CollectivityDocumentCreate` (parent, title, file_path, file_mime, file_size_bytes)
  - `CollectivityDocumentUpdate` (title)
  - `CollectivityDocumentRead` (tous les champs + `download_url` dérivé)
  - `CollectivityDocumentsReorder` (parent_type enum `province|region|commune`, parent_id UUID, ordered_ids list[UUID])
- `backend/app/schemas/compte_administratif.py` (modification) : pas de nouveau champ, mais nouvelle erreur documentée dans les exceptions (`CompteStillPublishedError`).
- `packages/shared/src/collectivity.ts` (nouveau type exporté) :
  ```ts
  export interface CollectivityDocument {
    id: string;
    parent_type: 'province' | 'region' | 'commune';
    parent_id: string;
    title: string;
    file_path: string;
    file_mime: string;
    file_size_bytes: number;
    position: number;
    download_url: string;
    created_at: string;
    updated_at: string;
  }
  ```
  Note : `parent_type` et `parent_id` sont dérivés côté serveur depuis la FK non nulle ; le frontend ne voit pas les trois colonnes FK nullables.
