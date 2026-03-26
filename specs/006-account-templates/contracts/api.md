# API Contracts: 006-account-templates

**Date**: 2026-03-20 | **Base path**: `/api/admin/templates`

All endpoints require authentication with role `admin` or `editor`.

---

## GET /api/admin/templates

Liste tous les templates.

**Response** `200 OK`:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Recettes",
      "type": "recette",
      "version": 1,
      "is_active": true,
      "lines_count": 168,
      "columns_count": 8,
      "created_at": "2026-03-20T10:00:00Z"
    }
  ],
  "total": 2
}
```

---

## GET /api/admin/templates/{id}

Detail d'un template avec ses lignes et colonnes.

**Path params**: `id` (UUID)

**Response** `200 OK`:
```json
{
  "id": "uuid",
  "name": "Recettes",
  "type": "recette",
  "version": 1,
  "is_active": true,
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": null,
  "lines": [
    {
      "id": "uuid",
      "compte_code": "70",
      "intitule": "IMPOTS SUR LES REVENUS, BENEFICES ET GAINS",
      "level": 1,
      "parent_code": null,
      "section": "fonctionnement",
      "sort_order": 1
    },
    {
      "id": "uuid",
      "compte_code": "708",
      "intitule": "Autres impots sur les revenus",
      "level": 2,
      "parent_code": "70",
      "section": "fonctionnement",
      "sort_order": 2
    }
  ],
  "columns": [
    {
      "id": "uuid",
      "name": "Budget primitif",
      "code": "budget_primitif",
      "data_type": "number",
      "is_computed": false,
      "formula": null,
      "sort_order": 1
    },
    {
      "id": "uuid",
      "name": "Previsions definitives",
      "code": "previsions_definitives",
      "data_type": "number",
      "is_computed": true,
      "formula": "budget_primitif + budget_additionnel + modifications",
      "sort_order": 4
    }
  ]
}
```

**Response** `404 Not Found`: `{"detail": "Template non trouve"}`

---

## PUT /api/admin/templates/{id}/lines

Modifier les lignes d'un template (bulk update).

**Path params**: `id` (UUID)

**Request body**:
```json
[
  {
    "id": "uuid",
    "compte_code": "70",
    "intitule": "IMPOTS SUR LES REVENUS, BENEFICES ET GAINS",
    "level": 1,
    "parent_code": null,
    "section": "fonctionnement",
    "sort_order": 1
  }
]
```

**Response** `200 OK`: Liste mise a jour des lignes

**Response** `404 Not Found`: `{"detail": "Template non trouve"}`
**Response** `422 Unprocessable Entity`: `{"detail": "Code 7080 duplique"}`

---

## PUT /api/admin/templates/{id}/columns

Modifier les colonnes d'un template (bulk update).

**Path params**: `id` (UUID)

**Request body**:
```json
[
  {
    "id": "uuid",
    "name": "Budget primitif",
    "code": "budget_primitif",
    "data_type": "number",
    "is_computed": false,
    "formula": null,
    "sort_order": 1
  }
]
```

**Response** `200 OK`: Liste mise a jour des colonnes

**Response** `404 Not Found`: `{"detail": "Template non trouve"}`
**Response** `422 Unprocessable Entity`: `{"detail": "Code budget_primitif duplique"}`

---

## POST /api/admin/templates/{id}/lines

Ajouter une nouvelle ligne a un template.

**Path params**: `id` (UUID)

**Request body**:
```json
{
  "compte_code": "7081",
  "intitule": "Nouveau compte",
  "level": 3,
  "parent_code": "708",
  "section": "fonctionnement",
  "sort_order": 5
}
```

**Response** `201 Created`: La ligne creee

**Response** `404 Not Found`: `{"detail": "Template non trouve"}`
**Response** `409 Conflict`: `{"detail": "Code 7081 existe deja dans ce template"}`
**Response** `422 Unprocessable Entity`: `{"detail": "Parent 708 non trouve dans le template"}`

---

## DELETE /api/admin/templates/{id}/lines/{line_id}

Supprimer une ligne d'un template.

**Path params**: `id` (UUID), `line_id` (UUID)

**Response** `204 No Content`

**Response** `404 Not Found`: `{"detail": "Ligne non trouvee"}`
**Response** `409 Conflict`: `{"detail": "Impossible de supprimer : cette ligne a des enfants"}`
