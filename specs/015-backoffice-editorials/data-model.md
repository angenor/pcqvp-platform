# Data Model: Section Éditoriaux du Backoffice

**Feature**: 015-backoffice-editorials
**Date**: 2026-03-27

## Entities

### EditorialContent

Stocke les blocs de contenu éditorial identifiés par une clé de section unique.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Identifiant unique |
| section_key | String(50) | UNIQUE, NOT NULL | Clé de section (hero_title, hero_subtitle, hero_description, body_content, footer_about) |
| content_text | Text | NULLABLE | Contenu texte simple (hero_title, hero_subtitle, hero_description) |
| content_json | JSONB | NULLABLE | Contenu riche EditorJS (body_content, footer_about) |
| updated_by | UUID | FK → users.id, NULLABLE | Dernier utilisateur ayant modifié |
| created_at | DateTime(tz) | NOT NULL, server_default=now() | Date de création |
| updated_at | DateTime(tz) | NULLABLE, onupdate=now() | Date de dernière modification |

**Section keys prédéfinies** :
- `hero_title` : Titre principal de la hero section (content_text)
- `hero_subtitle` : Sous-titre de la hero section (content_text)
- `hero_description` : Description de la hero section (content_text)
- `body_content` : Contenu riche du corps de page (content_json)
- `footer_about` : Section "À propos" du footer en contenu riche (content_json)

**Indexes** : `section_key` (unique)

---

### ContactInfo

Stocke les informations de contact structurées pour le footer. Table singleton (un seul enregistrement).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Identifiant unique |
| email | String(255) | NULLABLE | Adresse email de contact |
| phone | String(50) | NULLABLE | Numéro de téléphone |
| address | Text | NULLABLE | Adresse postale |
| updated_by | UUID | FK → users.id, NULLABLE | Dernier utilisateur ayant modifié |
| created_at | DateTime(tz) | NOT NULL, server_default=now() | Date de création |
| updated_at | DateTime(tz) | NULLABLE, onupdate=now() | Date de dernière modification |

---

### ResourceLink

Stocke les liens de la section "Ressources" du footer. Liste ordonnée.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Identifiant unique |
| title | String(255) | NOT NULL | Titre du lien |
| url | String(500) | NOT NULL | URL de destination |
| sort_order | Integer | NOT NULL, default=0 | Ordre d'affichage |
| created_at | DateTime(tz) | NOT NULL, server_default=now() | Date de création |
| updated_at | DateTime(tz) | NULLABLE, onupdate=now() | Date de dernière modification |

**Indexes** : `sort_order` (pour le tri)

---

## Relationships

```
User (existing)
  └── updated_by ←── EditorialContent.updated_by (optional FK)
  └── updated_by ←── ContactInfo.updated_by (optional FK)

EditorialContent (standalone, keyed by section_key)
ContactInfo (singleton)
ResourceLink (ordered list)
```

## Validation Rules

- `EditorialContent.section_key` : doit être une valeur parmi l'ensemble prédéfini
- `EditorialContent.content_text` : obligatoire pour les sections hero_title (non vide)
- `EditorialContent.content_json` : doit être un objet EditorJS valide (validé par le schéma `EditorJSData` existant)
- `ContactInfo.email` : format email valide si fourni
- `ResourceLink.title` : non vide, max 255 caractères
- `ResourceLink.url` : non vide, max 500 caractères

## Default Values (seed)

Quand aucun contenu n'existe, le frontend affiche des valeurs par défaut hardcodées :
- Hero title : "Plateforme de Suivi des Revenus Miniers"
- Hero subtitle : "Collectivités Territoriales de Madagascar"
- Hero description : "Publiez Ce Que Vous Payez - Madagascar"
- Body content : vide (section masquée)
- Footer about/contact/resources : valeurs actuelles du layout default.vue
