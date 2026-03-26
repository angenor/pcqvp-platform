# API Contract: Auth

**Base path**: `/api/auth`

---

## POST /api/auth/login

Authentifie un utilisateur et retourne un access token. Le refresh token est positionné en cookie httpOnly.

**Auth** : Public

**Request body** :
```json
{
  "email": "admin@example.com",
  "password": "secret123"
}
```

**Response 200** :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```
+ Header `Set-Cookie: refresh_token=eyJ...; HttpOnly; Secure; SameSite=Lax; Path=/api/auth; Max-Age=604800`

**Response 401** :
```json
{
  "detail": "Identifiants incorrects"
}
```

**Response 423** (compte verrouillé) :
```json
{
  "detail": "Compte temporairement verrouillé"
}
```

---

## POST /api/auth/register

Crée un nouveau compte utilisateur. Réservé aux administrateurs.

**Auth** : Bearer token + rôle admin

**Request body** :
```json
{
  "email": "editor@example.com",
  "password": "motdepasse8",
  "role": "editor"
}
```

**Response 201** :
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "editor@example.com",
  "role": "editor",
  "is_active": true,
  "created_at": "2026-03-20T10:30:00Z"
}
```

**Response 400** :
```json
{
  "detail": "Un compte avec cet email existe déjà"
}
```

**Response 403** :
```json
{
  "detail": "Accès réservé aux administrateurs"
}
```

---

## POST /api/auth/refresh

Renouvelle l'access token à partir du refresh token (cookie).

**Auth** : Cookie refresh_token

**Request body** : aucun

**Response 200** :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```
+ Nouveau cookie `refresh_token` (rotation)

**Response 401** :
```json
{
  "detail": "Token de rafraîchissement invalide ou expiré"
}
```

---

## GET /api/auth/me

Retourne le profil de l'utilisateur authentifié.

**Auth** : Bearer token

**Response 200** :
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "admin@example.com",
  "role": "admin",
  "is_active": true,
  "created_at": "2026-03-20T10:30:00Z"
}
```

**Response 401** :
```json
{
  "detail": "Non authentifié"
}
```

---

## Schemas Pydantic partagés

### LoginRequest
- `email`: str (EmailStr)
- `password`: str (min_length=8)

### RegisterRequest
- `email`: str (EmailStr)
- `password`: str (min_length=8)
- `role`: Literal["admin", "editor"] (default: "editor")

### TokenResponse
- `access_token`: str
- `token_type`: str = "bearer"

### UserResponse
- `id`: UUID
- `email`: str
- `role`: str
- `is_active`: bool
- `created_at`: datetime

## Types partagés frontend (packages/shared)

```typescript
export type UserRole = 'admin' | 'editor'

export interface UserProfile {
  id: string
  email: string
  role: UserRole
  is_active: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  password: string
  role?: UserRole
}
```
