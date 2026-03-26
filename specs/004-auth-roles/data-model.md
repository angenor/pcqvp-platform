# Data Model: Authentification et gestion des rôles

**Feature**: 004-auth-roles | **Date**: 2026-03-20

## Entités

### User

Représente un utilisateur de la plateforme admin.

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Identifiant unique |
| email | String(255) | UNIQUE, NOT NULL, INDEX | Adresse email (identifiant de connexion) |
| hashed_password | String(255) | NOT NULL | Mot de passe hashé bcrypt |
| role | Enum('admin', 'editor') | NOT NULL, default 'editor' | Rôle de l'utilisateur |
| is_active | Boolean | NOT NULL, default true | Compte actif/désactivé |
| failed_login_attempts | Integer | NOT NULL, default 0 | Compteur tentatives échouées (brute force) |
| locked_until | DateTime(tz) | NULLABLE | Date/heure de fin de verrouillage |
| created_at | DateTime(tz) | NOT NULL, default now() | Date de création |

**Index** : `ix_users_email` sur `email` (unique)

### Enum UserRole

```
admin   - Accès complet (CRUD utilisateurs, toutes sections admin)
editor  - Accès restreint (sections métier futures uniquement)
```

## Relations

Aucune relation pour cette feature. Le modèle User sera référencé par les futures entités (comptes administratifs, données géographiques, etc.) via une clé étrangère sur `user.id`.

## Transitions d'état

### Cycle de vie du compte

```
[Création par admin] → actif (is_active=true)
                     → désactivé (is_active=false) par un admin
                     → réactivé (is_active=true) par un admin
```

### Cycle de verrouillage brute force

```
[Connexion échouée] → failed_login_attempts += 1
                    → Si >= 5 : locked_until = now() + 15min
[Connexion réussie] → failed_login_attempts = 0, locked_until = null
[Temps écoulé]      → locked_until < now() → déverrouillé automatiquement
```

## Règles de validation

- **email** : format email valide, unique en base, insensible à la casse (stocké en minuscules)
- **password** (en entrée, jamais stocké) : minimum 8 caractères
- **role** : valeur parmi l'enum UserRole uniquement
- **Dernier admin** : interdiction de désactiver le dernier compte admin actif

## Migration Alembic

Table : `users`

**Upgrade** : CREATE TABLE users avec tous les champs ci-dessus + index unique sur email
**Downgrade** : DROP TABLE users
