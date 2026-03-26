# Feature Specification: Navigation Géographique Admin en Grille

**Feature Branch**: `013-admin-geography-grid`
**Created**: 2026-03-26
**Status**: Draft
**Input**: Refonte des pages admin Provinces, Régions et Communes : affichage en grille, navigation hiérarchique drill-down (Province → Régions → Communes), tri/filtrage, et ajout de la section "Données Financières" pour les régions avec lien vers les comptes administratifs.

## Clarifications

### Session 2026-03-26

- Q: Le drill-down Province → Régions → Communes se fait-il sur la même page (état local) ou via navigation URL (nouvelles routes) ? → A: Navigation par URL — cliquer sur une province navigue vers `/admin/geography/provinces/:id/regions`, cliquer sur une région navigue vers une route dédiée pour ses communes
- Q: Comment accéder aux actions CRUD (éditer, supprimer) depuis les cartes en grille ? → A: Menu contextuel (⋮) — un bouton trois points sur chaque carte ouvre un menu déroulant avec les actions
- Q: Les grilles doivent-elles être paginées ou tout charger d'un coup ? → A: Tout charger sans pagination — seules certaines entités seront utilisées, la recherche textuelle suffit pour filtrer

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Affichage en grille des provinces avec navigation drill-down (Priority: P1)

Un administrateur accède à la page "Provinces" du back-office et voit la liste des provinces affichée sous forme de grille de cartes (et non plus un tableau). Chaque carte affiche le nom de la province et son code. En cliquant sur une carte de province, l'administrateur voit la liste des régions de cette province s'afficher (toujours en grille). En cliquant sur une région, il voit la liste des communes de cette région. Un fil d'Ariane ou un système de navigation permet de revenir aux niveaux supérieurs.

**Why this priority**: L'affichage en grille avec navigation drill-down est le coeur de la demande. Il remplace l'affichage tableau actuel et offre une exploration hiérarchique intuitive.

**Independent Test**: Naviguer sur la page Provinces, cliquer sur une province, vérifier que ses régions apparaissent en grille, cliquer sur une région, vérifier que ses communes apparaissent.

**Acceptance Scenarios**:

1. **Given** un administrateur accède à `/admin/geography/provinces`, **When** la page se charge, **Then** les provinces sont affichées sous forme de cartes dans une grille responsive
2. **Given** l'administrateur clique sur une carte de province, **When** le navigateur navigue vers `/admin/geography/provinces/:id/regions`, **Then** la liste des régions de cette province s'affiche en grille avec le nom de la province sélectionnée visible
3. **Given** l'administrateur visualise les régions d'une province, **When** il clique sur une carte de région, **Then** le navigateur navigue vers la route des communes de cette région et les affiche en grille
4. **Given** l'administrateur est au niveau des communes, **When** il souhaite revenir en arrière, **Then** un fil d'Ariane lui permet de remonter au niveau régions ou provinces via les URLs correspondantes

---

### User Story 2 - Affichage en grille des régions avec tri par province (Priority: P1)

Un administrateur accède à la page "Régions" et voit toutes les régions affichées en grille. Un filtre/sélecteur de province est disponible en haut de page pour filtrer les régions par province, facilitant la recherche. En cliquant sur une carte de région, l'administrateur voit les communes de cette région.

**Why this priority**: La page Régions est indépendante de la page Provinces et doit offrir son propre accès avec filtrage par province.

**Independent Test**: Accéder à la page Régions, vérifier l'affichage grille, sélectionner une province dans le filtre, vérifier que seules les régions de cette province sont affichées.

**Acceptance Scenarios**:

1. **Given** un administrateur accède à `/admin/geography/regions`, **When** la page se charge, **Then** toutes les régions sont affichées en grille de cartes
2. **Given** la page Régions est affichée, **When** l'administrateur sélectionne une province dans le filtre, **Then** seules les régions de cette province sont affichées
3. **Given** l'administrateur visualise les régions, **When** il clique sur une carte de région, **Then** les communes de cette région s'affichent en grille
4. **Given** le filtre province est actif, **When** l'administrateur réinitialise le filtre, **Then** toutes les régions sont à nouveau affichées

