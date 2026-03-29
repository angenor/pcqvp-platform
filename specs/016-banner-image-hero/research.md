# Research: 016-banner-image-hero

**Date**: 2026-03-28

## Decision 1: Stockage de l'image banniere

**Decision**: Ajouter un champ `banner_image` de type `String(500)`, nullable, sur les trois modeles (Province, Region, Commune). Le champ stocke le chemin relatif retourne par l'endpoint d'upload existant (ex: `/uploads/images/{uuid}.jpg`).

**Rationale**: Coherent avec le pattern ResourceLink.url existant. Un seul champ string suffit car la relation est 1:1 et l'image est deja stockee sur le serveur via l'endpoint d'upload. Pas besoin d'une table separee.

**Alternatives considered**:
- Table `banner_images` separee avec FK : surdimensionne pour une relation 1:1 simple
- Champ JSONB avec metadonnees (alt, credit) : non requis par la spec, le hero n'affiche que l'image

## Decision 2: Reutilisation de l'endpoint d'upload existant

**Decision**: Reutiliser `POST /api/admin/upload/image` pour l'upload des bannieres. Pas de nouvel endpoint.

**Rationale**: L'endpoint existant gere deja la validation (type, taille 5Mo), le stockage avec UUID, et l'authentification admin/editor. Le frontend uploade l'image, recupere l'URL, puis l'envoie dans le champ `banner_image` lors du PUT de la collectivite.

**Alternatives considered**:
- Endpoint dedie avec redimensionnement : complexite non justifiee par la spec
- Upload multipart dans le PUT de la collectivite : casse le pattern existant JSON body

## Decision 3: Migration Alembic

**Decision**: Creer une migration `007_add_banner_image.py` ajoutant `banner_image String(500) nullable` sur les 3 tables (provinces, regions, communes).

**Rationale**: Suit le pattern de numerotation sequentielle existant (001-006). Colonne nullable = pas de donnees a migrer, backward compatible.

**Alternatives considered**:
- 3 migrations separees : inutile, les 3 changements sont lies

## Decision 4: API publique

**Decision**: Ajouter `banner_image: str | null` dans la reponse de `GET /api/public/collectivites/{ctype}/{cid}/description` et dans le type `PublicDescriptionResponse`.

**Rationale**: Le frontend public a besoin de l'URL pour afficher le hero. Le champ est deja present dans l'entite, il suffit de l'inclure dans la serialisation.

**Alternatives considered**:
- Endpoint separe pour la banniere : sur-ingenierie pour un seul champ

## Decision 5: Composant hero section

**Decision**: Le hero section sera conditionnel dans la page `[type]-[id].vue`. Si `banner_image` est defini, afficher le hero full-bleed et masquer le bloc titre. Sinon, garder le layout actuel.

**Rationale**: Un seul composant `CollectiviteHero` reutilisable, avec `v-if` conditionnel. Pas de changement structurel pour les collectivites sans banniere.

**Alternatives considered**:
- Inline dans la page : moins reutilisable mais plus simple. On opte pour un composant car il encapsule le style complexe (overlay, responsive, dark mode)
