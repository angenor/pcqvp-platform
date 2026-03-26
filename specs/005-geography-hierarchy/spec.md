# Feature Specification: Gestion de la hierarchie geographique

**Feature Branch**: `005-geography-hierarchy`
**Created**: 2026-03-20
**Status**: Draft
**Input**: User description: "Gestion de la hierarchie geographique de Madagascar : Provinces, Regions, Communes avec CRUD admin, selecteur chaine public et editeur de contenu riche."

## Clarifications

### Session 2026-03-20

- Q: Le bouton OK du selecteur doit-il etre actif uniquement quand les 3 niveaux sont selectionnes, ou a n'importe quel niveau ? → A: Le selecteur comporte 4 niveaux chaines : Province (obligatoire) > Region (obligatoire) > Commune (optionnelle) > Annee d'exercice (obligatoire). Commune est optionnelle car certains comptes appartiennent au niveau Region. Le bouton OK est actif des que Province + Region + Annee sont remplis.
- Q: D'ou provient la liste des annees d'exercice disponibles dans le selecteur ? → A: L'annee d'exercice correspond a l'annee du compte administratif. La liste des annees est derivee des comptes administratifs existants (feature ulterieure). Ce feature fournit le selecteur UI ; les annees disponibles seront alimentees par l'API des comptes administratifs.
- Q: Les listes admin doivent-elles etre paginees (notamment ~1500 communes) ? → A: Oui, pagination avec 20 items par page + recherche textuelle.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Naviguer dans la hierarchie geographique (Priority: P1)

Un visiteur du site souhaite explorer les collectivites territoriales de Madagascar. Il arrive sur la page d'accueil et utilise un selecteur a quatre niveaux pour choisir une Province, puis une Region, eventuellement une Commune, puis une annee d'exercice, afin d'acceder a la fiche detaillee de la collectivite selectionnee pour l'annee choisie.

**Why this priority**: C'est le parcours principal du site. Sans la possibilite de naviguer dans la hierarchie geographique, le site n'a pas de valeur pour les citoyens. Ce selecteur est le point d'entree fondamental vers toute l'information locale.

**Independent Test**: Peut etre teste en chargeant la page d'accueil, en selectionnant une Province, une Region, une annee, et en verifiant la redirection vers la page de la collectivite.

**Acceptance Scenarios**:

1. **Given** le visiteur est sur la page d'accueil, **When** il ouvre le premier menu deroulant, **Then** toutes les provinces s'affichent par ordre alphabetique
2. **Given** le visiteur a selectionne une province, **When** il ouvre le deuxieme menu deroulant, **Then** seules les regions de cette province s'affichent
3. **Given** le visiteur a selectionne une region, **When** il ouvre le troisieme menu deroulant (commune), **Then** seules les communes de cette region s'affichent, et le champ est marque comme optionnel (pas d'asterisque rouge)
4. **Given** le visiteur a selectionne une region, **When** il ouvre le quatrieme menu deroulant (annee), **Then** les annees d'exercice disponibles s'affichent, et le champ est marque comme obligatoire (asterisque rouge)
5. **Given** le visiteur a selectionne Province + Region + Annee (sans commune), **When** il clique sur "OK", **Then** il est redirige vers la page de detail de la region pour l'annee selectionnee
6. **Given** le visiteur a selectionne Province + Region + Commune + Annee, **When** il clique sur "OK", **Then** il est redirige vers la page de detail de la commune pour l'annee selectionnee
7. **Given** le visiteur n'a rempli que Province et Region (sans annee), **When** il regarde le bouton "OK", **Then** le bouton est desactive
8. **Given** le visiteur a selectionne une province puis change de province, **When** la nouvelle province est selectionnee, **Then** les menus region, commune et annee sont reinitialises

---

### User Story 2 - Gerer les provinces, regions et communes (Priority: P2)

Un administrateur ou editeur souhaite ajouter, modifier ou supprimer des entites geographiques (provinces, regions, communes) via l'interface d'administration. Chaque entite possede un nom, un code unique et une description en contenu riche.

**Why this priority**: La gestion des donnees geographiques est indispensable pour alimenter le selecteur public. Sans donnees, le front public ne peut fonctionner.

**Independent Test**: Peut etre teste en se connectant a l'admin, en creant une province, puis une region rattachee, puis une commune rattachee, et en verifiant leur apparition dans les listes.

**Acceptance Scenarios**:

