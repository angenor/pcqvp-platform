# Feature Specification: Interface publique de consultation des comptes administratifs

**Feature Branch**: `008-public-consultation`
**Created**: 2026-03-21
**Status**: Draft
**Input**: User description: "Feature 6 : Interface publique de consultation"

## Clarifications

### Session 2026-03-21

- Q: Comment naviguer entre les programmes dans l'onglet Depenses public ? → A: Sous-onglets par programme (un sous-onglet par programme), reproduisant le pattern de l'interface admin
- Q: Comment organiser l'onglet Recapitulatifs (recap recettes + recap depenses) ? → A: Vue unique scrollable avec recap recettes en haut et recap depenses en dessous, separes par un titre
- Q: Comment organiser les feuilles du fichier Excel exporte ? → A: Une feuille par section distincte : Recettes, une feuille par programme de depenses, Recap Recettes, Recap Depenses, Equilibre (reproduit la structure du document officiel)
- Q: Quel est l'etat initial des tableaux depliables au chargement ? → A: Tout replie, seules les lignes de niveau 1 sont visibles au chargement. Le visiteur deplie manuellement pour voir niv2 puis niv3
- Q: Comment separer visuellement les sections Fonctionnement et Investissement dans les tableaux ? → A: Lignes d'en-tete de section visibles ("FONCTIONNEMENT", "INVESTISSEMENT") separant les groupes de comptes, reproduisant la structure du document officiel

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consulter les comptes d'une collectivite via la page d'accueil (Priority: P1)

Un visiteur (citoyen, journaliste, chercheur) arrive sur la page d'accueil de la plateforme. Il voit le titre "Plateforme de suivi des revenus miniers des collectivites territoriales" et le logo de TI Madagascar. Il utilise le selecteur geographique pour choisir un type de collectivite (province, region ou commune), puis selectionne la collectivite souhaitee dans la hierarchie. Il est redirige vers la page de resultats de cette collectivite.

**Why this priority**: C'est le point d'entree unique de la plateforme publique. Sans cette page, aucun visiteur ne peut acceder aux donnees.

**Independent Test**: Peut etre teste en accedant a la page d'accueil, en selectionnant une commune dans le selecteur geographique et en verifiant la redirection vers la page de resultats.

**Acceptance Scenarios**:

1. **Given** un visiteur accede a la page d'accueil, **When** la page se charge, **Then** il voit le titre de la plateforme, le logo TI Madagascar et le selecteur geographique
2. **Given** le visiteur est sur la page d'accueil, **When** il selectionne un type de collectivite puis une collectivite, **Then** il est redirige vers la page de resultats de cette collectivite
3. **Given** aucun compte publie n'existe pour une collectivite, **When** le visiteur selectionne cette collectivite, **Then** la page de resultats affiche un message indiquant qu'aucune donnee n'est disponible
4. **Given** le visiteur est sur un appareil mobile, **When** il accede a la page d'accueil, **Then** la mise en page est adaptee et le selecteur geographique reste utilisable

---

### User Story 2 - Consulter les recettes et depenses d'une collectivite (Priority: P1)

Un visiteur arrive sur la page de resultats d'une collectivite. Il voit la description de la collectivite (contenu riche), un selecteur d'annee d'exercice et des onglets pour naviguer entre les differentes vues : Recettes, Depenses, Recapitulatifs, Equilibre. Le tableau de recettes affiche les lignes de comptes de maniere hierarchique (3 niveaux depliables). Les lignes de niveau 1 sont en gras avec un fond colore. Les colonnes affichees correspondent au template (budget primitif, OR admis, previsions definitives, etc.) avec les formules calculees (totaux, taux d'execution). Le tableau de depenses fonctionne de la meme maniere, ventile par programme.

**Why this priority**: L'affichage des tableaux de recettes et depenses est la fonctionnalite principale de la plateforme publique. C'est la raison d'etre du projet.

**Independent Test**: Peut etre teste en accedant a la page de resultats d'Andrafiabe 2023 et en verifiant que les tableaux affichent les bonnes valeurs avec les bons calculs.

**Acceptance Scenarios**:

