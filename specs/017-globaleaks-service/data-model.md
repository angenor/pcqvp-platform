# Data Model: Service de signalement GlobalLeaks

**Feature**: 017-globaleaks-service | **Date**: 2026-03-30

## Overview

GlobalLeaks est un logiciel pre-construit avec son propre modele de donnees interne (SQLite). Ce document decrit les entites du point de vue de la configuration, pas de l'implementation.

**Aucune modification du modele de donnees PCQVP (PostgreSQL) n'est necessaire.**

## Entites GlobalLeaks (configuration)

### Canal (Channel)

| Attribut         | Description                                       |
|------------------|---------------------------------------------------|
| Nom              | Nom du canal thematique                           |
| Description      | Description du type de signalement attendu         |
| Image            | Icone/image representative du canal               |
| Questionnaire    | Questionnaire associe au canal                     |
| Destinataires    | Liste des destinataires recevant les signalements  |
| Retention        | Indefinie (suppression manuelle)                   |

**Instances prevues** :
1. Fiscalite / Paiements
2. Environnement
3. Social / Communautaire
4. Gouvernance / Corruption

### Questionnaire

| Attribut         | Description                                       |
|------------------|---------------------------------------------------|
| Nom              | Nom du questionnaire                              |
| Etapes           | Liste ordonnee de groupes de questions             |
| Questions        | Type, libelle, aide, obligatoire, format           |

**Champs communs a tous les questionnaires** :
- Type d'irregularite (selection)
- Localisation geographique (texte libre)
- Entites impliquees (texte multiligne)
- Periode concernee (plage de dates)
- Description detaillee (texte multiligne)
- Pieces jointes (fichiers)

### Destinataire (Recipient)

| Attribut         | Description                                       |
|------------------|---------------------------------------------------|
| Nom              | Nom complet                                       |
| Email            | Adresse email pour les notifications              |
| Mot de passe     | Authentification sur GlobalLeaks                  |
| Canaux assignes  | Canaux dont il recoit les signalements            |
| 2FA              | Authentification a deux facteurs (recommande)      |

### Configuration PCQVP existante

L'URL de GlobalLeaks est stockee dans la table de configuration du backend PCQVP existant, accessible via :
- Endpoint public : `GET /api/public/config/globalleaks` → `{ "url": "https://alerte.miningobs.mg" }`
- Endpoint admin : `GET/PUT /api/admin/config/globalleaks_url`

## Relations

```
Canal 1──N Destinataire (un canal a plusieurs destinataires)
Canal 1──1 Questionnaire (un canal utilise un questionnaire)
Signalement N──1 Canal (un signalement appartient a un canal)
Signalement 1──N Piece jointe (un signalement a plusieurs fichiers)
Signalement 1──N Message (communication bidirectionnelle)
```

## Volumes Docker (stockage physique)

| Volume              | Contenu                                                |
|---------------------|--------------------------------------------------------|
| `globaleaks-data`   | DB SQLite, fichiers uploades, cles de chiffrement, config Tor, certificats HTTPS |
| `tor-keys`          | Cles du service Tor hidden (.onion)                    |