1. **Given** un admin est connecte, **When** il accede a la liste des provinces, **Then** il voit toutes les provinces existantes avec un champ de recherche
2. **Given** un admin est sur la liste des provinces, **When** il cree une nouvelle province avec un nom et un code, **Then** la province apparait dans la liste
3. **Given** un admin edite une province, **When** il modifie la description riche (titres, paragraphes, images), **Then** les modifications sont sauvegardees et visibles
4. **Given** un admin est sur la liste des regions, **When** il filtre par province, **Then** seules les regions de cette province s'affichent
5. **Given** un admin tente de supprimer une province qui contient des regions, **When** il confirme la suppression, **Then** le systeme empeche la suppression et affiche un message d'erreur expliquant que la province contient des regions

---

### User Story 3 - Consulter les details d'une collectivite (Priority: P3)

Un visiteur souhaite consulter les informations detaillees d'une province, d'une region ou d'une commune, incluant sa description riche (texte formate, images) et la liste de ses sous-divisions.

**Why this priority**: La consultation des fiches detaillees donne de la valeur a la navigation. C'est le contenu que les citoyens viennent chercher.

**Independent Test**: Peut etre teste en accedant directement a l'URL d'une province et en verifiant que la description riche et la liste des regions s'affichent correctement.

**Acceptance Scenarios**:

1. **Given** une province existe avec des regions, **When** un visiteur accede a la page de detail de cette province, **Then** il voit le nom, le code, la description riche et la liste des regions
2. **Given** une region existe avec des communes, **When** un visiteur accede a la page de detail de cette region, **Then** il voit le nom, le code, la description riche et la liste des communes
3. **Given** une commune existe avec une description riche contenant des images, **When** un visiteur accede a la page de detail, **Then** les images s'affichent correctement au sein du contenu

---

### User Story 4 - Editer du contenu riche pour les descriptions (Priority: P4)

Un administrateur ou editeur utilise un editeur de contenu riche pour composer les descriptions des entites geographiques. L'editeur permet d'inserer des titres, paragraphes et images, stockes sous forme de blocs structures.

**Why this priority**: L'editeur de contenu riche est un outil transversal qui sera reutilise pour d'autres fonctionnalites du site. Il est essentiel pour la qualite du contenu.

**Independent Test**: Peut etre teste en ouvrant l'editeur sur une entite, en ajoutant un titre, un paragraphe et une image, puis en verifiant que le contenu sauvegarde est correctement restitue.

**Acceptance Scenarios**:

1. **Given** un admin edite une entite, **When** il ajoute un bloc de type "titre", **Then** le bloc apparait dans l'editeur et est sauvegarde correctement
2. **Given** un admin edite une entite, **When** il ajoute un bloc de type "paragraphe" avec du texte, **Then** le texte est sauvegarde et affiche dans le bon ordre
3. **Given** un admin edite une entite, **When** il ajoute un bloc de type "image" avec une URL, **Then** l'image est sauvegardee et s'affiche en previsualisation
4. **Given** un admin a ajoute plusieurs blocs, **When** il reordonne les blocs, **Then** le nouvel ordre est preserve apres sauvegarde

---

### Edge Cases

