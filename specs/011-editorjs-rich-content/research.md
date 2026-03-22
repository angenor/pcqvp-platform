# Research: EditorJS Rich Content

## R1: Intégration EditorJS avec Nuxt 4

**Decision**: Utiliser EditorJS v2.31+ avec les plugins officiels, encapsulé dans un composant Vue 3 client-only via `<ClientOnly>`.

**Rationale**: EditorJS nécessite le DOM et ne peut pas être rendu côté serveur. Nuxt 4 fournit `<ClientOnly>` nativement pour ce cas d'usage. EditorJS est une bibliothèque mature (40k+ stars GitHub) avec un écosystème de plugins riche.

**Alternatives considered**:
- TipTap : plus complexe, overhead pour le besoin (blocs structurés)
- Quill : moins adapté au paradigme block-based
- Custom editor amélioré : coût de maintenance trop élevé

## R2: Packages EditorJS requis

**Decision**: Installer les packages suivants :
- `@editorjs/editorjs` - moteur principal
- `@editorjs/header` - blocs titre
- `@editorjs/paragraph` - blocs paragraphe (inclus par défaut)
- `@editorjs/image` - blocs image avec upload
- `@editorjs/table` - blocs tableau
- `@editorjs/list` - blocs liste (puces et numérotées)

**Rationale**: Ce sont les plugins officiels maintenus par l'équipe EditorJS, couvrant exactement les types de blocs requis par la spec (FR-002).

## R3: Format de données EditorJS vs format actuel

**Decision**: Stocker le format natif EditorJS dans `description_json`.

**Format EditorJS** :
```json
{
  "time": 1691234567890,
  "blocks": [
    { "id": "abc", "type": "header", "data": { "text": "Titre", "level": 2 } },
    { "id": "def", "type": "paragraph", "data": { "text": "Contenu" } },
    { "id": "ghi", "type": "image", "data": { "file": { "url": "/uploads/img.jpg" }, "caption": "Légende" } },
    { "id": "jkl", "type": "table", "data": { "content": [["A", "B"], ["C", "D"]] } },
    { "id": "mno", "type": "list", "data": { "style": "unordered", "items": ["Item 1", "Item 2"] } }
  ],
  "version": "2.31.0"
}
```

**Format actuel** (abandonné) :
```json
[
  { "type": "heading", "content": "Titre" },
  { "type": "paragraph", "content": "Contenu" },
  { "type": "image", "url": "https://...", "alt": "Alt" }
]
```

**Rationale**: Le format natif EditorJS est plus riche (métadonnées, IDs, niveaux de heading). Stocker directement ce format évite des conversions coûteuses et préserve toutes les fonctionnalités. Le champ JSONB PostgreSQL accepte n'importe quelle structure JSON.

## R4: Upload de fichiers images

**Decision**: Créer un nouvel endpoint backend `POST /api/admin/upload/image` qui :
- Accepte un fichier via `multipart/form-data`
- Valide le type MIME (image/jpeg, image/png, image/webp, image/gif)
- Valide la taille (max 5 MB)
- Stocke le fichier dans un répertoire `uploads/` local
- Retourne l'URL du fichier au format attendu par le plugin `@editorjs/image`
- Monte un `StaticFiles` pour servir les fichiers uploadés

**Rationale**: Aucun mécanisme d'upload n'existe actuellement dans le backend. Le plugin `@editorjs/image` attend un endpoint qui retourne `{ success: 1, file: { url: "..." } }`. `python-multipart` est déjà dans les dépendances.

**Alternatives considered**:
- Stockage cloud (S3) : over-engineering pour le stade actuel du projet
- URL uniquement : rejeté lors de la clarification, l'upload est requis

## R5: Mise à jour du search_vector

**Decision**: Aucune modification nécessaire pour le search_vector.

**Rationale**: Le search_vector actuel indexe uniquement le champ `name` via une colonne PostgreSQL `GENERATED ALWAYS AS`. Il n'indexe pas `description_json`. Ce comportement reste inchangé. Si l'indexation du contenu de description est souhaitée ultérieurement, elle pourra être ajoutée via un trigger ou une colonne computed étendue.

## R6: Validation backend du format EditorJS

**Decision**: Remplacer les schémas Pydantic actuels (`HeadingBlock`, `ParagraphBlock`, `ImageBlock`) par un schéma validant la structure EditorJS native (objet avec `blocks[]` contenant des blocs typés avec `data`).

**Rationale**: Le backend doit valider la structure pour prévenir l'injection de données malformées. Le format EditorJS a une structure prévisible avec des types de blocs connus.

## R7: Dark mode pour EditorJS

**Decision**: Appliquer des styles CSS personnalisés ciblant les classes EditorJS (`.codex-editor`, `.ce-block`, etc.) avec des variantes `dark:` Tailwind ou des sélecteurs `.dark`.

**Rationale**: EditorJS n'a pas de support dark mode natif. Le projet utilise `@nuxtjs/color-mode` avec stratégie `class`, ce qui permet de cibler `.dark .codex-editor` en CSS.

## R8: Migration des données existantes

**Decision**: Fournir un script Python standalone (`scripts/migrate_description_format.py`) qui convertit l'ancien format vers EditorJS.

**Rationale**: Le projet n'est pas en production. Le script sera utile pour les données de test existantes mais n'a pas besoin d'être robuste ou réversible. La conversion est simple : `heading` → `header`, `paragraph` → `paragraph`, `image` → `image` avec restructuration des données.