---

### User Story 3 - Section "Données Financières" sur les régions (Priority: P1)

Sur la page Régions (ou dans la vue région), l'administrateur voit une section "Données Financières" indiquant que les régions ont des comptes administratifs par année d'exercice. Un bouton ou lien "Voir les comptes" est disponible pour chaque région, redirigeant vers la liste des comptes administratifs filtrée pour cette région. L'administrateur peut également soumettre un nouveau compte administratif pour une région depuis cette section.

**Why this priority**: L'intégration des données financières dans la navigation géographique est une fonctionnalité métier essentielle demandée explicitement.

**Independent Test**: Accéder à la page Régions, vérifier la présence de la section "Données Financières", cliquer sur "Voir les comptes" et vérifier la redirection vers les comptes filtrés.

**Acceptance Scenarios**:

1. **Given** un administrateur visualise une région (via la page Régions ou le drill-down), **When** la carte ou la vue de la région est affichée, **Then** une section ou un lien "Données Financières" est visible
2. **Given** la section "Données Financières" est visible, **When** l'administrateur clique sur "Voir les comptes", **Then** il est redirigé vers la page des comptes administratifs filtrée pour cette région (type=region, collectivite_id=region.id)
3. **Given** l'administrateur est dans la section "Données Financières", **When** il souhaite soumettre un nouveau compte, **Then** un bouton "Soumettre un compte" le redirige vers le formulaire de création pré-rempli avec la région

---

### User Story 4 - Page Communes avec tri par région et province (Priority: P2)

Un administrateur accède à la page "Communes" et voit les communes affichées en grille. Des filtres par province et par région (en cascade) sont disponibles en haut de page pour faciliter la recherche. Le tri par province filtre d'abord les régions disponibles, puis le tri par région filtre les communes.

**Why this priority**: La page Communes avec filtrage en cascade est mentionnée comme déjà partiellement disponible. Il s'agit d'adapter l'affichage au format grille et de s'assurer que le filtrage fonctionne.

**Independent Test**: Accéder à la page Communes, vérifier l'affichage grille, sélectionner une province puis une région, vérifier le filtrage en cascade.

**Acceptance Scenarios**:

1. **Given** un administrateur accède à `/admin/geography/communes`, **When** la page se charge, **Then** les communes sont affichées en grille de cartes
2. **Given** la page Communes est affichée, **When** l'administrateur sélectionne une province, **Then** le filtre "Région" se met à jour pour ne montrer que les régions de cette province
3. **Given** un filtre région est sélectionné, **When** le filtrage s'applique, **Then** seules les communes de cette région sont affichées
4. **Given** des filtres sont actifs, **When** l'administrateur les réinitialise, **Then** toutes les communes sont à nouveau affichées

---

### Edge Cases

