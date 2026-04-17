# Implementation Plan: Correctifs UX back-office (lot 018)

**Branch**: `018-backoffice-ux-fixes` | **Date**: 2026-04-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/018-backoffice-ux-fixes/spec.md`

## Summary

Lot de quatre correctifs UX dans le back-office PCQVP :

1. **P1 — Bug éditeur éditorial** : rétablir l'insertion d'images dans le corps des pages éditoriales (endpoint `/api/admin/upload/image` et config `@editorjs/image` déjà en place, diagnostic à mener sur la propagation d'authentification ou le MIME).
2. **P2 — Suppression de compte administratif** : ajouter l'endpoint `DELETE /api/admin/comptes/{id}` (absent aujourd'hui) + action UI dans la liste `admin/accounts/index.vue`, avec blocage si le compte est publié (interprétation pratique de FR-006a) et journal d'audit.
3. **P2 — Documents officiels des collectivités** : nouvelle table `collectivity_documents` (FK exclusive vers province/region/commune), endpoint d'upload étendu pour PDF/DOC/DOCX/XLS/XLSX ≤ 20 Mo, bloc UI réutilisable dans les 3 pages d'édition juste après la bannière, affichage public avec titre + icône type + taille + date de mise à jour.
4. **P3 — Raccourcis commune** : ajouter deux liens par ligne (« Voir les comptes » → `/admin/accounts?collectivite_type=commune&collectivite_id={id}` ; « Soumettre un compte » → `/admin/accounts/new?collectivite_type=commune&collectivite_id={id}`). Le back et le front supportent déjà les query params, c'est du câblage UI.

Approche : migration Alembic unique, extension minimale du routeur upload, nouveau routeur `admin_collectivity_documents`, extensions de `admin_comptes`, composant `CollectivityDocumentsEditor.vue` réutilisé dans les trois pages d'édition géographique.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI 0.135+, SQLAlchemy 2.0 async, asyncpg, Pydantic v2, Alembic ; Nuxt 4.4+, Vue 3.5+, Tailwind CSS 4, `@editorjs/editorjs` + `@editorjs/image`, `@fortawesome/vue-fontawesome`
**Storage**: PostgreSQL 16 via asyncpg ; fichiers téléversés sur disque sous `backend/uploads/` (servis par le backend sous `/uploads/...`)
**Testing**: pytest + pytest-asyncio + httpx (backend, DB dédiée `pcqvp_test`). Côté frontend, pas de framework de test en place — vérification manuelle + scénarios d'acceptation.
**Target Platform**: serveur Linux (backend), navigateurs modernes (frontend) avec mode sombre/clair obligatoire
**Project Type**: application web monorepo (backend FastAPI + frontend Nuxt + types partagés)
**Performance Goals**: p95 < 500 ms sur les endpoints back-office ; upload d'un document 20 Mo < 5 s en conditions normales ; affichage d'une page publique de collectivité < 1 s en SSR
**Constraints**: mode sombre/clair sur tous les écrans back-office et public, UI en français, conformité aux rôles `admin` / `editor` existants, ruff clean (target py312, line-length 88, rules E/F/I/UP/W)
**Scale/Scope**: 6 provinces, 22 régions, ~1 579 communes (Madagascar) ; volumétrie estimée < 5 documents officiels par collectivité en moyenne, maximum 50 ; comptes administratifs à la dizaine de milliers à terme

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

La constitution du projet (`.specify/memory/constitution.md`) contient uniquement les placeholders du template générique, sans principes ratifiés. **Aucun gate bloquant n'est donc enforçable.** Le plan respecte néanmoins les règles usuelles documentées dans `CLAUDE.md` :

- Réutilisation des patterns existants (`UUIDBase`, relations `selectin`, `ondelete=RESTRICT` sur FK hiérarchiques) → ✅
- Composable `useApi` comme unique point d'entrée côté frontend → ✅
- Classes Tailwind `dark:` sur toutes les nouvelles interfaces → ✅
- Tests pytest pour tout nouvel endpoint backend → ✅
- Pas de secrets hardcodés, validation au boundary (Pydantic) → ✅

**Re-check post-Phase 1** : OK, aucun nouvel écart introduit (voir section Complexity Tracking, vide).

## Project Structure

### Documentation (this feature)

```text
specs/018-backoffice-ux-fixes/
├── plan.md              # Ce fichier
├── spec.md              # Spécification (déjà rédigée, clarifiée Q1-Q5)
├── research.md          # Phase 0 : diagnostic bug éditeur + choix schéma documents + stratégie de blocage delete
├── data-model.md        # Phase 1 : CollectivityDocument + évolutions CompteAdministratif
├── contracts/           # Phase 1 : contrats API
│   ├── admin-collectivity-documents.yaml
│   ├── admin-comptes-delete.yaml
│   └── admin-upload-document.yaml
├── quickstart.md        # Phase 1 : checklist de validation manuelle en environnement de dev
├── checklists/
│   └── requirements.md  # Déjà créée par /speckit.specify
└── tasks.md             # Généré par /speckit.tasks (hors scope /speckit.plan)
```

### Source Code (repository root)

Structure de projet déjà en place (web app, monorepo). Les modifications concernent les chemins suivants :

```text
backend/
├── alembic/versions/
│   └── 009_add_collectivity_documents.py    # Nouvelle migration (numéro à confirmer au moment du commit)
├── app/
│   ├── models/
│   │   └── collectivity_document.py         # Nouveau : CollectivityDocument (FK exclusive prov/reg/com)
│   ├── schemas/
│   │   └── collectivity_document.py         # Nouveau : Create / Read / Reorder
│   ├── routers/
│   │   ├── admin_collectivity_documents.py  # Nouveau : CRUD + reorder
│   │   ├── admin_comptes.py                 # MODIFIÉ : ajout DELETE /{id} avec blocage + audit
│   │   ├── public_geography.py              # MODIFIÉ : expose les documents dans le payload public
│   │   └── upload.py                        # MODIFIÉ : POST /api/admin/upload/document (PDF/DOC/XLS)
│   ├── services/
│   │   └── audit_log.py                     # Nouveau si absent : journalisation suppression compte
│   └── main.py                              # MODIFIÉ : monter le nouveau routeur
└── tests/
    ├── test_collectivity_documents.py        # Nouveau : CRUD, ordre, validation fichier
    ├── test_admin_comptes_delete.py          # Nouveau : DELETE + blocage si publié + audit
    ├── test_upload_document.py               # Nouveau : validations PDF/DOC/XLS + taille
    └── test_editor_image_upload.py           # Nouveau : non-régression upload image pour EditorJS

