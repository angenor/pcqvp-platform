# API Contracts: EditorJS Rich Content

## Endpoints modifiés

### PUT /api/admin/provinces/{id}
### PUT /api/admin/regions/{id}
### PUT /api/admin/communes/{id}
### POST /api/admin/provinces
### POST /api/admin/regions
### POST /api/admin/communes

**Changement** : Le champ `description_json` passe de `list[RichContentBlock]` à `EditorJSData`.

**Request body** (extrait) :
```json
{
  "name": "Antananarivo",
  "code": "ANT",
  "description_json": {
    "time": 1691234567890,
    "blocks": [
      {
        "id": "abc123",
        "type": "header",
        "data": { "text": "Présentation", "level": 2 }
      },
      {
        "id": "def456",
        "type": "paragraph",
        "data": { "text": "Description de la province." }
      },
      {
        "id": "ghi789",
        "type": "table",
        "data": {
          "withHeadings": true,
          "content": [
            ["Année", "Population"],
            ["2020", "1 200 000"],
            ["2025", "1 500 000"]
          ]
        }
      }
    ],
    "version": "2.31.0"
  }
}
```

**Response** : Inchangé (retourne l'entité complète avec `description_json`).

---

## Nouveaux endpoints

### POST /api/admin/upload/image

**Description** : Upload d'une image pour l'éditeur EditorJS.

**Auth** : Requiert rôle `admin` ou `editor`.

**Request** :
- Content-Type: `multipart/form-data`
- Champ : `image` (fichier)

**Contraintes** :
- Types MIME acceptés : `image/jpeg`, `image/png`, `image/webp`, `image/gif`
- Taille max : 5 MB

**Response 200** :
```json
{
  "success": 1,
  "file": {
    "url": "/uploads/images/550e8400-e29b-41d4-a716-446655440000.jpg"
  }
}
```

**Response 400** (fichier invalide) :
```json
{
  "success": 0,
  "detail": "Type de fichier non autorisé. Types acceptés : jpeg, png, webp, gif"
}
```

**Response 413** (fichier trop gros) :
```json
{
  "success": 0,
  "detail": "Le fichier dépasse la taille maximale autorisée (5 MB)"
}
```

---

### POST /api/admin/upload/image-by-url

**Description** : Récupère une image depuis une URL externe (utilisé par le plugin EditorJS image en mode "by URL").

**Auth** : Requiert rôle `admin` ou `editor`.

**Request** :
```json
{
  "url": "https://example.com/image.jpg"
}
```

**Response 200** :
```json
{
  "success": 1,
  "file": {
    "url": "/uploads/images/550e8400-e29b-41d4-a716-446655440000.jpg"
  }
}
```

---

## Fichiers statiques

### GET /uploads/images/{filename}

**Description** : Sert les images uploadées.

**Auth** : Public (pas d'authentification requise).

**Response** : Fichier image avec Content-Type approprié.
