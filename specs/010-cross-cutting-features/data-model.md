# Data Model: Fonctionnalites transverses

**Date**: 2026-03-21
**Feature**: 010-cross-cutting-features

## Nouvelles tables

### newsletter_subscribers

Abonnes a la newsletter avec cycle de vie : inscription → en_attente → actif → desinscrit → reactif.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Identifiant unique |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Adresse email de l'abonne |
| status | VARCHAR(20) | NOT NULL, default "en_attente" | Enum: en_attente, actif, desinscrit |
| unsubscribe_token | VARCHAR(255) | UNIQUE, NOT NULL | Token unique pour lien de desinscription |
| confirmed_at | TIMESTAMP | NULL | Date de confirmation du double opt-in |
| unsubscribed_at | TIMESTAMP | NULL | Date de desinscription |
| created_at | TIMESTAMP | NOT NULL, server_default now() | Date d'inscription (herite de TimestampMixin) |

**Contraintes**:
- UNIQUE sur `email` (une seule inscription par adresse, reactif si desinscrit)
- Index sur `status` pour filtrage admin
- `unsubscribe_token` genere a chaque activation (change a la reactivation)

**Transitions d'etat**:
```
inscription → en_attente (email soumis, en attente de confirmation)
en_attente → actif (confirmation via lien email, confirmed_at = now())
actif → desinscrit (clic lien desinscription, unsubscribed_at = now())
desinscrit → en_attente (reinscription avec meme email, nouveau opt-in)
```

### visit_logs

Evenements de visite et telechargement. Retention 12 mois, purge manuelle par admin.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Identifiant unique |
| event_type | VARCHAR(20) | NOT NULL | Enum: page_view, download |
| path | VARCHAR(500) | NOT NULL | Chemin de la page visitee ou ressource telechargee |
| page_type | VARCHAR(50) | NULL | Type de page: province, region, commune, compte, home |
| collectivite_type | VARCHAR(20) | NULL | Type de collectivite associee (si applicable) |
| collectivite_id | UUID | NULL | ID de la collectivite associee (si applicable) |
| download_format | VARCHAR(10) | NULL | Format de telechargement: xlsx, docx (si event_type=download) |
| user_agent | VARCHAR(500) | NULL | User-Agent du navigateur |
| ip_address | VARCHAR(45) | NULL | Adresse IP (IPv4 ou IPv6) |
| created_at | TIMESTAMP | NOT NULL, server_default now() | Horodatage de l'evenement |

**Contraintes**:
- Index sur `created_at` (filtrage par periode + purge)
- Index sur `event_type` (filtrage visites vs telechargements)
- Index sur `page_type` (aggregation par type de page)
- Pas de FK vers collectivites (logging decouple, la collectivite peut etre supprimee)

### site_configurations

Parametres configurables du site (cle-valeur).

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Identifiant unique |
| key | VARCHAR(100) | UNIQUE, NOT NULL | Cle de configuration |
| value | TEXT | NOT NULL, default "" | Valeur de la configuration |
| updated_at | TIMESTAMP | NULL | Date de derniere modification |
| created_at | TIMESTAMP | NOT NULL, server_default now() | Date de creation |

**Configurations initiales (seed)**:
- `globalleaks_url` : URL de l'instance GlobalLeaks

## Modifications sur tables existantes

### provinces, regions, communes

Ajout d'une colonne `search_vector` generee pour la recherche full-text.

| Colonne | Type | Description |
|---------|------|-------------|
| search_vector | TSVECTOR | Genere depuis `to_tsvector('fr_unaccent', coalesce(name, ''))`, INDEX GIN |

**Note**: Colonne `Computed` (stored/persisted) dans SQLAlchemy, mise a jour automatiquement par PostgreSQL.

### comptes_administratifs

Pas de modification structurelle. La recherche sur les comptes se fait via jointure avec la table de la collectivite associee (nom commune) + cast de `annee_exercice`.

## Extensions PostgreSQL requises

- `unaccent` : suppression des accents pour la recherche full-text
- Configuration de recherche `fr_unaccent` : copie de `french` avec dictionnaire `unaccent` + `french_stem`

## Relations

```
newsletter_subscribers : standalone, pas de FK vers d'autres tables
visit_logs : standalone, pas de FK (logging decouple)
site_configurations : standalone, cle-valeur
provinces.search_vector : genere depuis provinces.name
regions.search_vector : genere depuis regions.name
communes.search_vector : genere depuis communes.name
```
