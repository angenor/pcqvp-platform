# Public API Contracts: 008-public-consultation

## Base URL

`/api/public/collectivites`

Tous les endpoints sont publics (aucune authentification requise).

---

## GET /api/public/collectivites/{type}/{id}/annees

Retourne les annees d'exercice pour lesquelles des comptes publies existent.

**Path params**:
- `type`: string enum(province, region, commune)
- `id`: UUID

**Response 200**:
```json
{
  "annees": [2023, 2022, 2021]
}
```

**Response 404**: Collectivite non trouvee.

---

## GET /api/public/collectivites/{type}/{id}/description

Retourne la description riche de la collectivite.

**Path params**:
- `type`: string enum(province, region, commune)
- `id`: UUID

**Response 200**:
```json
{
  "name": "Andrafiabe",
  "type": "commune",
  "description_json": [
    { "type": "heading", "content": "Presentation" },
    { "type": "paragraph", "content": "La commune d'Andrafiabe..." },
    { "type": "image", "url": "/uploads/andrafiabe.jpg", "alt": "Vue aerienne" }
  ]
}
```

**Response 404**: Collectivite non trouvee.

---

## GET /api/public/collectivites/{type}/{id}/comptes?annee={year}

Retourne les donnees completes d'un compte publie avec tous les calculs.

**Path params**:
- `type`: string enum(province, region, commune)
- `id`: UUID

**Query params**:
- `annee`: int (obligatoire)

**Response 200**:
```json
{
  "compte": {
    "id": "uuid",
    "collectivite_type": "commune",
    "collectivite_id": "uuid",
    "collectivite_name": "Andrafiabe",
    "annee_exercice": 2023,
    "status": "published"
  },
  "recettes": {
    "template_columns": [
      { "code": "budget_primitif", "name": "Budget primitif", "is_computed": false },
      { "code": "previsions_definitives", "name": "Previsions definitives", "is_computed": true }
    ],
    "sections": [
      {
        "section": "fonctionnement",
        "lines": [
          {
            "template_line_id": "uuid",
            "compte_code": "70",
            "intitule": "Ventes de produits...",
            "level": 1,
            "section": "fonctionnement",
            "values": { "budget_primitif": 1000, "budget_additionnel": 200 },
            "computed": { "previsions_definitives": 1200, "reste_a_recouvrer": 800, "taux_execution": 0.33 },
            "children": [
              {
                "compte_code": "701",
                "intitule": "...",
                "level": 2,
                "values": { ... },
                "computed": { ... },
                "children": [ ... ]
              }
            ]
          }
        ]
      },
      {
        "section": "investissement",
        "lines": [ ... ]
      }
    ]
  },
  "depenses": {
    "template_columns": [ ... ],
    "programmes": [
      {
        "id": "uuid",
        "numero": 1,
        "intitule": "Administration et Coordination",
        "sections": [
          {
            "section": "fonctionnement",
            "lines": [ ... ]
          },
          {
            "section": "investissement",
            "lines": [ ... ]
          }
        ]
      }
    ]
  },
  "recapitulatifs": {
    "recettes": {
      "sections": [
        {
          "section": "fonctionnement",
          "categories": [
            { "compte_code": "70", "intitule": "...", "previsions_definitives": 0, "or_admis": 0, "recouvrement": 0, "reste_a_recouvrer": 0 }
          ],
          "total_reelles": { ... },
          "total_ordre": { ... },
          "total_section": { ... }
        }
      ]
    },
    "depenses": {
      "sections": [ ... ],
      "programmes": [ ... ]
    }
  },
  "equilibre": {
    "fonctionnement": {
      "depenses": { "reelles": [...], "total_reelles": 0, "ordre": [...], "total_ordre": 0, "total": 0 },
      "recettes": { "reelles": [...], "total_reelles": 0, "ordre": [...], "total_ordre": 0, "total": 0 },
      "excedent": 0
    },
    "investissement": { ... },
    "resultat_definitif": 0
  }
}
```

**Response 404**: Compte non trouve ou non publie pour cette collectivite/annee.

---

## GET /api/public/collectivites/{type}/{id}/comptes/{annee}/export?format={format}

Telecharge un fichier d'export du compte.

**Path params**:
- `type`: string enum(province, region, commune)
- `id`: UUID
- `annee`: int

**Query params**:
- `format`: string enum(xlsx, docx)

**Response 200**: Fichier binaire avec headers:
- `Content-Type`: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` ou `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- `Content-Disposition`: `attachment; filename="compte_{collectivite}_{annee}.{ext}"`

**Response 404**: Compte non trouve ou non publie.
