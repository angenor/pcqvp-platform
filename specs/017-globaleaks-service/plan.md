# Implementation Plan: Service de signalement GlobalLeaks

**Branch**: `017-globaleaks-service` | **Date**: 2026-03-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/017-globaleaks-service/spec.md`

## Summary

Deployer une instance GlobalLeaks 5.x via Docker sur le serveur existant, accessible sur `alerte.miningobs.mg` (et par IP/port en attendant le DNS). L'instance est independante et partagee entre plusieurs sites. Le deploiement inclut : configuration Docker avec Tor, personnalisation des 4 canaux thematiques (fiscalite, environnement, social, gouvernance), multilinguisme FR/MG, et integration du lien dans la plateforme PCQVP (deja partiellement en place).

## Technical Context

**Language/Version**: N/A (GlobalLeaks est un logiciel pre-construit deploye via Docker). Integration frontend : TypeScript/Vue 3.5 (Nuxt 4)
**Primary Dependencies**: Docker, GlobalLeaks 5.0.89 (image `globaleaks/globaleaks:latest`), Tor (integre dans GlobalLeaks)
**Storage**: Interne a GlobalLeaks (SQLite/volume Docker `globaleaks-data`), PostgreSQL 16 existant (non modifie)
**Testing**: Tests manuels via l'interface web GlobalLeaks + tests fonctionnels du lien frontend
**Target Platform**: Linux server (meme serveur que PCQVP)
**Project Type**: Infrastructure / service compagnon Docker
**Performance Goals**: Disponibilite 99% mensuelle, soumission < 10 min
**Constraints**: Instance independante partagee entre sites, acces Tor actif, acces IP/port temporaire avant DNS
**Scale/Scope**: ~100 signalements/an estime, 4 canaux, 2-5 destinataires

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution non configuree pour ce projet (template vide). Aucun gate a verifier. Proceeding.

## Project Structure

### Documentation (this feature)

```text
specs/017-globaleaks-service/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
# Fichiers nouveaux/modifies
docker-compose.globaleaks.yml    # Docker Compose dedie a GlobalLeaks (independant)
frontend/
└── app/
    └── pages/
        └── signaler.vue         # EXISTANT - mise a jour URL si necessaire
```

**Structure Decision**: GlobalLeaks est un service Docker autonome. Pas de code applicatif a ecrire cote backend/frontend hormis la mise a jour de la configuration de l'URL dans le backend existant. Le `docker-compose.globaleaks.yml` est separe du `docker-compose.yml` principal car l'instance est partagee entre plusieurs projets.

## Complexity Tracking

> Aucune violation de constitution a justifier.