- Que se passe-t-il quand une province n'a aucune région ? Un état vide est affiché avec un message explicatif ("Aucune région pour cette province") et un bouton pour créer une région
- Que se passe-t-il quand une région n'a aucune commune ? Un état vide est affiché avec un message similaire et un bouton de création
- Que se passe-t-il quand une région n'a aucun compte administratif ? La section "Données Financières" affiche un message "Aucun compte" avec un bouton pour en soumettre un
- Comment la grille s'adapte-t-elle sur mobile ? La grille passe de 3-4 colonnes sur desktop à 2 colonnes sur tablette et 1 colonne sur mobile
- Que se passe-t-il avec un très grand nombre de communes (recherche) ? Toutes les entités sont chargées d'un coup (pas de pagination). La barre de recherche textuelle et les filtres permettent d'affiner les résultats côté client

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Les pages admin Provinces, Régions et Communes DOIVENT afficher les entités sous forme de grille de cartes responsive au lieu d'un tableau
- **FR-002**: Chaque carte DOIT afficher au minimum le nom, le code de l'entité géographique et un menu contextuel (⋮) pour les actions CRUD
- **FR-003**: Sur la page Provinces, cliquer sur une carte de province DOIT naviguer vers une route dédiée (`/admin/geography/provinces/:id/regions`) affichant les régions de cette province en grille, avec possibilité de continuer vers les communes
- **FR-004**: Sur la page Régions, un filtre par province DOIT être disponible pour trier/filtrer les régions affichées
- **FR-005**: Sur la page Régions, cliquer sur une carte de région DOIT afficher les communes de cette région en grille
- **FR-006**: Sur la page Communes, des filtres en cascade (province → région) DOIVENT être disponibles pour faciliter la recherche
- **FR-007**: Chaque carte de région DOIT inclure un lien ou bouton "Voir les comptes" redirigeant vers les comptes administratifs de cette région
- **FR-008**: Depuis la vue d'une région, l'administrateur DOIT pouvoir soumettre un nouveau compte administratif pré-rempli avec la région sélectionnée
- **FR-009**: Un fil d'Ariane DOIT permettre de remonter dans la hiérarchie lors du drill-down (liens vers les routes parentes)
- **FR-010**: La grille DOIT être responsive : 3-4 colonnes sur desktop, 2 sur tablette, 1 sur mobile
- **FR-011**: Un état vide explicatif DOIT être affiché lorsqu'aucune entité enfant n'existe (avec option de création)
- **FR-012**: Les fonctionnalités CRUD existantes (création, édition, suppression) DOIVENT rester accessibles depuis les pages en grille via un menu contextuel (⋮) sur chaque carte, proposant les actions "Éditer" et "Supprimer"
- **FR-013**: Une barre de recherche textuelle DOIT être disponible sur chaque page pour filtrer les cartes par nom (filtrage côté client, toutes les entités sont chargées sans pagination)

### Key Entities

- **Province**: Entité géographique de premier niveau — contient des régions, affichée en grille sur la page admin dédiée
- **Région**: Entité géographique de second niveau — appartient à une province, contient des communes, possède des comptes administratifs par année d'exercice
- **Commune**: Entité géographique de troisième niveau — appartient à une région, niveau le plus fin de la hiérarchie
- **Compte Administratif**: Document financier annuel associé à une collectivité (province, région ou commune) — accessible depuis la section "Données Financières" des régions

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% des pages admin géographiques (Provinces, Régions, Communes) utilisent un affichage en grille de cartes au lieu de tableaux
- **SC-002**: La navigation drill-down (Province → Régions → Communes) est fonctionnelle en 2 clics maximum depuis la page Provinces
- **SC-003**: Le filtrage par province sur la page Régions réduit les résultats aux seules régions de la province sélectionnée
- **SC-004**: Le lien "Voir les comptes" sur chaque région redirige correctement vers les comptes administratifs filtrés pour cette région
- **SC-005**: Le filtrage en cascade (province → région) sur la page Communes fonctionne sans rechargement de page
- **SC-006**: La grille est utilisable sur les trois breakpoints (mobile, tablette, desktop) sans perte de fonctionnalité
- **SC-007**: Les opérations CRUD existantes (créer, modifier, supprimer) restent fonctionnelles sur les trois entités géographiques

## Assumptions

- Les API admin existantes (`/api/admin/provinces`, `/api/admin/regions`, `/api/admin/communes`) fournissent déjà les données nécessaires pour l'affichage en grille
- L'API `/api/admin/regions?province_id=...` supporte déjà le filtrage par province
- L'API `/api/admin/communes?region_id=...` supporte déjà le filtrage par région
- Le système de comptes administratifs existant supporte déjà le filtrage par `collectivite_type=region` et `collectivite_id`
- Le design des cartes suivra le design system défini dans la feature 012-backoffice-design-upgrade
- La navigation drill-down utilise des routes URL dédiées (ex: `/admin/geography/provinces/:id/regions`) permettant le partage de liens et l'historique du navigateur