- Que se passe-t-il si un admin tente de creer une province/region/commune avec un code deja existant ? Le systeme doit refuser et afficher un message d'erreur
- Que se passe-t-il si un admin supprime une region qui contient des communes ? Le systeme doit empecher la suppression (protection d'integrite referentielle)
- Que se passe-t-il si aucune province n'existe ? Le selecteur affiche un etat vide avec un message informatif
- Que se passe-t-il si une province n'a aucune region ? Le menu region est desactive avec un message "Aucune region disponible"
- Que se passe-t-il si la description riche contient une URL d'image invalide ? Le systeme affiche un placeholder au lieu de l'image cassee
- Que se passe-t-il si un visiteur accede a une URL de collectivite inexistante ? Le systeme affiche une page 404 appropriee
- Que se passe-t-il si aucune annee d'exercice n'est disponible ? Le menu annee est desactive avec un message informatif

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le systeme DOIT permettre de stocker des entites geographiques organisees en trois niveaux hierarchiques : Province, Region, Commune
- **FR-002**: Chaque entite geographique DOIT posseder un nom, un code unique et une description en contenu riche structure
- **FR-003**: Chaque Region DOIT etre rattachee a exactement une Province
- **FR-004**: Chaque Commune DOIT etre rattachee a exactement une Region
- **FR-005**: Le systeme DOIT fournir un selecteur a quatre niveaux chaines : Province (obligatoire) > Region (obligatoire) > Commune (optionnelle) > Annee d'exercice (obligatoire). Le bouton OK est actif des que les trois champs obligatoires sont remplis.
- **FR-006**: Le systeme DOIT fournir une vue hierarchique complete (arbre Province > Region > Commune) pour alimenter les selecteurs
- **FR-007**: Les operations de creation, modification et suppression des entites DOIVENT etre reservees aux utilisateurs ayant le role administrateur ou editeur
- **FR-008**: La consultation des entites (liste et detail) DOIT etre accessible sans authentification
- **FR-009**: Le systeme DOIT empecher la suppression d'une entite parente si elle contient des sous-entites (integrite referentielle)
- **FR-010**: Le systeme DOIT permettre de filtrer les regions par province et les communes par region
- **FR-011**: Le systeme DOIT permettre la recherche textuelle dans les listes d'entites en administration, avec pagination (20 items par page par defaut)
- **FR-012**: Le code de chaque entite DOIT etre unique au sein de son niveau hierarchique
- **FR-013**: Le systeme DOIT fournir un editeur de contenu riche permettant de composer des descriptions avec des blocs de type titre, paragraphe et image
- **FR-014**: Le contenu riche DOIT etre stocke sous forme de blocs structures (type + contenu)
- **FR-015**: Le systeme DOIT afficher le contenu riche de maniere fidele a la fois dans l'editeur et dans les pages publiques
- **FR-016**: Le selecteur DOIT indiquer visuellement les champs obligatoires (asterisque rouge) et les champs optionnels
- **FR-017**: Le selecteur d'annee DOIT afficher les annees pour lesquelles des comptes administratifs existent. La source de ces annees est une API fournie par la feature des comptes administratifs (dependance externe)

### Key Entities

- **Province**: Entite geographique de premier niveau. Possede un nom, un code unique et une description riche. Contient zero ou plusieurs regions.
- **Region**: Entite geographique de deuxieme niveau. Appartient a une province. Possede un nom, un code unique et une description riche. Contient zero ou plusieurs communes.
- **Commune**: Entite geographique de troisieme niveau. Appartient a une region. Possede un nom, un code unique et une description riche.
- **Bloc de contenu riche**: Element unitaire d'une description (titre, paragraphe ou image). Possede un type et un contenu. Ordonne au sein d'une description.
- **Annee d'exercice**: Annee du compte administratif d'une collectivite. Derivee des comptes administratifs existants. Utilisee comme parametre de navigation obligatoire dans le selecteur.

## Assumptions

- Les roles administrateur et editeur existent deja dans le systeme (feature 004-auth-roles)
- Il n'y a pas de limite au nombre de blocs dans une description riche
- L'upload d'images est hors scope ; les images sont referencees par URL
- Le selecteur redirige vers une page de type `/regions/{id}/annee/{year}` ou `/communes/{id}/annee/{year}` selon la selection
- Les listes publiques de provinces sont suffisamment petites pour etre chargees en une seule requete (pas de pagination necessaire pour le selecteur)
- Le contenu riche ne supporte pas de blocs imbriques (structure plate)
- La liste des annees d'exercice est derivee des comptes administratifs existants. Tant que la feature des comptes n'est pas implementee, le selecteur d'annee affichera une liste vide ou un placeholder
- Le selecteur d'annee consomme une API externe (comptes administratifs) ; cette feature definit uniquement l'interface du selecteur, pas la source de donnees

## Out of Scope

- Comptes administratifs (couvert par feature 004)
- Donnees financieres (feature separee)
- Upload de fichiers/images (les images sont referencees par URL)
- Gestion des fokontany ou autres niveaux sous-communaux
- Import/export en masse des donnees geographiques
- Cartographie ou affichage sur carte
- Gestion CRUD des annees d'exercice (ce feature fournit uniquement le selecteur; la gestion des annees releve d'une feature ulterieure)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un visiteur peut selectionner une collectivite et une annee via le selecteur a quatre niveaux en moins de 20 secondes
- **SC-002**: 100% des provinces, regions et communes crees via l'admin apparaissent dans le selecteur public sans intervention supplementaire
- **SC-003**: Un administrateur peut creer une nouvelle entite geographique complete (avec description riche) en moins de 3 minutes
- **SC-004**: Le selecteur affiche les options du niveau suivant en moins de 1 seconde apres une selection
- **SC-005**: Le contenu riche saisi dans l'editeur admin s'affiche de maniere identique sur les pages publiques
- **SC-006**: Le systeme empeche 100% des tentatives de suppression d'entites parentes contenant des sous-entites
- **SC-007**: Le bouton OK reste desactive tant que les 3 champs obligatoires (Province, Region, Annee) ne sont pas remplis