frontend/
└── app/
    ├── components/
    │   ├── CollectivityDocumentsEditor.vue  # Nouveau : éditeur réutilisable (upload, réordo, remplacer, supprimer)
    │   ├── CollectivityDocumentsList.vue    # Nouveau : rendu public (titre + icône + taille + date)
    │   ├── RichContentEditor.vue            # MODIFIÉ : fix config image si nécessaire (voir research)
    │   └── AccountTable.vue                 # MODIFIÉ : action Supprimer (confirmation + appel DELETE)
    ├── composables/
    │   ├── useCollectivityDocuments.ts      # Nouveau : upload, liste, réordo, remplacer, supprimer
    │   └── useComptes.ts                    # MODIFIÉ : méthode deleteCompte(id)
    ├── pages/
    │   ├── admin/
    │   │   ├── accounts/index.vue           # MODIFIÉ : colonne ACTIONS enrichie (Supprimer)
    │   │   └── geography/
    │   │       ├── communes/index.vue       # MODIFIÉ : liens « Voir les comptes » + « Soumettre un compte »
    │   │       ├── communes/[id].vue        # MODIFIÉ : intégration CollectivityDocumentsEditor après bannière
    │   │       ├── provinces/[id].vue       # MODIFIÉ : idem
    │   │       └── regions/[id].vue         # MODIFIÉ : idem
    │   ├── communes/[id].vue                # MODIFIÉ : affichage public des documents
    │   ├── provinces/[id].vue               # MODIFIÉ : idem
    │   └── regions/[id].vue                 # MODIFIÉ : idem
    └── types/
        └── collectivity-document.ts         # Nouveau : interface TS partagée

packages/shared/
└── src/collectivity.ts                      # MODIFIÉ : export du type CollectivityDocument
```

**Structure Decision**: application web existante, aucun nouveau projet ni réorganisation. Les ajouts sont localisés dans les dossiers conventionnels du backend (`models/`, `schemas/`, `routers/`, `services/`, `tests/`) et du frontend (`components/`, `composables/`, `pages/admin/`, `pages/<entity>/`). Le composant `CollectivityDocumentsEditor.vue` est mutualisé entre Province / Région / Commune pour éviter toute duplication.

## Complexity Tracking

> Aucune violation à documenter. Le plan reste dans les patterns existants.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
