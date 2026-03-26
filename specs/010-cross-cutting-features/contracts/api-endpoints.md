# API Contracts: Fonctionnalites transverses

**Date**: 2026-03-21
**Feature**: 010-cross-cutting-features

## Recherche full-text

### GET /api/search?q={query}&limit={limit}

Recherche globale sur collectivites et comptes publies.

**Rate limit**: 30 req/min par IP

**Query params**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| q | string | required | Terme de recherche (min 2 caracteres) |
| limit | int | 10 | Nombre max de resultats (max 20) |

**Response 200**:
```json
{
  "results": {
    "collectivites": [
      {
        "id": "uuid",
        "name": "Antananarivo",
        "type": "commune",
        "parent_name": "Analamanga",
        "url": "/communes/uuid"
      }
    ],
    "comptes": [
      {
        "id": "uuid",
        "collectivite_name": "Antsirabe",
        "collectivite_type": "commune",
        "annee_exercice": 2024,
        "url": "/collectivite/commune-uuid"
      }
    ]
  },
  "total": 5
}
```

**Response 422**: Query trop courte (< 2 caracteres)
**Response 429**: Rate limit depasse

---

## Newsletter

### POST /api/newsletter/subscribe

Inscription a la newsletter (double opt-in).

**Rate limit**: 5 req/min par IP

**Request body**:
```json
{
  "email": "user@example.com"
}
```

**Response 200**: Inscription enregistree (ou reactif si desinscrit)
```json
{
  "message": "Un email de confirmation a ete envoye."
}
```

**Response 422**: Email invalide
**Response 429**: Rate limit depasse

### GET /api/newsletter/confirm?token={token}

Confirmation du double opt-in. Redirige vers le frontend avec un parametre de statut.

**Response 302**: Redirect vers `{FRONTEND_URL}/newsletter/confirmed`
**Response 400**: Token invalide ou expire

### GET /api/newsletter/unsubscribe?token={token}

Desinscription via le lien dans l'email.

**Response 302**: Redirect vers `{FRONTEND_URL}/newsletter/unsubscribed`
**Response 400**: Token invalide

---

## Newsletter Admin

### GET /api/admin/newsletter/subscribers

Liste paginee des abonnes. Authentification admin requise.

**Query params**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| page | int | 1 | Numero de page |
| per_page | int | 50 | Resultats par page (max 100) |
| status | string | null | Filtrer par statut: actif, desinscrit, en_attente |
| search | string | null | Recherche par email |

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "status": "actif",
      "confirmed_at": "2026-03-21T10:00:00Z",
      "created_at": "2026-03-21T09:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 50
}
```

### GET /api/admin/newsletter/export

Export CSV de tous les abonnes actifs. Authentification admin requise.

**Response 200**: `Content-Type: text/csv`, `Content-Disposition: attachment; filename=abonnes_newsletter_YYYY-MM-DD.csv`

### DELETE /api/admin/newsletter/subscribers/{subscriber_id}

Suppression d'un abonne. Authentification admin requise.

**Response 204**: Supprime avec succes
**Response 404**: Abonne non trouve

---

## Suivi des visites

### POST /api/tracking/visit

Enregistrement d'une visite (appele cote frontend). Alternatif au middleware backend.

**Note**: Le middleware backend enregistre aussi les visites. Cet endpoint est une alternative pour le tracking cote frontend (SPA navigation).

**Request body**:
```json
{
  "path": "/communes/uuid",
  "page_type": "commune",
  "collectivite_type": "commune",
  "collectivite_id": "uuid"
}
```

**Response 204**: Enregistre

### GET /api/admin/analytics/dashboard

Dashboard des statistiques. Authentification admin requise.

**Query params**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| period | string | "30d" | Periode: 7d, 30d, 12m |

**Response 200**:
```json
{
  "period": "30d",
  "visits": {
    "total": 1250,
    "by_page_type": {
      "home": 300,
      "province": 150,
      "region": 200,
      "commune": 400,
      "compte": 200
    },
    "trend": [
      { "date": "2026-03-01", "count": 42 },
      { "date": "2026-03-02", "count": 38 }
    ]
  },
  "downloads": {
    "total": 85,
    "by_format": {
      "xlsx": 60,
      "docx": 25
    },
    "trend": [
      { "date": "2026-03-01", "count": 3 },
      { "date": "2026-03-02", "count": 5 }
    ]
  },
  "data_retention": {
    "oldest_record": "2025-04-01T00:00:00Z",
    "purge_eligible_count": 120,
    "purge_eligible": true
  }
}
```

### DELETE /api/admin/analytics/purge

Purge manuelle des donnees de plus de 12 mois. Authentification admin requise.

**Response 200**:
```json
{
  "purged_count": 120,
  "message": "120 enregistrements de plus de 12 mois ont ete supprimes."
}
```

---

## Configuration du site

### GET /api/admin/config/{key}

Lecture d'une configuration. Authentification admin requise.

**Response 200**:
```json
{
  "key": "globalleaks_url",
  "value": "https://globalleaks.pcqvp.mg"
}
```

### PUT /api/admin/config/{key}

Mise a jour d'une configuration. Authentification admin requise.

**Request body**:
```json
{
  "value": "https://globalleaks.pcqvp.mg"
}
```

**Response 200**:
```json
{
  "key": "globalleaks_url",
  "value": "https://globalleaks.pcqvp.mg",
  "updated_at": "2026-03-21T10:00:00Z"
}
```

### GET /api/public/config/globalleaks

Lecture publique de l'URL GlobalLeaks (pas d'authentification).

**Response 200**:
```json
{
  "url": "https://globalleaks.pcqvp.mg"
}
```
