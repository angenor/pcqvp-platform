# API Contracts: Comptes Administratifs

**Date**: 2026-03-21 | **Branch**: `007-admin-accounts-entry`

Tous les endpoints sont sous le prefixe `/api/admin/comptes`. Auth requise (JWT Bearer).

## Endpoints

### 1. POST /api/admin/comptes

Creer un nouveau compte administratif.

**Auth**: admin, editor
**Request**:
```json
{
  "collectivite_type": "commune",
  "collectivite_id": "uuid",
  "annee_exercice": 2023
}
```
**Response 201**:
```json
{
  "id": "uuid",
  "collectivite_type": "commune",
  "collectivite_id": "uuid",
  "collectivite_name": "Andrafiabe",
  "annee_exercice": 2023,
  "status": "draft",
  "created_by": "uuid",
  "programmes": [
    {"id": "uuid", "numero": 1, "intitule": "Administration et Coordination"},
    {"id": "uuid", "numero": 2, "intitule": "Developpement economique et social"},
    {"id": "uuid", "numero": 3, "intitule": "Sante"}
  ],
  "created_at": "2026-03-21T10:00:00Z",
  "updated_at": null
}
```
**Errors**: 409 (doublon collectivite+annee), 404 (collectivite non trouvee), 422 (validation)

---

### 2. GET /api/admin/comptes

Liste filtree des comptes administratifs.

