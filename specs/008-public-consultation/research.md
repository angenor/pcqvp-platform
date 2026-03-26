# Research: 008-public-consultation

## R1: Pattern pour endpoints publics (sans auth)

**Decision**: Creer un nouveau router `public_comptes.py` avec prefix `/api/public/collectivites` sans aucune dependance d'auth.

**Rationale**: Le projet utilise deja ce pattern pour le router `geography.py` qui expose des endpoints publics sans `Depends(require_role(...))`. Les routes admin sont toutes sous `/api/admin/*`. Le prefix `/api/public/` separe clairement les endpoints publics des endpoints admin.

**Alternatives considered**:
- Reutiliser le router admin avec un filtre status=published → Risque de fuite de donnees brouillon, melange de concerns
- Ajouter les routes dans le router geography → Hors du scope geographique, pollution du namespace

## R2: Reutilisation des services existants pour les calculs

**Decision**: Reutiliser `account_service.py` (calculs, recapitulatifs, equilibre) et `compte_service.py` (chargement des comptes) avec un filtre supplementaire `status="published"`.

**Rationale**: Les fonctions `compute_line_values()`, `compute_hierarchical_sums()`, `calculate_recettes_recap()`, `calculate_depenses_recap()`, et `calculate_equilibre()` contiennent toute la logique metier. Les dupliquer serait une violation du principe III (simplicite). Il suffit d'ajouter une methode publique `get_published_compte()` qui filtre par status.

**Alternatives considered**:
- Dupliquer les services → Violation DRY, risque de divergence
- Exposer directement les endpoints admin → Risque de securite

## R3: Export Excel (openpyxl)

**Decision**: Utiliser openpyxl (deja en dependance) pour generer les fichiers Excel cote serveur. Creer un service `export_service.py` avec une fonction par format.

**Rationale**: openpyxl est deja utilise pour l'import de templates (seed_templates.py). L'export suit la meme logique en sens inverse. La generation cote serveur garantit la coherence des donnees et le format uniforme.

**Alternatives considered**:
- Export cote frontend (SheetJS/xlsx) → Pas de controle sur le format, dependance supplementaire, pas de Word
- CSV simple → Ne respecte pas la structure multi-feuilles requise

## R4: Export Word (python-docx)

**Decision**: Ajouter `python-docx>=1.1.0` aux dependances backend. Creer les documents Word cote serveur dans le meme service d'export.

**Rationale**: python-docx est la librairie standard Python pour generer des fichiers .docx. Pas d'alternative mature en Python. La generation cote serveur est coherente avec l'export Excel.

**Alternatives considered**:
- Pas d'export Word → Explicitement demande dans la spec (FR-016) et la constitution (formats ouverts)
- Conversion Excel→Word → Perte de qualite et de structure

## R5: Adaptation du GeographySelector pour la page publique

**Decision**: Modifier le GeographySelector existant pour accepter une prop `navigateTo` (callback ou pattern d'URL) au lieu de hardcoder les routes `/communes/{id}/annee/{year}`. La page d'accueil publique passera un pattern vers `/collectivite/{type}-{id}`.

**Rationale**: Le composant est deja bien structure avec props et watchers. Ajouter une prop de navigation est minimal et evite de dupliquer le composant. Le selectoreur d'annee sera gere sur la page de resultats (pas dans le selector lui-meme, car les annees disponibles dependent de la collectivite choisie).

**Alternatives considered**:
- Dupliquer le composant → Violation DRY
- Emit event au lieu de naviguer → Necessite que chaque parent gere la navigation, plus complexe

## R6: Structure des URL publiques

**Decision**: Route Nuxt `app/pages/collectivite/[type]-[id].vue` avec `type` = province|region|commune et `id` = UUID. L'annee est un query param ou un segment additionnel.

**Rationale**: Pattern clair et SEO-friendly. Le type dans l'URL permet de resoudre la collectivite sans ambiguite. Compatible avec le pattern existant des pages de detail geographique (`/provinces/[id]`, `/regions/[id]`, `/communes/[id]`).

**Alternatives considered**:
- `/communes/{id}?annee=` (reutiliser pages existantes) → Les pages existantes sont des pages de detail geographique, pas de consultation de comptes
- `/comptes/{compte_id}` → Expose l'ID interne du compte, pas stable si le compte est recree
