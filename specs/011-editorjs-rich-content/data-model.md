# Data Model: EditorJS Rich Content

## Entités modifiées

### Province / Region / Commune

Aucune modification de schéma de base de données. Le champ `description_json` (JSONB) change de format de contenu.

**Avant** (ancien format) :
```
description_json: list[RichContentBlock]
  - RichContentBlock: { type, content?, url?, alt? }
```

**Après** (format EditorJS natif) :
```
description_json: EditorJSData
  - EditorJSData: { time: int, blocks: list[EditorJSBlock], version: str }
  - EditorJSBlock: { id: str, type: str, data: dict }
```

### Types de blocs supportés

| Type EditorJS | Champ `data` | Description |
|---------------|-------------|-------------|
| `header` | `{ text: str, level: int(1-6) }` | Titre avec niveau hiérarchique |
| `paragraph` | `{ text: str }` | Paragraphe de texte |
| `image` | `{ file: { url: str }, caption?: str, withBorder?: bool, stretched?: bool, withBackground?: bool }` | Image avec légende optionnelle |
| `table` | `{ withHeadings?: bool, content: list[list[str]] }` | Tableau avec lignes et colonnes |
| `list` | `{ style: "ordered"\|"unordered", items: list[str] }` | Liste ordonnée ou non ordonnée |

## Nouvelles entités

Aucune nouvelle table en base de données.

## Fichiers uploadés

Les images uploadées via l'éditeur sont stockées en tant que fichiers sur le système de fichiers du serveur :

```
apps/backend/uploads/
└── images/
    └── {uuid}.{ext}     # Fichier image renommé avec UUID
```

**Attributs du fichier** :
- Nom : UUID v4 généré côté serveur
- Types acceptés : image/jpeg, image/png, image/webp, image/gif
- Taille max : 5 MB
- URL servie : `/uploads/images/{uuid}.{ext}`

## Schémas Pydantic (backend)

### EditorJSBlock (nouveau)

```
EditorJSBlock:
  id: str (optionnel)
  type: str (enum: header, paragraph, image, table, list)
  data: dict (structure variable selon le type)
```

### EditorJSData (nouveau)

```
EditorJSData:
  time: int (optionnel)
  blocks: list[EditorJSBlock]
  version: str (optionnel)
```

### ImageUploadResponse (nouveau)

```
ImageUploadResponse:
  success: int (1 = succès, 0 = échec)
  file: { url: str }
```

## Relations

Aucune nouvelle relation. Les entités Province, Region, Commune conservent leurs relations existantes (Province → Region → Commune via FK).

## Validation

- Le backend valide que chaque bloc a un `type` parmi les types supportés
- Le backend valide la structure `data` de chaque bloc selon son type
- Les images uploadées sont validées (type MIME, taille)
- Le contenu HTML dans les blocs texte est sanitisé
