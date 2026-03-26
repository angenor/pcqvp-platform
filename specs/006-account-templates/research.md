# Research: 006-account-templates

**Date**: 2026-03-20 | **Branch**: `006-account-templates`

## 1. Parsing Excel avec openpyxl

**Decision**: Utiliser openpyxl pour parser les fichiers Excel de reference dans le script de seed.

**Rationale**: openpyxl est la bibliotheque standard Python pour lire/ecrire des fichiers .xlsx. Elle supporte la lecture des formules, des valeurs et de la structure des feuilles. Elle est legere et n'a pas de dependances systeme.

**Alternatives considered**:
- pandas : Trop lourd pour un simple parsing de structure, ajoute une dependance massive
- xlrd : Ne supporte que le format .xls ancien, pas .xlsx
- openpyxl (choisi) : Lecture native .xlsx, acces aux formules, leger

**Action**: Ajouter `openpyxl>=3.1.0` aux dependances backend dans pyproject.toml.

## 2. Modelisation de la hierarchie des comptes

**Decision**: Utiliser une table unique `account_template_lines` avec les colonnes `level` (1/2/3), `parent_code` (nullable), et `section` (enum fonctionnement/investissement) pour representer la hierarchie.

**Rationale**: L'analyse des fichiers Excel montre une hierarchie a 3 niveaux fixes (2/3/4 chiffres). Une table unique avec parent_code est plus simple qu'un modele polymorphique ou une table par niveau. Le parent_code (pas parent_id) permet de referenceR les lignes par leur code comptable naturel, ce qui simplifie l'import Excel.

**Alternatives considered**:
- Table par niveau (3 tables) : Sur-ingenierie pour une hierarchie fixe a 3 niveaux
- Materialized path : Complexite inutile pour 3 niveaux
- Adjacency list avec parent_code (choisi) : Simple, direct, conforme a la nomenclature comptable

## 3. Stockage des formules de colonnes calculees

**Decision**: Stocker les formules sous forme declarative dans le champ `formula` de `account_template_columns` (ex: `"budget_primitif + budget_additionnel + modifications"`).

**Rationale**: Les formules sont simples (addition, soustraction, division) et n'impliquent que des colonnes du meme template. Un format declaratif (references aux codes de colonnes) est suffisant et interpretable cote frontend pour le calcul a l'affichage. Pas besoin d'un moteur d'expressions complexe.

**Alternatives considered**:
- Formules Excel brutes : Non portable, couple au format Excel
- Code Python/JS evalue dynamiquement : Risque d'injection, complexe
- Format declaratif avec codes de colonnes (choisi) : Simple, securise, interpretable partout

## 4. Calcul des agregations (sommes hierarchiques)

**Decision**: Les sommes hierarchiques (Niv1 = somme Niv2, Niv2 = somme Niv3) et les sous-totaux par section sont calcules dynamiquement a l'affichage (frontend), pas stockes en base.

**Rationale**: Conformement a la clarification spec, les lignes parentes ne contiennent jamais de donnees saisies directement. Seules les feuilles (Niv3) ont des valeurs. Les sommes sont derivables de la hierarchie. Cela evite les problemes de coherence et simplifie les mises a jour.

**Alternatives considered**:
- Stored computed columns (triggers) : Complexite de maintenance
- Materialized views : Sur-ingenierie pour cette taille de donnees
- Calcul frontend a l'affichage (choisi) : Simple, coherent, pas de donnees perimees

## 5. Strategie d'import idempotent

**Decision**: L'import utilise `ON CONFLICT (template_type + code)` pour les lignes et les colonnes. Si le template existe deja (meme nom + type), il est mis a jour au lieu d'etre recree.

**Rationale**: L'idempotence est une exigence (FR-010). L'approche upsert est la plus simple et garantit qu'un import relance ne cree pas de doublons tout en permettant des mises a jour si la structure de reference evolue.

**Alternatives considered**:
- Drop + recreate : Destructif, perd les references FK
- Check + skip : Ne permet pas les mises a jour
- Upsert (choisi) : Idempotent et evolutif

## 6. Structure des fichiers Excel de reference

**Decision**: Les fichiers Excel sont deja copies dans `apps/backend/app/data/reference/`. Le script de seed les lit directement depuis ce chemin.

**Findings from analysis**:

### Template_Tableaux_de_Compte_Administratif.xlsx (8 feuilles)
- **RECETTES** : 182 lignes, 168 comptes (14 Niv1 + 36 Niv2 + 118 Niv3), colonnes A-M
  - Section Fonctionnement : comptes 70-77
  - Section Investissement : comptes 10-16
- **DEPENSES PROGRAMME I/II/III** : 289 lignes chacune, 273 comptes (16 Niv1 + 59 Niv2 + 198 Niv3), colonnes A-N
  - Section Fonctionnement : comptes 60-67, 12
  - Section Investissement : comptes 16, 20-21
- Colonnes recettes : COMPTE, INTITULES, BUDGET PRIMITIF, BUDGET ADDITIONNEL, MODIFICATIONS, PREVISIONS DEFINITIVES, OR ADMIS, RECOUVREMENT, RESTE A RECOUVRER, TAUX D'EXECUTION
- Colonnes depenses : idem + ENGAGEMENT, MANDAT ADMIS, PAIEMENT, RESTE A PAYER
- Hierarchie : Niv1 en col B, Niv2 en col C, Niv3 en col D, intitule en col E

### COMPTE_ADMINISTRATIF_COMMUNE_ANDRAFIABE_2023.xlsx (12 feuilles)
- Structure similaire mais avec donnees reelles
- 3 programmes : ADMINISTRATION ET COORDINATION, DEVELOPPEMENT ECONOMIQUE ET SOCIAL, SANTE
- Donnees sur ~48 lignes de recettes, ~50-70 lignes de depenses par programme

## 7. Patterns backend existants a suivre

**Decision**: Suivre exactement les patterns etablis dans les features 004 (auth) et 005 (geography).

| Aspect | Pattern existant | Application |
|--------|-----------------|-------------|
| Modele | UUIDBase + fields | AccountTemplate, AccountTemplateLine, AccountTemplateColumn |
| Schema | Create/Update/List/Detail | TemplateCreate, TemplateList, TemplateDetail, etc. |
| Service | Fonctions async avec AsyncSession | template_service.py |
| Router | admin_*.py avec require_role | admin_templates.py |
| Migration | 00X_ prefix | 003_create_account_template_tables.py |
| Test | conftest fixtures + classes | test_templates.py |

## 8. Patterns frontend existants a suivre

**Decision**: Suivre le pattern admin geography (list + detail/edit pages).

| Aspect | Pattern existant | Application |
|--------|-----------------|-------------|
| Pages | admin/geography/{entity}/index.vue + [id].vue | admin/templates/index.vue + [id].vue |
| Composable | useGeography.ts | useTemplates.ts |
| Types | packages/shared/types/geography.ts | packages/shared/types/templates.ts |
| Layout | admin.vue avec sidebar | Ajouter lien Templates dans sidebar |
| Dark mode | Classes dark: sur tous les elements | Obligatoire |
