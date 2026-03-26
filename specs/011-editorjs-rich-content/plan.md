# Implementation Plan: EditorJS Rich Content

**Branch**: `011-editorjs-rich-content` | **Date**: 2026-03-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/011-editorjs-rich-content/spec.md`

## Summary

Remplacer l'éditeur de contenu custom actuel (RichContentEditor) par EditorJS dans les formulaires d'administration des provinces, régions et communes. Ajouter un endpoint d'upload d'images, mettre à jour les schémas Pydantic pour valider le format EditorJS natif, et adapter le renderer public pour les nouveaux types de blocs (paragraphe, titre, image, tableau, listes).

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript strict (frontend)
**Primary Dependencies**: FastAPI 0.135+, SQLAlchemy 2.0.48+ async, asyncpg, Nuxt 4.4+, Tailwind CSS 4, @editorjs/editorjs + plugins
**Storage**: PostgreSQL 16+ (JSONB pour description_json), système de fichiers local (uploads/images/)
**Testing**: pytest + pytest-asyncio + httpx (backend)
**Target Platform**: Web (serveur Linux, navigateurs modernes)
**Project Type**: Web application (monorepo backend + frontend)
**Performance Goals**: Éditeur réactif, upload < 3s pour images < 5MB
**Constraints**: Images max 5 MB, types MIME restreints (jpeg, png, webp, gif)
**Scale/Scope**: Application interne, < 100 utilisateurs admin, ~1000 entités géographiques

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principe | Statut | Conformité |
|----------|--------|------------|
| I. Données Ouvertes & Transparence | PASS | Le contenu riche améliore la présentation des données géographiques publiques |
| II. Sécurité & Confidentialité | PASS | Upload validé (type MIME, taille), endpoint protégé par rôle admin/editor, sanitisation du contenu |
| III. Simplicité & Maintenabilité | PASS | EditorJS est une dépendance standard, composant réutilisable unique, pas de sur-ingénierie |
| Types partagés centralisés | PASS | Types EditorJS ajoutés dans packages/shared |
| useApi point d'entrée unique | PASS | Upload utilise useApi via le composable existant |
| Migrations réversibles | PASS | Pas de migration Alembic nécessaire (JSONB flexible) |

**Post-Phase 1 recheck** : Tous les principes respectés. Pas de violation.

## Project Structure

### Documentation (this feature)

```text
specs/011-editorjs-rich-content/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 - research findings
├── data-model.md        # Phase 1 - data model changes
├── quickstart.md        # Phase 1 - getting started
├── contracts/
│   └── api.md           # Phase 1 - API contracts
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
apps/backend/
├── app/
│   ├── core/
│   │   └── config.py           # + UPLOAD_DIR, MAX_IMAGE_SIZE settings
│   ├── models/
│   │   └── geography.py        # Inchangé (JSONB flexible)
│   ├── schemas/
│   │   └── geography.py        # Nouveaux schémas EditorJS (remplace RichContentBlock)
│   ├── routers/
│   │   ├── admin_geography.py  # Adapté au nouveau format description_json
│   │   └── upload.py           # NOUVEAU - endpoint upload images
│   ├── services/
│   │   └── geography.py        # Adapté au nouveau format
│   └── main.py                 # + montage StaticFiles + routeur upload
├── uploads/
│   └── images/                 # NOUVEAU - stockage fichiers uploadés
├── scripts/
│   └── migrate_description_format.py  # NOUVEAU - migration ancien format
└── tests/
    ├── test_geography.py       # Mis à jour pour format EditorJS
    └── test_upload.py          # NOUVEAU - tests upload

apps/frontend/
├── app/
│   ├── components/
│   │   ├── RichContentEditor.vue   # Réécrit avec EditorJS
│   │   └── RichContentRenderer.vue # Adapté pour blocs EditorJS
│   ├── composables/
│   │   └── useGeography.ts         # Adapté au nouveau format
│   └── pages/admin/geography/
│       ├── provinces/[id].vue      # ClientOnly wrapper
│       ├── regions/[id].vue        # ClientOnly wrapper
│       └── communes/[id].vue       # ClientOnly wrapper

packages/shared/
└── types/
    └── geography.ts                # Types EditorJS (remplace RichContentBlock)
```

**Structure Decision**: Architecture monorepo existante préservée. Ajout d'un routeur `upload.py` dans le backend et réécriture du composant éditeur frontend. Pas de nouvelle couche d'abstraction.

## Complexity Tracking

Aucune violation de la constitution à justifier.
