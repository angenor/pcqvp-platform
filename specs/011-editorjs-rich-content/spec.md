# Feature Specification: EditorJS Rich Content pour Géographies

**Feature Branch**: `011-editorjs-rich-content`
**Created**: 2026-03-22
**Status**: Draft
**Input**: User description: "dans le back office, pour provinces, regions et communes la description doit est écrit avec editorJs afin de pouvoir ajouter librement text, images et tableau au lieu de champs fix"

## Clarifications

### Session 2026-03-22

- Q: Comment les images doivent-elles être ajoutées dans l'éditeur ? → A: Upload de fichiers vers le serveur + URL en option.
- Q: Les listes doivent-elles faire partie des blocs supportés ? → A: Oui, inclure les listes (à puces et numérotées) dès maintenant.
- Q: Faut-il maintenir la rétrocompatibilité avec l'ancien format ? → A: Non, abandonner l'ancien format avec migration ponctuelle si nécessaire.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rédaction de contenu riche avec EditorJS (Priority: P1)

En tant qu'administrateur ou éditeur, je souhaite rédiger la description d'une province, région ou commune à l'aide d'un éditeur EditorJS complet, afin de créer du contenu structuré avec paragraphes, titres, images et tableaux sans être limité par des champs fixes.

**Why this priority**: C'est la fonctionnalité principale demandée. Sans l'éditeur EditorJS fonctionnel dans les formulaires d'administration, aucune autre story n'a de valeur.

**Independent Test**: Peut être testé en accédant à la page d'édition d'une province, en utilisant l'éditeur EditorJS pour ajouter du texte, un titre, une image et un tableau, puis en sauvegardant. Les données doivent être persistées et rechargées correctement à la réouverture du formulaire.

**Acceptance Scenarios**:

1. **Given** un administrateur sur la page d'édition d'une province, **When** il clique dans la zone de description, **Then** un éditeur EditorJS interactif s'affiche avec une barre d'outils proposant les blocs disponibles (paragraphe, titre, image, tableau).
2. **Given** un éditeur EditorJS avec du contenu, **When** l'administrateur ajoute un bloc tableau et remplit des cellules, **Then** le tableau est inséré dans le contenu et ses données sont préservées.
3. **Given** un éditeur EditorJS avec du contenu mixte (texte, images, tableaux), **When** l'administrateur sauvegarde le formulaire, **Then** toutes les données sont persistées et restaurées fidèlement à la réouverture.
4. **Given** un formulaire d'édition avec du contenu déjà au format EditorJS, **When** l'administrateur ouvre la page, **Then** le contenu est chargé et affiché fidèlement dans l'éditeur.

---

### User Story 2 - Affichage public du contenu EditorJS (Priority: P1)

En tant que visiteur du site, je souhaite voir le contenu riche (texte, images, tableaux) des pages géographiques rendu de manière fidèle et lisible, afin de consulter des informations bien formatées.

**Why this priority**: Le contenu riche n'a de valeur que s'il est correctement affiché côté public. Cette story est indissociable de la P1 d'édition.

**Independent Test**: Peut être testé en créant du contenu avec EditorJS dans l'admin, puis en visitant la page publique correspondante pour vérifier que tous les types de blocs (texte, titres, images, tableaux) sont rendus correctement.

**Acceptance Scenarios**:

1. **Given** une province avec une description contenant des blocs EditorJS (paragraphes, titres, images, tableaux), **When** un visiteur consulte la page publique de cette province, **Then** chaque type de bloc est rendu avec un formatage approprié et lisible.
2. **Given** un bloc tableau dans la description, **When** le contenu est affiché publiquement, **Then** le tableau est rendu sous forme de table avec lignes, colonnes et en-têtes clairement distincts.
3. **Given** un contenu avec des images, **When** l'image ne peut pas être chargée, **Then** un placeholder ou un message alternatif est affiché.

---

### User Story 3 - Uniformité entre provinces, régions et communes (Priority: P2)

En tant qu'administrateur, je souhaite que l'expérience d'édition avec EditorJS soit identique sur les trois types d'entités géographiques (provinces, régions, communes), afin d'avoir une expérience cohérente.

**Why this priority**: L'uniformité est importante pour l'expérience utilisateur mais est une conséquence naturelle d'une bonne implémentation de P1.

**Independent Test**: Peut être testé en naviguant entre les pages d'édition de chaque type d'entité géographique et en vérifiant que l'éditeur offre les mêmes fonctionnalités et la même apparence.

**Acceptance Scenarios**:

1. **Given** un administrateur sur la page d'édition d'une région, **When** il utilise l'éditeur de description, **Then** les mêmes outils et blocs sont disponibles que sur la page d'édition d'une province ou d'une commune.
2. **Given** du contenu identique créé dans les trois types d'entités, **When** il est affiché publiquement, **Then** le rendu est visuellement identique.

