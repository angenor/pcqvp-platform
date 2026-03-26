# Feature Specification: Back-Office Design Upgrade

**Feature Branch**: `012-backoffice-design-upgrade`
**Created**: 2026-03-22
**Status**: Draft
**Input**: User description: "S'inspirer du design back-office de l'ancienne plateforme collectivites_territoriales pour améliorer le design de la plateforme actuelle. Adopter les mêmes polices. Amélioration visuelle uniquement."

## Clarifications

### Session 2026-03-22

- Q: L'état déplié/replié de la sidebar doit-il persister entre les sessions ? → A: Oui, persistant — l'état est sauvegardé localement et restauré à chaque session
- Q: Les nouvelles polices (Barlow Condensed, Inter, JetBrains Mono) s'appliquent-elles uniquement au back-office ou à toute la plateforme ? → A: Global — les polices s'appliquent à toute la plateforme (admin + public), le redesign des composants/layout reste limité au back-office
- Q: Les pages admin existantes doivent-elles être refactorisées pour utiliser les nouveaux composants ? → A: Migration complète — toutes les pages admin existantes sont refactorisées avec les nouveaux composants

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Typographie professionnelle et design system (Priority: P1)

Un administrateur ou éditeur accède au back-office et voit immédiatement une typographie soignée et professionnelle : les titres utilisent la police Barlow Condensed en majuscules (style condensé et impactant), le corps de texte utilise Inter (lisible et moderne), et les données numériques/financières utilisent JetBrains Mono (alignement parfait des chiffres). Un design system centralisé avec variables CSS définit la palette officielle TI Madagascar (#3695d8 comme couleur primaire), les couleurs sémantiques, les espacements, les ombres et les z-index, avec support complet du mode sombre.

**Why this priority**: La typographie et le design system sont les fondations de toute amélioration visuelle. Sans ces bases, aucun composant ne peut être cohérent. C'est le changement le plus impactant avec le meilleur rapport effort/résultat.

**Independent Test**: Peut être testé en vérifiant visuellement que les polices et la palette de couleurs sont correctement appliquées sur toutes les pages admin, en mode clair et sombre.

**Acceptance Scenarios**:

1. **Given** un utilisateur accède à une page admin, **When** la page se charge, **Then** les titres sont en Barlow Condensed majuscules, le texte en Inter, et les données numériques en JetBrains Mono
2. **Given** le design system est en place, **When** un développeur inspecte les styles, **Then** toutes les couleurs utilisent des variables CSS centralisées avec la primaire #3695d8
3. **Given** le mode sombre est activé, **When** l'utilisateur consulte une page, **Then** la palette s'inverse automatiquement (fond gray-950, cartes gray-900, texte clair)
4. **Given** les polices web ne sont pas encore chargées, **When** la page s'affiche, **Then** des polices de fallback appropriées sont utilisées sans rupture visuelle

---

### User Story 2 - Layout admin professionnel (sidebar et header) (Priority: P1)

L'administrateur voit un layout professionnel avec : une sidebar fixe à gauche (256px dépliée, 64px repliée) avec des menus groupés par catégorie (Tableau de bord, Géographie, Comptes, Outils) et support de sous-menus avec animation ; un header fixe en haut avec fil d'Ariane, toggle mode sombre et menu utilisateur. Le tout est responsive avec un overlay mobile pour la sidebar.

**Why this priority**: Le layout est l'ossature de l'expérience utilisateur. Une navigation claire et un header informatif sont essentiels pour la productivité quotidienne des administrateurs.

**Independent Test**: Peut être testé en naviguant dans le back-office sur desktop, tablette et mobile, en dépliant/repliant la sidebar et en utilisant les éléments du header.

**Acceptance Scenarios**:

1. **Given** un administrateur accède au back-office sur desktop, **When** la page se charge, **Then** la sidebar est visible à gauche (256px) avec les menus groupés et le header fixe en haut
2. **Given** la sidebar est dépliée, **When** l'utilisateur clique sur le bouton de repli, **Then** la sidebar se réduit à 64px en affichant uniquement les icônes
3. **Given** un menu a des sous-éléments, **When** l'utilisateur clique dessus, **Then** les sous-menus se déploient avec une animation de chevron
4. **Given** un administrateur est sur mobile (<768px), **When** il appuie sur le hamburger menu, **Then** la sidebar s'ouvre en overlay
5. **Given** un administrateur est sur tablette (768-1024px), **When** la page se charge, **Then** la sidebar est repliée par défaut (64px)

---

### User Story 3 - Composants UI réutilisables (Priority: P2)

Les pages admin utilisent des composants UI cohérents et réutilisables : boutons avec variantes (primary, secondary, outline, ghost, danger), badges de statut colorés, cartes statistiques (KPI) avec valeur formatée et tendance optionnelle, modales de confirmation, et formulaires stylisés avec états d'erreur. Tous ces composants suivent le design system et supportent le mode sombre.

**Why this priority**: Les composants réutilisables garantissent la cohérence visuelle et accélèrent le développement futur. Ils dépendent du design system (P1) pour être cohérents.

**Independent Test**: Peut être testé en vérifiant chaque composant individuellement dans les pages admin existantes (boutons dans les formulaires, badges dans les listes, cartes sur le dashboard).

**Acceptance Scenarios**:

1. **Given** un bouton primary est affiché, **When** l'utilisateur le survole, **Then** le bouton change de teinte avec une transition fluide (200ms)
2. **Given** un badge de statut "publié" est affiché, **When** il est rendu, **Then** il utilise les couleurs sémantiques vertes avec support mode sombre
3. **Given** une carte statistique est affichée sur le dashboard, **When** elle présente une donnée, **Then** elle montre le libellé, la valeur formatée, l'icône et optionnellement la tendance
4. **Given** une modale de confirmation de suppression est ouverte, **When** elle apparaît, **Then** elle a un overlay sombre, un titre, un message et des boutons annuler/confirmer
5. **Given** un champ de formulaire a une erreur de validation, **When** l'erreur est affichée, **Then** le champ a une bordure rouge et un message d'erreur visible

---

### User Story 4 - Tables de données améliorées (Priority: P2)

Les listes admin (provinces, régions, communes, comptes, utilisateurs) utilisent un composant DataTable professionnel avec : barre de recherche intégrée, en-têtes triables, colonne d'actions (voir, éditer, supprimer), pagination, états de chargement (skeleton) et état vide avec message explicatif et bouton d'action.

**Why this priority**: Les tables sont le composant le plus utilisé dans le back-office pour la consultation et la gestion des données. Leur amélioration a un impact direct sur l'efficacité.

**Independent Test**: Peut être testé en chargeant une page de liste admin et en interagissant avec le tri, la recherche et la pagination.

**Acceptance Scenarios**:

1. **Given** une liste admin est affichée, **When** l'utilisateur tape dans la barre de recherche, **Then** les résultats sont filtrés
2. **Given** un en-tête de colonne est cliquable, **When** l'utilisateur clique dessus, **Then** les données sont triées avec un indicateur visuel (flèche asc/desc)
3. **Given** les données sont en cours de chargement, **When** la requête est en cours, **Then** un skeleton loader est affiché
4. **Given** aucune donnée ne correspond aux filtres, **When** la liste est vide, **Then** un état vide avec icône, message et bouton d'action est affiché

---

### User Story 5 - Icônes et finitions visuelles (Priority: P3)

Le back-office utilise FontAwesome comme système d'icônes cohérent pour la navigation (sidebar), les boutons d'action, les statuts et les indicateurs. Les transitions visuelles sont fluides, les bordures arrondies (12px) sont cohérentes, et les ombres subtiles renforcent la hiérarchie visuelle.

**Why this priority**: Les icônes et les finitions visuelles peaufinent l'expérience globale. Elles dépendent des composants (P2) pour être intégrées.

**Independent Test**: Peut être testé en vérifiant visuellement la présence et la cohérence des icônes et des finitions visuelles sur l'ensemble du back-office.

**Acceptance Scenarios**:

1. **Given** la sidebar est affichée, **When** l'utilisateur regarde les éléments de navigation, **Then** chaque élément a une icône descriptive à gauche du texte
2. **Given** un bouton d'action est affiché, **When** il est visible, **Then** il combine une icône pertinente et un texte descriptif
3. **Given** une carte ou un conteneur est affiché, **When** il est visible, **Then** il a des bordures arrondies (12px) et une ombre subtile

---

### Edge Cases

- Que se passe-t-il quand les polices web ne se chargent pas ? Le système utilise des polices de fallback : sans-serif pour Inter, condensed sans-serif pour Barlow Condensed, monospace pour JetBrains Mono
- Comment le design gère-t-il les très longs noms de menu dans la sidebar ? Troncature avec ellipsis en mode replié, texte complet en mode déplié
- Que se passe-t-il lors de la transition mode clair → sombre ? Transition fluide (200ms) sans flash de couleur
- Comment le layout s'adapte-t-il aux écrans entre 768px et 1024px ? Sidebar repliée par défaut, contenu à pleine largeur
- Que se passe-t-il si l'utilisateur a désactivé les animations (prefers-reduced-motion) ? Les transitions sont désactivées pour respecter la préférence système

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT charger et appliquer les polices Barlow Condensed (titres), Inter (corps de texte) et JetBrains Mono (données numériques) avec des polices de fallback appropriées — les polices s'appliquent globalement (admin + pages publiques)
- **FR-002**: Le système DOIT définir un design system centralisé avec des variables CSS pour les couleurs, espacements, ombres, rayons de bordure et z-index
- **FR-003**: La couleur primaire DOIT être #3695d8 (bleu TI Madagascar) avec une échelle complète de teintes (50 à 950)
- **FR-004**: Le système DOIT supporter un mode sombre complet avec une palette inversée cohérente pour toutes les variables CSS
- **FR-005**: La sidebar DOIT être fixe, repliable (256px → 64px), avec des menus groupés par catégorie, support de sous-menus animés, et persistance de l'état déplié/replié entre les sessions
- **FR-006**: Le header DOIT être fixe et contenir au minimum : fil d'Ariane, toggle mode sombre et menu utilisateur
- **FR-007**: Le système DOIT fournir un composant Button réutilisable avec les variantes : primary, secondary, outline, ghost, danger, success
- **FR-008**: Le système DOIT fournir un composant Badge pour les statuts avec les variantes : primary, success, warning, error, info
- **FR-009**: Le système DOIT fournir un composant StatCard pour les indicateurs KPI avec libellé, valeur, icône et tendance optionnelle
- **FR-010**: Le système DOIT fournir un composant DataTable avec recherche, tri, pagination, état de chargement (skeleton) et état vide
- **FR-011**: Le système DOIT fournir un composant Modal avec overlay, titre, contenu et boutons d'action
- **FR-012**: Le layout DOIT être responsive : sidebar en overlay sur mobile (<768px), repliée sur tablette (768-1024px), dépliée sur desktop (>1024px)
- **FR-013**: Les formulaires DOIVENT avoir un style cohérent avec labels, états de focus (ring primaire), états d'erreur (bordure rouge + message) et états désactivés
- **FR-014**: Le système DOIT utiliser FontAwesome comme bibliothèque d'icônes cohérente
- **FR-015**: Toutes les transitions visuelles DOIVENT être fluides (200-300ms ease-in-out) et respecter la préférence prefers-reduced-motion
- **FR-016**: Le système DOIT conserver toutes les fonctionnalités existantes intactes — seul le design visuel est modifié, aucune logique métier n'est changée
- **FR-017**: Toutes les pages admin existantes DOIVENT être refactorisées pour utiliser les nouveaux composants UI (migration complète, pas incrémentale)

### Key Entities

- **Design Tokens**: Variables CSS centralisées définissant couleurs, typographie, espacements, ombres et z-index — socle de tout le design system
- **Composants UI**: Bibliothèque de composants Vue réutilisables (Button, Badge, StatCard, DataTable, Modal, FormInput, etc.) — briques visuelles pour toutes les pages admin
- **Layout Admin**: Structure de page admin (sidebar + header + zone de contenu) — cadre de navigation pour l'ensemble du back-office

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% des pages admin utilisent la typographie cohérente (Barlow Condensed pour titres, Inter pour corps, JetBrains Mono pour données numériques)
- **SC-002**: Toutes les couleurs du back-office utilisent les variables CSS du design system centralisé (aucune couleur en dur dans les composants)
- **SC-003**: Le passage entre mode clair et sombre se fait sans flash visible et en moins de 300ms
- **SC-004**: La navigation admin est fonctionnelle et utilisable sur les trois breakpoints : mobile (<768px), tablette (768-1024px) et desktop (>1024px)
- **SC-005**: Tous les composants UI réutilisables (Button, Badge, StatCard, DataTable, Modal) sont intégrés dans au moins une page admin existante
- **SC-006**: Le temps de premier chargement des pages admin n'augmente pas de plus de 500ms par rapport à la version actuelle
- **SC-007**: Aucune fonctionnalité existante n'est cassée par les changements de design — formulaires, tables, actions et navigation fonctionnent comme avant

## Assumptions

- Les polices Barlow Condensed, Inter et JetBrains Mono sont disponibles via Google Fonts ou auto-hébergement
- L'ancienne plateforme `collectivites_territoriales/` sert uniquement de référence de design ; aucun code n'est copié
- Les polices s'appliquent globalement (admin + public) ; le redesign des composants et du layout est limité au back-office admin
- Les composants existants (RichContentEditor, RichContentRenderer, GeographySelector) sont conservés et adaptés au nouveau design system
- FontAwesome est ajouté comme nouvelle dépendance
