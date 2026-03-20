# Contract: Health Check Endpoint

**Branch**: `003-monorepo-foundations` | **Date**: 2026-03-20

## GET /health

Point de controle sante du backend. Verifie que le service est operationnel et que la base de donnees est accessible.

### Request

- **Method**: GET
- **Path**: `/health`
- **Authentication**: Aucune
- **Query Parameters**: Aucun
- **Body**: Aucun

### Response: Service et DB operationnels

- **Status**: `200 OK`
- **Content-Type**: `application/json`

```json
{
  "status": "ok",
  "db": "connected"
}
```

### Response: Service operationnel, DB inaccessible

- **Status**: `503 Service Unavailable`
- **Content-Type**: `application/json`

```json
{
  "status": "ok",
  "db": "disconnected",
  "detail": "Connection refused"
}
```

### Comportement

1. Le endpoint tente d'executer une requete de test (`SELECT 1`) sur la base de donnees.
2. Si la requete reussit : retourne 200 avec `db: "connected"`.
3. Si la requete echoue (timeout, connexion refusee, etc.) : retourne 503 avec `db: "disconnected"` et le detail de l'erreur.
4. Le champ `status` indique toujours `"ok"` car le service backend lui-meme est operationnel (il repond a la requete).

### Notes

- Ce endpoint est utilise par le frontend (page d'accueil) pour afficher le statut de connexion.
- Pas de rate limiting pour cette feature (dev uniquement).
