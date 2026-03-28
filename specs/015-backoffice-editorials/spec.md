# Feature Specification: Section Éditoriaux du Backoffice

**Feature Branch**: `015-backoffice-editorials`
**Created**: 2026-03-27
**Status**: Draft
**Input**: User description: "Créer une section éditoriaux dans le backOffice qui permet de modifier le header (titre, sous-titre, description), le corps de la page d'accueil (contenu riche via éditeur), et le footer (À propos, Contact, Ressources)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gestion de la Hero Section de la page d'accueil (Priority: P1)

Un administrateur souhaite personnaliser les textes affichés dans la hero section de la page d'accueil publique. Il se rend dans la section "Éditoriaux" du backoffice, onglet "Hero Section", et modifie le titre principal ("Plateforme de suivi..."), le sous-titre ("Collectivités Territoriales...") et la description ("Publiez Ce Que Vous Payez..."). Après enregistrement, les modifications sont immédiatement visibles sur la page d'accueil.

**Why this priority**: La hero section est le premier élément visible par les visiteurs. Pouvoir la modifier sans intervention technique est essentiel pour la communication de la plateforme.

**Independent Test**: Peut être testé en modifiant les trois champs de la hero section dans le backoffice et en vérifiant leur affichage sur la page d'accueil publique.

**Acceptance Scenarios**:

1. **Given** un administrateur connecté au backoffice, **When** il accède à la section "Éditoriaux" onglet "Hero Section", **Then** il voit les valeurs actuelles du titre, sous-titre et description de la hero section.
2. **Given** un administrateur sur l'onglet Hero Section, **When** il modifie le titre et clique sur "Enregistrer", **Then** la modification est sauvegardée et un message de confirmation s'affiche.
3. **Given** une hero section modifiée dans le backoffice, **When** un visiteur accède à la page d'accueil, **Then** il voit les textes mis à jour.
4. **Given** un administrateur sur l'onglet Hero Section, **When** il tente d'enregistrer un titre vide, **Then** le système affiche un message d'erreur et ne sauvegarde pas.

---

### User Story 2 - Gestion du contenu riche du corps de page (Priority: P1)

Un administrateur souhaite enrichir la page d'accueil avec une présentation contextuelle de la plateforme. Il accède à la section "Éditoriaux" et utilise l'éditeur de contenu riche pour insérer des titres, textes, images, tableaux, citations et liens. Le contenu est rendu sur la page d'accueil dans une section dédiée.

**Why this priority**: Le contenu contextuel est le coeur informatif de la page d'accueil. Sa gestion dynamique évite toute dépendance technique pour les mises à jour de contenu.

**Independent Test**: Peut être testé en créant du contenu riche (texte + image + lien) dans l'éditeur et en vérifiant le rendu fidèle sur la page d'accueil.

**Acceptance Scenarios**:

1. **Given** un administrateur sur la section Éditoriaux, **When** il accède à l'onglet "Corps de page", **Then** il voit un éditeur de contenu riche avec les outils disponibles (titres, texte, images, tableaux, citations, liens).
2. **Given** un éditeur de contenu riche ouvert, **When** l'administrateur insère un titre, un paragraphe, une image et un tableau, **Then** chaque élément est correctement ajouté et prévisualisable.
3. **Given** du contenu riche enregistré, **When** un visiteur charge la page d'accueil, **Then** la section de présentation contextuelle affiche le contenu avec un rendu fidèle (mise en forme, images, liens cliquables).
4. **Given** un administrateur revenant sur la section corps de page, **When** il ouvre l'éditeur, **Then** le contenu précédemment sauvegardé est correctement rechargé et éditable.

---

### User Story 3 - Gestion du Footer (Priority: P2)

Un administrateur souhaite modifier les informations du pied de page : les sections "À propos", "Contact" et "Ressources". Il se rend dans la section "Éditoriaux" du backoffice, modifie les contenus de chaque section du footer, et les changements sont reflétés sur toutes les pages du site.

**Why this priority**: Le footer est visible sur toutes les pages et contient des informations importantes, mais il change moins fréquemment que le header et le corps de page.

**Independent Test**: Peut être testé en modifiant le texte de la section "À propos" dans le backoffice et en vérifiant sa mise à jour dans le footer sur n'importe quelle page du site.

**Acceptance Scenarios**:

1. **Given** un administrateur sur la section Éditoriaux, **When** il accède à l'onglet "Footer", **Then** il voit les contenus actuels des sections "À propos", "Contact" et "Ressources".
2. **Given** un administrateur modifiant la section "Contact", **When** il enregistre ses modifications, **Then** les nouvelles informations de contact apparaissent dans le footer de toutes les pages.
3. **Given** un administrateur modifiant la section "Ressources", **When** il ajoute un nouveau lien, **Then** le lien apparaît dans la section Ressources du footer et est cliquable.

---

### Edge Cases

