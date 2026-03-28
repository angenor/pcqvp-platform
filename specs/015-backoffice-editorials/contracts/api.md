# API Contracts: Section Éditoriaux

**Feature**: 015-backoffice-editorials
**Date**: 2026-03-27

## Public Endpoints (non authentifié)

### GET /api/editorial

Retourne tout le contenu éditorial en une seule réponse.

**Response 200**:
```json
{
  "hero": {
    "title": "Plateforme de Suivi des Revenus Miniers",
    "subtitle": "Collectivités Territoriales de Madagascar",
    "description": "Publiez Ce Que Vous Payez - Madagascar"
  },
  "body": {
    "content_json": { "time": 1234, "blocks": [...], "version": "2.28.0" }
  },
  "footer": {
    "about": {
      "content_json": { "time": 1234, "blocks": [...], "version": "2.28.0" }
    },
    "contact": {
      "email": "contact@pcqvp.mg",
      "phone": "+261 20 22 123 45",
      "address": "Antananarivo, Madagascar"
    },
    "resources": [
      { "id": "uuid", "title": "EITI Madagascar", "url": "https://...", "sort_order": 0 },
      { "id": "uuid", "title": "Signaler un problème", "url": "/signaler", "sort_order": 1 }
    ]
  }
}
```

---

## Admin Endpoints (requiert rôle admin ou editor)

### GET /api/admin/editorial

Retourne tout le contenu éditorial avec métadonnées (updated_at, updated_by).

**Headers**: `Authorization: Bearer <token>`

**Response 200**:
```json
{
  "hero": {
    "title": { "value": "...", "updated_at": "2026-03-27T10:00:00Z" },
    "subtitle": { "value": "...", "updated_at": "2026-03-27T10:00:00Z" },
    "description": { "value": "...", "updated_at": "2026-03-27T10:00:00Z" }
  },
  "body": {
    "content_json": { ... },
    "updated_at": "2026-03-27T10:00:00Z"
  },
  "footer": {
    "about": {
      "content_json": { ... },
      "updated_at": "2026-03-27T10:00:00Z"
    },
    "contact": {
      "id": "uuid",
      "email": "...",
      "phone": "...",
      "address": "...",
      "updated_at": "2026-03-27T10:00:00Z"
    },
    "resources": [
      { "id": "uuid", "title": "...", "url": "...", "sort_order": 0, "updated_at": "..." }
    ]
  }
}
```

**Response 401**: Non authentifié
**Response 403**: Rôle insuffisant

---

### PUT /api/admin/editorial/hero

Met à jour les champs de la hero section.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "title": "Plateforme de Suivi des Revenus Miniers",
  "subtitle": "Collectivités Territoriales de Madagascar",
  "description": "Publiez Ce Que Vous Payez - Madagascar"
}
```

**Validation**:
- `title` : requis, non vide, max 255 caractères
- `subtitle` : optionnel, max 255 caractères
- `description` : optionnel, max 500 caractères

**Response 200**: `{ "message": "Hero section mise à jour" }`
**Response 422**: Erreur de validation

---

### PUT /api/admin/editorial/body

Met à jour le contenu riche du corps de page.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "content_json": {
    "time": 1234567890,
    "blocks": [
      { "type": "header", "data": { "text": "Titre", "level": 2 } },
      { "type": "paragraph", "data": { "text": "Contenu..." } }
    ],
    "version": "2.28.0"
  }
}
```

**Validation**: `content_json` validé par le schéma `EditorJSData` existant.

**Response 200**: `{ "message": "Corps de page mis à jour" }`
**Response 422**: Erreur de validation

---

### PUT /api/admin/editorial/footer/about

Met à jour la section "À propos" du footer (contenu riche).

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "content_json": { "time": 1234, "blocks": [...], "version": "2.28.0" }
}
```

**Response 200**: `{ "message": "Section À propos mise à jour" }`

---

### PUT /api/admin/editorial/footer/contact

Met à jour les informations de contact du footer.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "email": "contact@pcqvp.mg",
  "phone": "+261 20 22 123 45",
  "address": "Antananarivo, Madagascar"
}
```

**Validation**:
- `email` : format email valide si fourni
- `phone` : optionnel, max 50 caractères
- `address` : optionnel, max 500 caractères

**Response 200**: `{ "message": "Contact mis à jour" }`

---

### GET /api/admin/editorial/footer/resources

Liste les liens de la section Ressources, triés par `sort_order`.

**Response 200**:
```json
[
  { "id": "uuid", "title": "EITI Madagascar", "url": "https://...", "sort_order": 0 }
]
```

---

### POST /api/admin/editorial/footer/resources

Ajoute un lien à la section Ressources.

**Request Body**:
```json
{
  "title": "EITI Madagascar",
  "url": "https://eiti.org/madagascar",
  "sort_order": 0
}
```

**Validation**:
- `title` : requis, non vide, max 255 caractères
- `url` : requis, non vide, max 500 caractères
- `sort_order` : requis, entier >= 0

**Response 201**: `{ "id": "uuid", "title": "...", "url": "...", "sort_order": 0 }`

---

### PUT /api/admin/editorial/footer/resources/{id}

Met à jour un lien existant.

**Request Body**: même format que POST

**Response 200**: `{ "id": "uuid", "title": "...", "url": "...", "sort_order": 0 }`
**Response 404**: Lien non trouvé

---

### DELETE /api/admin/editorial/footer/resources/{id}

Supprime un lien.

**Response 204**: Supprimé
**Response 404**: Lien non trouvé

---

### PUT /api/admin/editorial/footer/resources/reorder

Réordonne les liens.

**Request Body**:
```json
{
  "order": ["uuid1", "uuid2", "uuid3"]
}
```

**Response 200**: `{ "message": "Ordre mis à jour" }`