1. **Given** un compte publie existe pour une collectivite, **When** le visiteur accede a la page de resultats, **Then** il voit la description de la collectivite, le selecteur d'annee et les onglets Recettes/Depenses/Recapitulatifs/Equilibre
2. **Given** le visiteur est sur l'onglet Recettes, **When** le tableau se charge, **Then** les lignes sont affichees en hierarchie depliable (niv1 > niv2 > niv3) avec les lignes niv1 en gras et fond colore
3. **Given** le visiteur consulte le tableau de recettes, **When** il deplie une ligne de niveau 1, **Then** les lignes de niveau 2 apparaissent, et il peut les deplier pour voir les lignes de niveau 3
4. **Given** le visiteur consulte le tableau de recettes, **When** les colonnes calculees sont affichees, **Then** les previsions definitives, le reste a recouvrer et le taux d'execution sont correctement calcules
5. **Given** le visiteur passe a l'onglet Depenses, **When** le tableau se charge, **Then** des sous-onglets sont affiches (un par programme) et chaque sous-onglet presente le tableau de depenses du programme avec la meme structure hierarchique depliable
6. **Given** plusieurs annees sont disponibles, **When** le visiteur change l'annee via le selecteur, **Then** les donnees du tableau se mettent a jour pour l'annee selectionnee
7. **Given** le tableau s'adapte a la structure du template, **When** l'admin a modifie le template (ajout/suppression de lignes), **Then** le tableau public reflete ces modifications

---

### User Story 3 - Consulter les recapitulatifs et l'equilibre budgetaire (Priority: P2)

Un visiteur souhaite avoir une vue synthetique des finances d'une collectivite. Via les onglets Recapitulatifs et Equilibre, il consulte : le recapitulatif des recettes (synthese par categorie de niveau 1 avec sous-totaux par section fonctionnement/investissement), le recapitulatif des depenses (croisement categories/programmes), et le tableau d'equilibre (recettes vs depenses avec resultat excedentaire ou deficitaire).

**Why this priority**: Les recapitulatifs et l'equilibre apportent une vue analytique essentielle, mais dependent des tableaux de base (P1).

**Independent Test**: Peut etre teste en accedant aux onglets Recapitulatifs et Equilibre pour Andrafiabe 2023 et en comparant les resultats avec le document officiel.

**Acceptance Scenarios**:

1. **Given** le visiteur est sur l'onglet Recapitulatifs, **When** la page se charge, **Then** une vue unique scrollable affiche le recapitulatif des recettes en haut (categories niv1 avec sous-totaux par section Fonctionnement/Investissement), puis le recapitulatif des depenses en dessous (categories en lignes, programmes en colonnes avec mandat, paiement et reste a payer), separes par un titre de section
3. **Given** le visiteur est sur l'onglet Equilibre, **When** le tableau se charge, **Then** les recettes et depenses sont presentees par section avec separation des operations reelles et d'ordre, et le resultat (excedent ou deficit) est affiche par section et au global

---

### User Story 4 - Exporter les donnees d'un compte (Priority: P3)

Un visiteur souhaite conserver ou partager les donnees consultees. Il peut imprimer la page via le bouton "Imprimer", telecharger un fichier Excel ou telecharger un fichier Word contenant les tableaux du compte administratif.

**Why this priority**: L'export est un complement utile mais non bloquant. Les donnees sont consultables en ligne sans export.

**Independent Test**: Peut etre teste en cliquant sur chaque bouton d'export et en verifiant que le fichier produit contient les bonnes donnees.

**Acceptance Scenarios**:

1. **Given** le visiteur consulte un compte, **When** il clique sur "Imprimer", **Then** la fenetre d'impression du navigateur s'ouvre avec une mise en page adaptee a l'impression
2. **Given** le visiteur consulte un compte, **When** il clique sur "Telecharger Excel", **Then** un fichier Excel est telecharge contenant les tableaux de recettes, depenses, recapitulatifs et equilibre
3. **Given** le visiteur consulte un compte, **When** il clique sur "Telecharger Word", **Then** un fichier Word est telecharge contenant les memes donnees sous forme de document structure

---

### User Story 5 - Referencement et partage des pages (Priority: P3)

Un visiteur ou un moteur de recherche accede a une page de collectivite. La page dispose de meta titres et descriptions dynamiques pour un bon referencement. Les URL sont claires et partageables.

