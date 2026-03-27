# API Contracts: Comptes administratifs par région

**Date**: 2026-03-27

## Endpoints existants utilisés (aucune modification)

### Admin - Liste des comptes avec filtres

```
GET /api/admin/comptes?collectivite_type=region&collectivite_id={uuid}&annee={year}
Authorization: Bearer {token} (admin|editor)

Response 200:
{
  "items": [
    {
      "id": "uuid",
      "collectivite_type": "region",
      "collectivite_id": "uuid",
      "collectivite_name": "string",
      "annee_exercice": 2024,
      "status": "draft|published",
      "created_by": "uuid",
      "created_at": "datetime",
      "updated_at": "datetime|null"
    }
  ],
  "total": 1
}
```

### Admin - Création de compte

```
POST /api/admin/comptes
Authorization: Bearer {token} (admin|editor)

Body:
{
  "collectivite_type": "region",
  "collectivite_id": "uuid",
  "annee_exercice": 2024
}

Response 201: CompteDetail
Response 404: { "detail": "Collectivite non trouvee" }
Response 409: { "detail": "Un compte existe deja..." }
```

### Public - Années disponibles

```
GET /api/public/collectivites/region/{id}/annees

Response 200:
{
  "annees": [2023, 2024]
}

Response 404: { "detail": "Collectivite non trouvee" }
```

### Public - Détail d'un compte publié

```
GET /api/public/collectivites/region/{id}/comptes?annee={year}

Response 200: PublicCompteResponse
Response 404: { "detail": "Compte non trouve ou non publie" }
```

## Navigation frontend (nouveaux liens)

| Source | Destination | Paramètres |
|--------|-------------|------------|
| Fiche admin région (`/admin/geography/regions/[id]`) | `/admin/accounts?collectivite_type=region&collectivite_id={id}` | Query params |
| Page publique région (`/regions/[id]`) | Page détail compte publié (via API publique) | Année d'exercice |