---

### Edge Cases

- Que se passe-t-il si l'utilisateur colle du contenu HTML complexe depuis un document externe (Word, page web) ? Le contenu doit être nettoyé et converti en blocs EditorJS valides.
- Que se passe-t-il si la description est vide (aucun bloc) ? Le formulaire doit sauvegarder correctement avec une description vide.
- Que se passe-t-il si le contenu en base est dans l'ancien format (non migré) ? L'éditeur doit afficher un message indiquant que le contenu nécessite une migration.
- Comment le mode sombre est-il géré dans l'éditeur EditorJS ? L'éditeur et tous ses blocs doivent respecter le thème clair/sombre du back office.
- Que se passe-t-il si une image référencée dans un bloc est supprimée du serveur ? Un placeholder doit être affiché à la place.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT remplacer l'éditeur de contenu actuel (RichContentEditor) par un éditeur EditorJS dans les formulaires d'administration des provinces, régions et communes.
- **FR-002**: L'éditeur EditorJS DOIT supporter au minimum les types de blocs suivants : paragraphe, titre (heading), image, tableau et listes (à puces et numérotées).
- **FR-003**: Le système DOIT persister le contenu EditorJS au format natif EditorJS (structure JSON avec `time`, `blocks`, `version`) dans le champ `description_json` existant.
- **FR-004**: L'ancien format de contenu (blocs `heading`, `paragraph`, `image`) est abandonné. Un script de migration ponctuel DOIT être fourni pour convertir les données existantes au format EditorJS si nécessaire.
- **FR-005**: Le composant de rendu public DOIT afficher correctement tous les types de blocs EditorJS supportés, y compris les tableaux.
- **FR-006**: L'éditeur et le rendu DOIVENT fonctionner correctement en mode clair et en mode sombre.
- **FR-007**: L'éditeur DOIT permettre la réorganisation des blocs par glisser-déposer (fonctionnalité native d'EditorJS).
- **FR-008**: L'éditeur DOIT supporter le collage de texte simple et nettoyer le HTML collé pour produire des blocs valides.
- **FR-009**: Le système DOIT valider la structure du contenu EditorJS côté serveur avant de le persister.
- **FR-010**: L'éditeur DOIT permettre l'ajout d'images par upload de fichiers vers le serveur ainsi que par saisie d'URL externe.
- **FR-011**: Le système DOIT fournir un endpoint d'upload de fichiers images dédié à l'éditeur, avec validation du type et de la taille des fichiers.

### Key Entities

- **EditorJS Content**: Structure JSON contenant un tableau de blocs, chaque bloc ayant un type (`paragraph`, `header`, `image`, `table`) et des données spécifiques au type. Remplace la structure de blocs simplifiée actuelle.
- **Province / Region / Commune**: Entités géographiques existantes dont le champ `description_json` stockera désormais du contenu au format EditorJS natif.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Les administrateurs peuvent créer et modifier du contenu avec paragraphes, titres, images et tableaux en moins de 2 minutes pour une page type.
- **SC-002**: Si des données existantes au format ancien sont présentes, le script de migration les convertit au format EditorJS sans perte de contenu textuel.
- **SC-003**: Le rendu public de tous les types de blocs (paragraphe, titre, image, tableau, listes) est visuellement fidèle au contenu saisi dans l'éditeur.
- **SC-004**: L'éditeur fonctionne correctement en mode clair et sombre sans artefacts visuels.
- **SC-005**: Le contenu sauvegardé puis rechargé dans l'éditeur est identique au contenu original (aucune perte ou corruption de données au cycle sauvegarde/chargement).

## Assumptions

- EditorJS est une bibliothèque JavaScript open-source mature et compatible avec le framework frontend du projet.
- Le format JSON natif d'EditorJS sera stocké directement dans le champ JSONB existant `description_json`, sans nécessiter de modification de schéma de base de données.
- L'upload d'images utilisera le mécanisme existant de la plateforme.
- La recherche full-text existante (search_vector) continuera de fonctionner en extrayant le texte brut des blocs EditorJS.
- Le projet n'étant pas encore en production, l'ancien format de contenu est abandonné sans rétrocompatibilité. Un script de migration ponctuel sera fourni si des données de test existent.

## Scope Boundaries

**Inclus** :
- Remplacement de l'éditeur actuel par EditorJS dans les 3 formulaires admin (provinces, régions, communes)
- Support des blocs : paragraphe, titre, image, tableau, listes (à puces et numérotées)
- Rendu public de tous les blocs supportés
- Script de migration ponctuel pour l'ancien format si nécessaire
- Support du mode clair/sombre

**Exclus** :
- Ajout de nouveaux types de blocs au-delà de paragraphe, titre, image, tableau et listes
- Gestion avancée des médias (galerie, recadrage d'images)
- Changement de la structure de la base de données