- Que se passe-t-il si un administrateur modifie la hero section pendant qu'un autre administrateur modifie le même champ simultanément ? L'enregistrement le plus récent prévaut et un avertissement est affiché.
- Que se passe-t-il si l'image insérée dans le contenu riche est supprimée du serveur ? Un placeholder ou message d'erreur élégant s'affiche à la place de l'image manquante.
- Que se passe-t-il si aucun contenu éditorial n'a encore été défini ? Des valeurs par défaut sont affichées sur la page d'accueil.
- Comment le système gère-t-il un contenu riche très volumineux ? Le système accepte le contenu dans une limite raisonnable et affiche un avertissement si la taille est excessive.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT fournir une section "Éditoriaux" dans le backoffice accessible aux administrateurs et éditeurs.
- **FR-002**: Le système DOIT permettre la modification du titre principal de la hero section de la page d'accueil.
- **FR-003**: Le système DOIT permettre la modification du sous-titre de la hero section de la page d'accueil.
- **FR-004**: Le système DOIT permettre la modification de la description de la hero section de la page d'accueil.
- **FR-005**: Le système DOIT valider que le titre de la hero section n'est pas vide avant sauvegarde.
- **FR-015**: Le système DOIT organiser la section Éditoriaux en une page unique avec trois onglets : "Hero Section", "Corps de page" et "Footer".
- **FR-006**: Le système DOIT fournir un éditeur de contenu riche pour le corps de la page d'accueil supportant : titres, textes, images, tableaux, citations et liens.
- **FR-007**: Le système DOIT sauvegarder le contenu riche de manière structurée pour un rendu fidèle côté public.
- **FR-008**: Le système DOIT afficher le contenu éditorial (hero section, corps, footer) sur la page d'accueil publique.
- **FR-009**: Le système DOIT permettre la modification du contenu de la section "À propos" du footer via un éditeur de texte riche.
- **FR-010**: Le système DOIT permettre la modification de la section "Contact" du footer via des champs structurés (email, téléphone, adresse).
- **FR-011**: Le système DOIT permettre la gestion de la section "Ressources" du footer sous forme de liste de liens (titre + URL), avec possibilité d'ajouter, modifier et supprimer des entrées.
- **FR-012**: Le système DOIT afficher les contenus du footer mis à jour sur toutes les pages du site.
- **FR-013**: Le système DOIT afficher des valeurs par défaut si aucun contenu éditorial n'a été défini.
- **FR-014**: Le système DOIT restreindre l'accès à la section Éditoriaux aux utilisateurs ayant le rôle administrateur ou éditeur.

### Key Entities

- **EditorialContent**: Représente un bloc de contenu éditorial. Attributs principaux : identifiant de section (hero_title, hero_subtitle, hero_description, body_content, footer_about), contenu (texte simple ou contenu riche structuré), date de dernière modification, auteur de la dernière modification.
- **ContactInfo**: Informations de contact structurées du footer. Attributs : email, téléphone, adresse, date de dernière modification.
- **ResourceLink**: Lien dans la section Ressources du footer. Attributs : titre, URL, ordre d'affichage, date de dernière modification.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un administrateur peut modifier et publier les textes de la hero section en moins de 2 minutes.
- **SC-002**: Le contenu riche créé dans l'éditeur s'affiche sur la page d'accueil avec un rendu fidèle à 100% (tous les types de blocs supportés sont correctement rendus).
- **SC-003**: Les modifications du footer sont visibles sur toutes les pages du site dans un délai de moins de 5 secondes après enregistrement.
- **SC-004**: 100% des champs éditoriaux existants sont correctement rechargés lors de la réouverture de l'éditeur (aucune perte de données).
- **SC-005**: La page d'accueil affiche des valeurs par défaut cohérentes lorsqu'aucun contenu éditorial n'a été défini.

## Clarifications

### Session 2026-03-27

- Q: Quel format pour chaque section du footer ? → A: Mixte — "À propos" en texte riche, "Contact" en champs structurés (email, téléphone, adresse), "Ressources" en liste de liens (titre + URL).
- Q: Organisation de la page Éditoriaux ? → A: Page unique avec onglets (tabs) : Hero Section, Corps de page, Footer.
- Q: Terminologie "Header" ? → A: Il s'agit en fait de la "Hero Section" de la page d'accueil, pas du header du site.

## Assumptions

- Les rôles `admin` et `editor` existants dans le système d'authentification seront réutilisés pour contrôler l'accès à la section Éditoriaux.
- L'éditeur de contenu riche (EditorJS) déjà présent dans le projet sera réutilisé pour l'édition du corps de page.
- Le composant de rendu de contenu riche (RichContentRenderer) existant sera réutilisé pour l'affichage public.
- La section "À propos" du footer utilise un éditeur de texte riche, "Contact" utilise des champs structurés (email, téléphone, adresse), et "Ressources" utilise une liste de liens (titre + URL).
- Le contenu éditorial est global (un seul jeu de contenu pour tout le site, pas de contenu par langue ou par région).
- Les modifications sont publiées immédiatement après enregistrement (pas de workflow de validation/publication).
