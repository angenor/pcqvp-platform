# Feature Specification: Image banniere hero section collectivites

**Feature Branch**: `016-banner-image-hero`
**Created**: 2026-03-28
**Status**: Draft
**Input**: User description: "on veut pouvoir ajouter une image banniere a une commune et une region dans le backoffice afin qu'elle s'affiche dans le hero section (a creer) de la page de details collectivite/[type]-[id].vue"

## Clarifications

### Session 2026-03-28

- Q: Quelle hauteur pour le hero section ? → A: Hero moyen (~250-300px), bon equilibre image/contenu.
- Q: Le hero doit-il etre full-bleed ou contenu dans max-w-6xl ? → A: Full-bleed (bord a bord), texte centre.
- Q: Le hero remplace-t-il le bloc titre existant ou coexiste-t-il ? → A: Le hero remplace le bloc titre (nom + type affiches uniquement dans le hero). La description riche (description_json) reste affichee apres le hero si elle existe.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ajouter une image banniere depuis le backoffice (Priority: P1)

Un administrateur ou editeur se rend sur la page d'edition d'une commune ou d'une region dans le backoffice. Il voit un champ d'upload d'image banniere au-dessus du formulaire existant. Il selectionne une image depuis son ordinateur, voit un apercu de l'image, puis enregistre la collectivite. L'image banniere est stockee et associee a cette collectivite.

**Why this priority**: Sans la possibilite d'ajouter une image banniere, la fonctionnalite hero section n'a aucun contenu a afficher. C'est le prerequis indispensable.

**Independent Test**: Peut etre teste en uploadant une image sur une commune/region existante dans le backoffice et en verifiant que l'image est bien sauvegardee (visible dans le formulaire apres rechargement de la page).

**Acceptance Scenarios**:

1. **Given** un editeur sur la page d'edition d'une commune, **When** il selectionne une image et enregistre, **Then** l'image banniere est sauvegardee et visible dans l'apercu du formulaire.
2. **Given** un editeur sur la page d'edition d'une region, **When** il selectionne une image et enregistre, **Then** l'image banniere est sauvegardee et visible dans l'apercu du formulaire.
3. **Given** un editeur qui a deja ajoute une banniere, **When** il revient sur la page d'edition, **Then** l'image banniere existante est affichee dans l'apercu.
4. **Given** un editeur avec une banniere existante, **When** il selectionne une nouvelle image et enregistre, **Then** l'ancienne image est remplacee par la nouvelle.
5. **Given** un editeur avec une banniere existante, **When** il supprime l'image et enregistre, **Then** la banniere est retiree de la collectivite.

---

### User Story 2 - Affichage du hero section sur la page publique (Priority: P2)

Un visiteur se rend sur la page de detail d'une commune ou region qui possede une image banniere. En haut de la page, un hero section full-bleed (~250-300px) affiche l'image banniere en pleine largeur de l'ecran avec le nom de la collectivite et son type superposes (texte centre). Le hero remplace le bloc titre existant. La description riche (description_json) reste affichee juste apres le hero si elle est definie. L'affichage est adapte au mode clair et sombre et est responsive.

**Why this priority**: C'est l'objectif final visible par les utilisateurs publics. Depend de la P1 pour avoir du contenu a afficher.

**Independent Test**: Peut etre teste en visitant la page publique d'une collectivite possedant une image banniere et en verifiant l'affichage du hero section avec le nom superpose.

**Acceptance Scenarios**:

1. **Given** une collectivite avec une image banniere, **When** un visiteur accede a sa page de detail, **Then** un hero section full-bleed (~250-300px) affiche l'image en arriere-plan avec le nom et le type superposes, et le bloc titre habituel n'apparait pas.
2. **Given** une collectivite avec une banniere et une description riche, **When** un visiteur accede a sa page, **Then** la description riche est affichee juste apres le hero section.
3. **Given** une collectivite sans image banniere, **When** un visiteur accede a sa page de detail, **Then** la page s'affiche comme actuellement avec le bloc titre classique (comportement par defaut preserve).
4. **Given** un visiteur en mode sombre, **When** il consulte le hero section, **Then** le texte superpose reste lisible grace a un overlay adapte.
5. **Given** un visiteur sur mobile, **When** il consulte le hero section, **Then** l'image et le texte s'adaptent a la taille de l'ecran (hauteur reduite, texte redimensionne).

---

### User Story 3 - Gestion de la banniere province (Priority: P3)

Un administrateur ou editeur ajoute une image banniere a une province de la meme maniere que pour les communes et regions. Le hero section de la page de detail d'une province affiche egalement la banniere si elle est definie.

