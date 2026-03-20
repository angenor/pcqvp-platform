# Research: 005-geography-hierarchy

**Date**: 2026-03-20

## R1: Editeur de contenu riche en blocs (Vue/Nuxt)

**Decision**: Editeur custom leger base sur un tableau de blocs JSON, sans librairie externe lourde.

**Rationale**: La spec definit 3 types de blocs simples (heading, paragraph, image). Utiliser TipTap ou ProseMirror serait une sur-ingenierie. Un composant Vue avec un tableau reactif de blocs, des boutons d'ajout et du drag-and-drop natif (HTML5 Drag API ou `v-sortable`) suffit. Le contenu est stocke en JSONB, ce qui rend la serialisation triviale.

**Alternatives considered**:
- TipTap/ProseMirror : trop complexe pour 3 types de blocs, dependance lourde
- Markdown editor : ne permet pas le controle fin des blocs (images inline, reordonnement)
- ContentEditable brut : problemes de sanitisation et compatibilite navigateur

## R2: Stockage JSONB avec SQLAlchemy async

**Decision**: Utiliser le type `JSONB` natif de SQLAlchemy avec `mapped_column(JSONB, default=list)`. Pas d'index GIN necessaire car pas de recherche dans le contenu riche.

**Rationale**: PostgreSQL JSONB est nativement supporte par SQLAlchemy et asyncpg. Le contenu riche est lu/ecrit en bloc (pas de requetes partielles). La validation de la structure des blocs se fait au niveau Pydantic (schema), pas au niveau base de donnees.

**Alternatives considered**:
- Table separee pour les blocs (normalise) : sur-ingenierie pour ce cas, requetes plus complexes
- JSON (non-binaire) : moins performant que JSONB, pas d'avantage ici

## R3: Selecteur chaine a 4 niveaux (Vue)

**Decision**: Composant Vue unique `GeographySelector.vue` avec 4 `<select>` reactifs. Le changement d'un niveau reinitialise les niveaux inferieurs via `watch`. Les donnees sont chargees via `useApi` : provinces au montage, regions/communes a la selection, annees via endpoint externe (placeholder tant que la feature comptes n'existe pas).

**Rationale**: Avec ~6 provinces, ~23 regions et ~1500 communes, le chargement a la demande (lazy) est adapte. L'arbre complet (`/api/geography/hierarchy`) est reserve aux cas ou tout l'arbre est necessaire d'un coup.

**Alternatives considered**:
- Chargement de l'arbre complet au montage : ~1500 communes en une requete, trop lourd
- Composant tiers (vue-treeselect) : sur-ingenierie pour des selects simples chaines

## R4: Pagination backend

**Decision**: Pagination offset-based avec parametres `skip` et `limit` (defaut: skip=0, limit=20). Retour d'un objet `{ items: [...], total: int }` pour permettre au frontend d'afficher la pagination.

**Rationale**: Coherent avec les patterns FastAPI standard. Offset-based est suffisant pour des listes d'entites admin (<2000 items). Le parametre `search` filtre par nom (ILIKE).

**Alternatives considered**:
- Cursor-based : plus complexe, necessaire pour des datasets tres larges (>100k), pas notre cas
- Pas de pagination (tout charger) : inacceptable pour ~1500 communes

## R5: Protection d'integrite referentielle a la suppression

**Decision**: Verification explicite dans le service avant suppression (compter les enfants). Pas de CASCADE DELETE. Retourner une erreur 409 Conflict avec message explicatif.

**Rationale**: La spec exige d'empecher la suppression avec un message clair. Un ON DELETE RESTRICT au niveau DB est un filet de securite supplementaire, mais le message d'erreur doit etre genere au niveau service pour etre user-friendly.

**Alternatives considered**:
- ON DELETE CASCADE : dangereux, suppression silencieuse des enfants
- ON DELETE RESTRICT seul : message d'erreur cryptique de la DB, pas user-friendly

## R6: Annee d'exercice - strategie d'integration

**Decision**: Le selecteur d'annee appelle un endpoint `/api/accounts/years` (ou similaire) qui sera fourni par la feature des comptes administratifs. En attendant, le composant accepte une prop `years` (tableau d'entiers) avec un fallback sur un etat vide/desactive. Un endpoint stub peut etre fourni temporairement.

**Rationale**: Decouplage net entre la feature geographie et la feature comptes. Le selecteur est pret a consommer les annees des qu'elles seront disponibles, sans modification.

**Alternatives considered**:
- Hardcoder une plage d'annees : ne reflete pas les donnees reelles
- Attendre la feature comptes : bloquerait le developpement du selecteur