**Auth**: admin, editor
**Query params** (tous optionnels):
- `collectivite_type`: "province" | "region" | "commune"
- `collectivite_id`: UUID
- `annee`: integer

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "collectivite_type": "commune",
      "collectivite_id": "uuid",
      "collectivite_name": "Andrafiabe",
      "annee_exercice": 2023,
      "status": "draft",
      "created_by": "uuid",
      "created_at": "2026-03-21T10:00:00Z",
      "updated_at": "2026-03-21T12:00:00Z"
    }
  ],
  "total": 1
}
```

---

### 3. GET /api/admin/comptes/{id}

Detail complet d'un compte avec recettes, depenses et recapitulatifs calcules.

**Auth**: admin, editor
**Response 200**:
```json
{
  "id": "uuid",
  "collectivite_type": "commune",
  "collectivite_id": "uuid",
  "collectivite_name": "Andrafiabe",
  "annee_exercice": 2023,
  "status": "draft",
  "created_by": "uuid",
  "programmes": [
    {"id": "uuid", "numero": 1, "intitule": "Administration et Coordination"}
  ],
  "recettes": {
    "lines": [
      {
        "template_line_id": "uuid",
        "compte_code": "7080",
        "intitule": "Impots sur les revenus",
        "level": 3,
        "parent_code": "708",
        "section": "fonctionnement",
        "sort_order": 1,
        "values": {"budget_primitif": 1017922, "budget_additionnel": 0, "modifications": 0, "or_admis": 1017922, "recouvrement": 0},
        "computed": {"previsions_definitives": 1017922, "reste_a_recouvrer": 1017922, "taux_execution": 1.0}
      }
    ],
    "hierarchical_sums": {
      "708": {"budget_primitif": 1017922, "previsions_definitives": 1017922},
      "70": {"budget_primitif": 1017922, "previsions_definitives": 1017922}
    }
  },
  "created_at": "2026-03-21T10:00:00Z",
  "updated_at": "2026-03-21T12:00:00Z"
}
```
**Errors**: 404

---

### 4. PUT /api/admin/comptes/{id}/recettes

Upsert une ligne de recette (auto-save).

**Auth**: admin, editor
**Request**:
```json
{
  "template_line_id": "uuid",
  "values": {
    "budget_primitif": 1017922,
    "budget_additionnel": 0,
    "modifications": 0,
    "or_admis": 1017922,
    "recouvrement": 0
  }
}
```
**Response 200**:
```json
{
  "id": "uuid",
  "template_line_id": "uuid",
  "values": {"budget_primitif": 1017922, "budget_additionnel": 0, "modifications": 0, "or_admis": 1017922, "recouvrement": 0},
  "computed": {"previsions_definitives": 1017922, "reste_a_recouvrer": 1017922, "taux_execution": 1.0}
}
```
**Side effect**: Si le compte est en statut "published", une entree est ajoutee au journal des modifications.
**Errors**: 404 (compte ou template_line non trouve), 422 (validation)

---

### 5. POST /api/admin/comptes/{id}/programmes

Ajouter un programme de depenses.

**Auth**: admin, editor
**Request**:
```json
{
  "intitule": "Nouveau programme"
}
```
**Response 201**:
```json
{
  "id": "uuid",
  "numero": 4,
  "intitule": "Nouveau programme",
  "created_at": "2026-03-21T10:00:00Z"
}
```
**Errors**: 404 (compte non trouve)

---

### 6. PUT /api/admin/comptes/{id}/programmes/{prog_id}

Modifier l'intitule d'un programme.

**Auth**: admin, editor
**Request**:
```json
{
  "intitule": "Intitule modifie"
}
```
**Response 200**:
```json
{
  "id": "uuid",
  "numero": 1,
  "intitule": "Intitule modifie",
  "updated_at": "2026-03-21T12:00:00Z"
}
```
**Errors**: 404

---

### 7. DELETE /api/admin/comptes/{id}/programmes/{prog_id}

Supprimer un programme et toutes ses lignes de depenses.

**Auth**: admin, editor
**Response**: 204 No Content
**Side effect**: Si publie, entree journal avec detail du programme supprime.
**Errors**: 404

---

### 8. PUT /api/admin/comptes/{id}/programmes/{prog_id}/depenses

Upsert une ligne de depense (auto-save).

**Auth**: admin, editor
**Request**:
```json
{
  "template_line_id": "uuid",
  "values": {
    "budget_primitif": 5000000,
    "budget_additionnel": 0,
    "modifications": 0,
    "engagement": 5000000,
    "mandat_admis": 4500000,
    "paiement": 4500000
  }
}
```
**Response 200**:
```json
{
  "id": "uuid",
  "template_line_id": "uuid",
  "values": {"budget_primitif": 5000000, "budget_additionnel": 0, "modifications": 0, "engagement": 5000000, "mandat_admis": 4500000, "paiement": 4500000},
  "computed": {"previsions_definitives": 5000000, "reste_a_payer": 0, "taux_execution": 0.9}
}
```
**Side effect**: Journal si publie.
**Errors**: 404, 422

---

### 9. PUT /api/admin/comptes/{id}/status

Publier ou depublier un compte.

**Auth**: admin uniquement
**Request**:
```json
{
  "status": "published"
}
```
**Response 200**:
```json
{
  "id": "uuid",
  "status": "published",
  "updated_at": "2026-03-21T14:00:00Z"
}
```
**Errors**: 403 (role editor tente de publier), 404, 422

---

### 10. GET /api/admin/comptes/{id}/recapitulatifs/recettes

Recapitulatif des recettes par categorie Niv1.

**Auth**: admin, editor
**Response 200**:
```json
{
  "sections": [
    {
      "section": "fonctionnement",
      "categories": [
        {
          "compte_code": "70",
          "intitule": "Impots sur les revenus",
          "previsions_definitives": 1017922,
          "or_admis": 1017922,
          "recouvrement": 0,
          "reste_a_recouvrer": 1017922
        }
      ],
      "total_reelles": {"previsions_definitives": 50000000, "or_admis": 48000000, "recouvrement": 45000000, "reste_a_recouvrer": 3000000},
      "total_ordre": {"previsions_definitives": 2000000, "or_admis": 2000000, "recouvrement": 2000000, "reste_a_recouvrer": 0},
      "total_section": {"previsions_definitives": 52000000, "or_admis": 50000000, "recouvrement": 47000000, "reste_a_recouvrer": 3000000}
    }
  ]
}
```

---

### 11. GET /api/admin/comptes/{id}/recapitulatifs/depenses

Recapitulatif des depenses croise comptes x programmes.

**Auth**: admin, editor
**Response 200**:
```json
{
  "sections": [
    {
      "section": "fonctionnement",
      "categories": [
        {
          "compte_code": "60",
          "intitule": "Charges du personnel",
          "programmes": [
            {"programme_id": "uuid", "numero": 1, "mandat_admis": 15000000, "paiement": 15000000, "reste_a_payer": 0},
            {"programme_id": "uuid", "numero": 2, "mandat_admis": 8000000, "paiement": 8000000, "reste_a_payer": 0},
            {"programme_id": "uuid", "numero": 3, "mandat_admis": 3420000, "paiement": 3420000, "reste_a_payer": 0}
          ],
          "total": {"mandat_admis": 26420000, "paiement": 26420000, "reste_a_payer": 0}
        }
      ],
      "total_section": {"mandat_admis": 41849200, "paiement": 41849200, "reste_a_payer": 0}
    }
  ],
  "programmes": [
    {"id": "uuid", "numero": 1, "intitule": "Administration et Coordination"},
    {"id": "uuid", "numero": 2, "intitule": "Developpement economique et social"},
    {"id": "uuid", "numero": 3, "intitule": "Sante"}
  ]
}
```

---

### 12. GET /api/admin/comptes/{id}/recapitulatifs/equilibre

Tableau d'equilibre depenses vs recettes.

**Auth**: admin, editor
**Response 200**:
```json
{
  "fonctionnement": {
    "depenses": {
      "reelles": [
        {"compte_code": "60", "intitule": "Charges du personnel", "montant": 26420000}
      ],
      "total_reelles": 40849200,
      "ordre": [],
      "total_ordre": 0,
      "total": 41849200
    },
    "recettes": {
      "reelles": [
        {"compte_code": "70", "intitule": "Impots sur les revenus", "montant": 1017922}
      ],
      "total_reelles": 49988701,
      "ordre": [
        {"compte_code": "110", "intitule": "Report excedent", "montant": 2000000}
      ],
      "total_ordre": 2000000,
      "total": 51988701
    },
    "excedent": 10139501
  },
  "investissement": {
    "depenses": {"reelles": [], "total_reelles": 2220000, "ordre": [], "total_ordre": 0, "total": 2220000},
    "recettes": {"reelles": [], "total_reelles": 0, "ordre": [], "total_ordre": 2200000, "total": 2200000},
    "excedent": -20000
  },
  "resultat_definitif": 7939501
}
```

---

### 13. GET /api/admin/comptes/{id}/changelog

Journal des modifications d'un compte publie.

**Auth**: admin, editor
**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "user_email": "admin@pcqvp.mg",
      "change_type": "recette_update",
      "detail": {"template_line_id": "uuid", "compte_code": "7080", "column": "budget_primitif", "old_value": 0, "new_value": 1017922},
      "created_at": "2026-03-21T14:30:00Z"
    }
  ],
  "total": 1
}
```