**Why this priority**: Le SEO ameliore la decouverte de la plateforme mais n'est pas indispensable au fonctionnement.

**Independent Test**: Peut etre teste en verifiant les balises meta de la page de resultats et en testant le partage d'URL.

**Acceptance Scenarios**:

1. **Given** une page de collectivite existe, **When** un moteur de recherche ou un reseau social charge l'URL, **Then** le titre de la page contient le nom de la collectivite et l'annee d'exercice
2. **Given** un visiteur partage l'URL d'une page de collectivite, **When** le destinataire ouvre le lien, **Then** il arrive directement sur la bonne collectivite avec les bonnes donnees

---

### Edge Cases

- Que se passe-t-il si une collectivite n'a aucun compte publie ? La page de resultats affiche un message "Aucune donnee disponible pour cette collectivite" sans erreur
- Que se passe-t-il si l'annee selectionnee ne correspond a aucun compte publie ? Le systeme affiche les annees disponibles et un message invitant a selectionner une autre annee
- Que se passe-t-il si un compte est depublie alors qu'un visiteur le consulte ? La prochaine requete retourne une erreur 404 et la page affiche un message "Ces donnees ne sont plus disponibles"
- Que se passe-t-il si toutes les valeurs d'un tableau sont a zero ? Le tableau s'affiche normalement avec des zeros, sans masquer de lignes
- Que se passe-t-il si un programme de depenses est vide (aucune valeur saisie) ? Le programme apparait dans l'onglet Depenses avec des valeurs a zero
- Que se passe-t-il si la collectivite n'a pas de description (description_json vide) ? La section description est simplement omise de la page
- Que se passe-t-il si le visiteur accede a un type/id de collectivite inexistant dans l'URL ? La page affiche une erreur 404 claire
- Que se passe-t-il sur mobile avec un tableau de 9 colonnes ? Le tableau scrolle horizontalement avec un indicateur visuel de defilement

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le systeme DOIT fournir des points d'acces publics (sans authentification) pour consulter les comptes administratifs publies d'une collectivite
- **FR-002**: Le systeme DOIT fournir un point d'acces public retournant les donnees completes d'un compte publie pour une collectivite et une annee donnees, incluant les recettes, les depenses par programme, les colonnes calculees et les sommes hierarchiques
- **FR-003**: Le systeme DOIT fournir un point d'acces public retournant la description riche d'une collectivite (province, region ou commune)
- **FR-004**: Le systeme DOIT fournir un point d'acces public retournant la liste des annees d'exercice pour lesquelles des comptes publies existent pour une collectivite donnee
- **FR-005**: Les points d'acces publics NE DOIVENT retourner que les comptes dont le statut est "publie" ; les comptes en brouillon sont invisibles
- **FR-006**: Le systeme DOIT afficher une page d'accueil avec le titre "Plateforme de suivi des revenus miniers des collectivites territoriales", le logo TI Madagascar et le selecteur geographique existant
- **FR-007**: Le systeme DOIT afficher une page de resultats par collectivite avec un selecteur d'annee d'exercice, la description riche de la collectivite, et quatre onglets : Recettes, Depenses, Recapitulatifs, Equilibre
- **FR-008**: Le tableau de comptes DOIT afficher les lignes de maniere hierarchique depliable sur 3 niveaux, avec les lignes de niveau 1 en gras et fond colore. Au chargement, seules les lignes de niveau 1 sont visibles (tout replie) ; le visiteur deplie manuellement pour voir les niveaux 2 et 3. Des lignes d'en-tete de section ("FONCTIONNEMENT", "INVESTISSEMENT") DOIVENT separer visuellement les groupes de comptes, reproduisant la structure du document officiel
- **FR-009**: Le tableau de comptes DOIT adapter ses colonnes au type de tableau (recettes ou depenses) selon la structure definie dans le template
- **FR-010**: Le tableau DOIT afficher les formules calculees (totaux hierarchiques, previsions definitives, restes, taux d'execution) de maniere identique aux calculs du back-office
- **FR-011**: Le tableau DOIT s'adapter dynamiquement a la structure du template : si l'administrateur a modifie la structure (ajout ou suppression de lignes ou colonnes), le tableau public reflete ces modifications
- **FR-012**: L'onglet Recapitulatifs DOIT presenter le recapitulatif des recettes (synthese par categorie niv1 avec sous-totaux par section) et le recapitulatif des depenses (croisement categories/programmes avec mandat, paiement, reste a payer)
- **FR-013**: L'onglet Equilibre DOIT presenter les recettes et depenses par section (fonctionnement, investissement), en distinguant operations reelles et operations d'ordre, avec le resultat excedentaire ou deficitaire par section et au global
- **FR-014**: Le systeme DOIT offrir un bouton d'impression declenchant la fonction d'impression native du navigateur avec une mise en page adaptee
- **FR-015**: Le systeme DOIT permettre le telechargement des donnees au format Excel, organise en feuilles distinctes : une feuille Recettes, une feuille par programme de depenses, une feuille Recap Recettes, une feuille Recap Depenses et une feuille Equilibre (reproduisant la structure du document officiel)
- **FR-016**: Le systeme DOIT permettre le telechargement des donnees au format Word, sous forme de document structure
- **FR-017**: Les pages de collectivites DOIVENT inclure des meta titres et descriptions dynamiques bases sur le nom de la collectivite et l'annee d'exercice
- **FR-018**: L'interface DOIT etre responsive mobile-first : les tableaux scrollent horizontalement sur ecran etroit avec un indicateur visuel de defilement
- **FR-019**: Le systeme DOIT gerer le mode clair et le mode sombre sur l'ensemble de l'interface publique

### Key Entities

- **Consultation publique**: Vue en lecture seule d'un compte administratif publie, regroupe les donnees de recettes, depenses par programme, recapitulatifs et equilibre pour une collectivite et une annee donnees. Aucune donnee supplementaire n'est creee : il s'agit d'une projection des donnees existantes (comptes administratifs, lignes de recettes/depenses, templates).
- **Page de collectivite**: Page publique identifiee par le type et l'identifiant de la collectivite. Affiche la description riche, les annees disponibles et les tableaux de comptes. Sert de point d'entree pour le partage et le referencement.

## Assumptions

- Les comptes administratifs, templates, lignes de recettes et depenses sont deja geres par les Features 006 et 007
- La hierarchie geographique (provinces, regions, communes) avec descriptions riches est en place (Feature 005)
- Le composant GeographySelector existant (Feature 003) peut etre reutilise sur la page d'accueil publique
- Le composant RichContentRenderer existant peut etre reutilise pour afficher les descriptions de collectivites
- Les formules de calcul (colonnes derivees, sommes hierarchiques, recapitulatifs, equilibre) sont identiques a celles du back-office admin
- L'impression utilise window.print() avec une feuille de style dediee a l'impression (media print)
- Les exports Excel et Word sont generes cote serveur et telecharges par le visiteur
- La charte graphique TI Madagascar fournit le logo et les couleurs de reference pour la page d'accueil
- Les URL de pages publiques sont stables et partageables (pas de parametres de session)
- Le mode sombre/clair suit le meme mecanisme que le reste de l'application (classe CSS)

## Out of Scope

- Authentification ou comptes utilisateurs pour les visiteurs publics
- Commentaires ou annotations sur les comptes publics
- Comparaison inter-annuelle ou inter-collectivites
- Graphiques ou visualisations de donnees (uniquement des tableaux)
- Notification de mise a jour des donnees
- API publique documentee pour des consommateurs tiers
- Traduction multi-langue (le contenu est en francais uniquement)
- Recherche textuelle dans les comptes ou les lignes de comptes

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un visiteur peut selectionner une collectivite et consulter ses comptes en moins de 30 secondes depuis la page d'accueil
- **SC-002**: Les tableaux de comptes (jusqu'a 289 lignes) se chargent et affichent tous les calculs en moins de 3 secondes
- **SC-003**: Les valeurs affichees dans les tableaux publics sont identiques a celles du back-office admin pour le meme compte (zero ecart)
- **SC-004**: L'interface publique est utilisable sur mobile (ecran 375px de large) sans perte d'information : tous les tableaux sont consultables par defilement horizontal
- **SC-005**: Les meta titres et descriptions sont presents et pertinents sur 100% des pages de collectivites
- **SC-006**: Les fichiers Excel et Word telecharges contiennent l'integralite des donnees du compte consulte avec les memes valeurs que l'affichage en ligne
