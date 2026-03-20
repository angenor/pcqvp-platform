<!--
  Sync Impact Report
  ===================
  Version change: N/A -> 1.0.0 (creation initiale)

  Principes ajoutes:
    - I. Donnees Ouvertes & Transparence (nouveau)
    - II. Securite & Confidentialite (nouveau)
    - III. Simplicite & Maintenabilite (nouveau)

  Sections ajoutees:
    - Contraintes Techniques
    - Workflow de Developpement
    - Governance

  Sections supprimees: aucune (creation initiale)

  Templates:
    - .specify/templates/plan-template.md: OK (Constitution Check dynamique)
    - .specify/templates/spec-template.md: OK (aucune reference directe)
    - .specify/templates/tasks-template.md: OK (aucune reference directe)

  Follow-up TODOs: aucun
-->

# PCQVP Platform Constitution

## Core Principles

### I. Donnees Ouvertes & Transparence

- Les donnees financieres des collectivites territoriales DOIVENT etre
  accessibles au public sans restriction d'acces
- Les donnees DOIVENT etre exportables en formats ouverts (Excel, Word,
  CSV) pour repondre aux besoins des acteurs institutionnels
- L'API REST DOIT exposer les donnees de maniere structuree et documentee
- Les comptes administratifs DOIVENT suivre la structure standardisee
  malgache avec hierarchie de comptes a 3 niveaux
- Les formules d'agregation dans les templates comptables DOIVENT etre
  transparentes, verifiables et calculees automatiquement
- La hierarchie geographique (Province, Region, Commune) DOIT etre le
  point d'entree principal pour la consultation des donnees

**Justification** : La raison d'etre de cette plateforme est de renforcer
la transparence financiere et la redevabilite des collectivites
territoriales de Madagascar beneficiaires de ristournes et redevances
minieres. Toute decision de conception DOIT servir cet objectif.

### II. Securite & Confidentialite

- L'authentification DOIT utiliser JWT avec refresh tokens
- Les mots de passe DOIVENT etre hashes avec bcrypt
- Toutes les entrees utilisateur DOIVENT etre validees et sanitisees
  (Pydantic v2 cote backend, validation TypeScript cote frontend)
- Les roles (admin, editeur) DOIVENT etre verifies a chaque requete
  protegee via middleware d'autorisation
- La configuration CORS DOIT etre restrictive en production
- Les donnees sensibles (tokens, credentials, secrets) NE DOIVENT JAMAIS
  etre exposees dans les logs, reponses API ou code source
- Les migrations de base de donnees DOIVENT etre reversibles

**Justification** : Le back office manipule des donnees financieres
officielles. L'integrite et la securite des acces sont essentielles pour
maintenir la confiance des utilisateurs et des institutions partenaires.

### III. Simplicite & Maintenabilite

- Le code DOIT rester simple et lisible ; eviter la sur-ingenierie
- Chaque module (service, composant, routeur) DOIT avoir une
  responsabilite unique et clairement definie
- Les abstractions NE DOIVENT etre creees que lorsqu'un besoin concret
  les justifie (pas d'abstraction prematuree)
- Les tests DOIVENT couvrir les chemins critiques : pytest pour le
  backend, Vitest pour le frontend
- Le linting DOIT etre applique systematiquement : ruff pour Python,
  ESLint pour TypeScript
- Les types partages entre backend et frontend DOIVENT etre centralises
  dans `packages/shared`

**Justification** : Le projet est porte par une ONG avec des ressources
limitees. Le code DOIT etre comprehensible et maintenable par des
developpeurs qui n'ont pas participe a sa creation initiale.

## Contraintes Techniques

**Architecture** : Monorepo avec deux applications et un package partage

| Couche | Stack | Emplacement |
|--------|-------|-------------|
| Backend | FastAPI 0.135+, Python 3.12+, Uvicorn | `apps/backend/` |
| Frontend | Nuxt 4.4+, TypeScript strict | `apps/frontend/` |
| Types partages | TypeScript | `packages/shared/` |
| Base de donnees | PostgreSQL 16+ | — |
| ORM | SQLAlchemy 2.0.48+ async (asyncpg) | — |
| Migrations | Alembic | `apps/backend/alembic/` |
| CSS | Tailwind CSS 4 (config CSS-native) | — |
| Tests backend | pytest | `apps/backend/tests/` |
| Tests frontend | Vitest | `apps/frontend/tests/` |
| Lint Python | ruff | — |
| Lint TypeScript | ESLint | — |

**Structure backend** : `app/main.py`, `app/core/`, `app/models/`,
`app/schemas/`, `app/routers/`, `app/services/`

**Structure frontend (Nuxt 4)** : tout le code applicatif dans `app/`
(`app/pages/`, `app/components/`, `app/composables/`, `app/layouts/`),
dossier `shared/` pour les types partages entre `app/` et `server/`

**Contraintes fonctionnelles** :

- La hierarchie geographique (Province, Region, Commune) est un concept
  central et structurant de toute la plateforme
- Les tableaux de comptes administratifs suivent une structure
  standardisee malgache a 3 niveaux hierarchiques avec formules
  d'agregation automatiques
- L'export Excel/Word DOIT respecter la mise en forme attendue par les
  utilisateurs institutionnels

## Workflow de Developpement

- Les migrations de base de donnees DOIVENT etre gerees via Alembic
  avec des fichiers de migration versionnes et reversibles
- Les changements d'API DOIVENT etre refletes dans les types partages
  (`packages/shared`) pour maintenir la coherence backend/frontend
- Le backend et le frontend DOIVENT pouvoir etre developpes et testes
  independamment l'un de l'autre
- Chaque fonctionnalite DOIT etre developpee sur une branche dediee
- Les commits DOIVENT etre atomiques et decrire clairement le changement
- Le composable `useApi` DOIT etre le point d'entree unique pour tous
  les appels API cote frontend

## Governance

- Cette constitution est le document de reference pour toutes les
  decisions architecturales et de developpement du projet
- Tout amendement DOIT etre documente, justifie et versionne selon
  le versionnement semantique
- Le versionnement suit le format MAJOR.MINOR.PATCH :
  - MAJOR : changement incompatible de principes ou de gouvernance
  - MINOR : ajout de principe ou section, extension significative
  - PATCH : clarifications, corrections de formulation
- Les revues de code DOIVENT verifier la conformite avec cette
  constitution
- En cas de conflit entre rapidite de livraison et principes, les
  principes prevalent

**Version**: 1.0.0 | **Ratified**: 2026-03-20 | **Last Amended**: 2026-03-20