**Why this priority**: Les provinces sont moins nombreuses que les communes/regions, mais la coherence de l'experience utilisateur justifie d'etendre la fonctionnalite. Peut etre implementee apres les deux premieres stories.

**Independent Test**: Peut etre teste en ajoutant une banniere a une province et en verifiant l'affichage sur la page publique.

**Acceptance Scenarios**:

1. **Given** un editeur sur la page d'edition d'une province, **When** il ajoute une image banniere et enregistre, **Then** la banniere est sauvegardee.
2. **Given** une province avec banniere, **When** un visiteur accede a sa page, **Then** le hero section affiche la banniere.

---

### Edge Cases

- Que se passe-t-il si l'image uploadee est trop lourde (> 5 Mo) ? Le systeme doit refuser l'upload avec un message explicite.
- Que se passe-t-il si le format d'image n'est pas supporte ? Le systeme doit afficher un message d'erreur clair (seuls JPEG, PNG, WebP, GIF sont acceptes).
- Que se passe-t-il si l'image banniere referencee n'existe plus sur le serveur ? Le hero section ne doit pas s'afficher (fallback au comportement sans banniere).
- Que se passe-t-il si l'image est tres large ou tres haute ? L'image doit etre cadree (recadrage visuel) pour s'adapter aux dimensions du hero section sans deformation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le systeme DOIT permettre l'upload d'une image banniere lors de l'edition d'une commune, region ou province dans le backoffice.
- **FR-002**: Le systeme DOIT afficher un apercu de l'image banniere dans le formulaire d'edition apres selection ou lors du chargement d'une entite existante.
- **FR-003**: Le systeme DOIT permettre la suppression de l'image banniere d'une collectivite.
- **FR-004**: Le systeme DOIT stocker la reference a l'image banniere (chemin du fichier) dans les donnees de la collectivite.
- **FR-005**: Le systeme DOIT afficher un hero section full-bleed (~250-300px de hauteur) en haut de la page publique de detail lorsqu'une image banniere est definie.
- **FR-006**: Le hero section DOIT afficher le nom de la collectivite et son type superposes et centres sur l'image banniere.
- **FR-007**: Le hero section DOIT remplacer le bloc titre existant (nom + type) lorsqu'une banniere est presente. La description riche (description_json) DOIT rester affichee apres le hero si elle existe.
- **FR-008**: Le hero section DOIT etre responsive et s'adapter aux ecrans mobile, tablette et desktop.
- **FR-009**: Le hero section DOIT etre compatible avec les modes clair et sombre (overlay pour lisibilite du texte).
- **FR-010**: Le systeme DOIT respecter les contraintes d'upload existantes : taille max 5 Mo, formats JPEG/PNG/WebP/GIF.
- **FR-011**: La page publique de detail DOIT conserver son comportement actuel (bloc titre classique) lorsqu'aucune banniere n'est definie.
- **FR-012**: Le systeme DOIT inclure l'URL de l'image banniere dans la reponse de l'API publique de description de la collectivite.

### Key Entities

- **Image banniere**: Image associee a une collectivite (commune, region ou province). Attributs cles : URL du fichier image. Relation un-pour-un avec une collectivite.
- **Collectivite (Commune/Region/Province)**: Entites geographiques existantes auxquelles un champ optionnel d'image banniere est ajoute.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un editeur peut ajouter, remplacer ou supprimer une image banniere sur une collectivite en moins de 30 secondes.
- **SC-002**: Le hero section s'affiche correctement sur la page publique dans 100% des cas ou une banniere est definie.
- **SC-003**: Le hero section est lisible (texte superpose) sur les deux modes (clair et sombre) sans intervention manuelle de l'utilisateur.
- **SC-004**: La page publique sans banniere ne montre aucune difference par rapport au comportement actuel.
- **SC-005**: L'image banniere s'affiche correctement sur les 3 formats d'ecran principaux (mobile, tablette, desktop) sans deformation ni debordement.

## Assumptions

- Le systeme d'upload existant (upload d'images via l'endpoint admin) est reutilise pour l'upload des bannieres. Pas de nouveau endpoint d'upload necessaire.
- Les contraintes de taille (5 Mo) et de format (JPEG, PNG, WebP, GIF) existantes sont suffisantes pour les images bannieres.
- Le hero section n'a pas besoin de sous-titre ou de texte additionnel au-dela du nom et du type de la collectivite.
- L'image banniere est un champ optionnel : les collectivites existantes sans banniere continuent de fonctionner sans changement.
- La suppression d'une collectivite n'implique pas la suppression physique du fichier image sur le serveur (coherent avec le comportement existant).
