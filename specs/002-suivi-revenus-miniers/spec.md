# Feature Specification: Plateforme de suivi des revenus miniers des collectivités territoriales

**Feature Branch**: `002-suivi-revenus-miniers`
**Created**: 2026-03-20
**Status**: Draft
**Input**: Plateforme de suivi des revenus miniers des collectivités territoriales pour PCQVP Madagascar / Transparency International - Initiative Madagascar

## Clarifications

### Session 2026-03-20

- Q: Que se passe-t-il pour les comptes existants lorsqu'un template est modifié ? → A: Versionnement — chaque compte garde le template de sa version de saisie, les nouveaux comptes utilisent le template actuel.
- Q: Un compte administratif est-il visible immédiatement après saisie ou doit-il être validé ? → A: Workflow brouillon/publié — l'éditeur enregistre en brouillon, un administrateur valide et publie.
- Q: Un éditeur peut-il saisir pour toute collectivité ou est-il restreint ? → A: Affectation par région — un éditeur est assigné à une ou plusieurs régions (et leurs communes).
- Q: Peut-il exister plusieurs comptes pour la même collectivité et année ? → A: Non, unicité stricte — un seul compte par couple (collectivité, année).
- Q: Le citoyen peut-il comparer les comptes sur plusieurs années ? → A: Mono-année avec navigation — affichage d'une année avec sélecteur pour basculer rapidement entre années.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultation des comptes administratifs d'une collectivité (Priority: P1)

Un citoyen accède à la plateforme pour consulter les comptes administratifs (recettes et dépenses) d'une collectivité territoriale bénéficiaire de revenus miniers. Il sélectionne une Province, puis une Région, puis optionnellement une Commune via des menus déroulants hiérarchiques. Après validation, il visualise les tableaux détaillés des comptes pour l'année d'exercice sélectionnée : recettes (3 niveaux hiérarchiques), dépenses par programme, récapitulatifs et tableau d'équilibre.

**Why this priority**: C'est la raison d'être de la plateforme. Sans cette fonctionnalité, aucune valeur de transparence n'est délivrée aux citoyens.

**Independent Test**: Peut être testé en naviguant sur la plateforme, en sélectionnant une collectivité et en vérifiant l'affichage correct des tableaux de comptes administratifs avec données de test.

**Acceptance Scenarios**:

1. **Given** un citoyen sur la page d'accueil, **When** il sélectionne une Province, **Then** le menu Région se peuple avec les régions de cette province
2. **Given** une Province et une Région sélectionnées, **When** il sélectionne une Commune et clique "OK", **Then** les tableaux des comptes administratifs de la commune s'affichent
3. **Given** une Province et une Région sélectionnées sans Commune, **When** il clique "OK", **Then** les tableaux des comptes administratifs de la région s'affichent
4. **Given** les tableaux affichés, **When** le citoyen consulte le tableau des recettes, **Then** il voit les comptes hiérarchiques (Niv1, Niv2, Niv3) avec les colonnes Budget Primitif, Additionnel, Modifications, Prévisions, OR Admis, Recouvrement, Reste à Recouvrer et Taux
5. **Given** les tableaux affichés, **When** le citoyen consulte le tableau des dépenses, **Then** il voit les comptes par programme avec les colonnes Budget, Engagement, Mandatement, Paiement, Reste à Payer et Taux
6. **Given** les tableaux affichés, **When** le citoyen consulte le tableau d'équilibre, **Then** il voit les dépenses et recettes côte à côte
7. **Given** des comptes de niveau 2 sous un compte de niveau 1, **When** les tableaux sont affichés, **Then** la valeur du Niv1 est égale à la somme de ses Niv2
8. **Given** un tableau de recettes, **When** les colonnes Prévisions et OR Admis ont des valeurs, **Then** le Taux affiché est OR / Prévisions et le Reste est OR - Recouvrement
9. **Given** les tableaux d'une collectivité affichés pour une année, **When** le citoyen utilise le sélecteur d'année pour choisir une autre année, **Then** les tableaux se mettent à jour avec les données de l'année sélectionnée sans revenir à la page d'accueil

---

### User Story 2 - Gestion de la géographie hiérarchique (Priority: P2)

Un administrateur gère l'arborescence géographique de Madagascar (Provinces, Régions, Communes) depuis le back-office. Il peut créer, modifier, supprimer et réordonner les entités géographiques. Chaque entité peut avoir une description en texte riche visible sur le front-office.

**Why this priority**: Sans la structure géographique, aucune donnée de comptes ne peut être associée à une collectivité.

**Independent Test**: Peut être testé en se connectant au back-office, en créant une province, une région rattachée, et une commune rattachée, puis en vérifiant qu'elles apparaissent dans les menus déroulants du front-office.

**Acceptance Scenarios**:

1. **Given** un administrateur connecté, **When** il crée une Province avec un nom et une description, **Then** la province apparaît dans la liste et dans le menu déroulant du front-office
2. **Given** une Province existante, **When** l'administrateur crée une Région rattachée, **Then** la région apparaît sous cette province dans la hiérarchie
3. **Given** une Région existante, **When** l'administrateur crée une Commune rattachée, **Then** la commune apparaît sous cette région
4. **Given** plusieurs entités au même niveau, **When** l'administrateur les réordonne, **Then** l'ordre est respecté dans les menus déroulants du front-office
5. **Given** une entité géographique sans comptes administratifs associés, **When** l'administrateur la supprime, **Then** elle disparaît de la hiérarchie
6. **Given** une entité géographique avec des comptes associés, **When** l'administrateur tente de la supprimer, **Then** le système lui demande confirmation et l'avertit de la perte de données associées

---

### User Story 3 - Saisie des comptes administratifs (Priority: P3)

Un éditeur ou administrateur saisit les comptes administratifs d'une collectivité pour une année d'exercice donnée. Il remplit les tableaux de recettes et de dépenses par programme selon la structure définie par les templates. Les formules de calcul (totaux, taux, restes) se calculent automatiquement.

**Why this priority**: Les données de comptes sont le contenu principal de la plateforme. Sans saisie, il n'y a rien à consulter.

**Independent Test**: Peut être testé en saisissant un jeu complet de comptes pour une commune et une année, puis en vérifiant leur affichage correct côté front-office.

**Acceptance Scenarios**:

1. **Given** un éditeur connecté, **When** il sélectionne une collectivité et une année, **Then** il accède au formulaire de saisie des comptes administratifs
2. **Given** le formulaire de saisie des recettes, **When** l'éditeur remplit les valeurs des comptes de niveau 2 et 3, **Then** les totaux de niveau 1 se calculent automatiquement
3. **Given** le formulaire de saisie des dépenses, **When** l'éditeur ajoute un nouveau programme (au-delà des 3 par défaut), **Then** le programme apparaît avec sa propre structure de comptes
4. **Given** des valeurs saisies dans les recettes, **When** Prévisions et OR Admis sont renseignés, **Then** le Taux (OR/Prévisions) et le Reste à Recouvrer (OR - Recouvrement) se calculent automatiquement
5. **Given** un compte administratif complété, **When** l'éditeur enregistre la saisie, **Then** le compte est sauvegardé avec le statut "brouillon"
6. **Given** un compte en statut "brouillon", **When** un administrateur le valide et publie, **Then** les données deviennent consultables sur le front-office
7. **Given** un compte en statut "publié", **When** un administrateur le dépublie, **Then** les données ne sont plus visibles sur le front-office
8. **Given** une Région sélectionnée, **When** l'éditeur crée un compte administratif, **Then** le champ Commune est optionnel (les régions peuvent avoir leurs propres comptes)

---

### User Story 4 - Téléchargement et impression des données (Priority: P4)

Un citoyen souhaite exporter les tableaux de comptes administratifs pour les partager, les analyser hors-ligne ou les imprimer. Il peut télécharger les données en format Excel ou Word, ou utiliser la fonction d'impression.

**Why this priority**: L'export renforce la transparence en permettant la diffusion des données au-delà de la plateforme.

**Independent Test**: Peut être testé en affichant les comptes d'une collectivité puis en téléchargeant le fichier Excel et Word, et en vérifiant que le contenu correspond aux tableaux affichés.

**Acceptance Scenarios**:

1. **Given** des tableaux de comptes affichés, **When** le citoyen clique sur "Télécharger Excel", **Then** un fichier Excel contenant tous les tableaux est téléchargé
2. **Given** des tableaux de comptes affichés, **When** le citoyen clique sur "Télécharger Word", **Then** un fichier Word contenant tous les tableaux est téléchargé
3. **Given** des tableaux de comptes affichés, **When** le citoyen clique sur "Imprimer", **Then** la mise en page d'impression est optimisée pour les tableaux
4. **Given** un fichier Excel téléchargé, **When** il est ouvert, **Then** les formules de calcul sont préservées et les données sont identiques à l'affichage web

---

### User Story 5 - Administration des templates de tableaux (Priority: P5)

Un administrateur configure la structure des tableaux de comptes (lignes et colonnes) sans intervention technique. Il définit les comptes hiérarchiques, les colonnes, et les formules de calcul via le back-office. Ces templates servent de modèle standardisé pour la saisie et l'affichage.

**Why this priority**: La modulabilité des tableaux est une exigence clé pour s'adapter aux évolutions réglementaires sans développement.

**Independent Test**: Peut être testé en modifiant la structure d'un tableau (ajout d'une ligne de compte, modification d'une colonne), puis en vérifiant que la saisie et l'affichage reflètent les changements.

**Acceptance Scenarios**:

1. **Given** un administrateur dans le back-office, **When** il accède à la gestion des templates, **Then** il voit la structure actuelle des tableaux de recettes et dépenses
2. **Given** un template de recettes, **When** l'administrateur ajoute un nouveau compte de niveau 2 sous un Niv1 existant, **Then** le compte apparaît dans la structure et dans les formulaires de saisie
3. **Given** un template de dépenses, **When** l'administrateur modifie le libellé d'une colonne, **Then** le changement se reflète dans l'affichage front-office et les exports
4. **Given** un template, **When** l'administrateur définit une formule de calcul (ex: Taux = Colonne A / Colonne B), **Then** la formule s'applique automatiquement à la saisie et à l'affichage

---

### User Story 6 - Gestion des utilisateurs et des rôles (Priority: P6)

Un administrateur gère les comptes utilisateurs du back-office. Deux rôles existent : administrateur (accès complet) et éditeur (saisie des données uniquement). L'administrateur peut créer, modifier et désactiver des comptes.

**Why this priority**: Nécessaire pour sécuriser l'accès au back-office et déléguer la saisie.

**Independent Test**: Peut être testé en créant un utilisateur éditeur et en vérifiant qu'il peut saisir des comptes mais ne peut pas modifier la géographie ou les templates.

**Acceptance Scenarios**:

1. **Given** un administrateur connecté, **When** il crée un compte éditeur avec email et mot de passe, **Then** l'éditeur peut se connecter au back-office
2. **Given** un éditeur connecté, **When** il tente d'accéder à la gestion de la géographie, **Then** l'accès lui est refusé
3. **Given** un éditeur connecté, **When** il accède à la saisie des comptes, **Then** il ne voit que les collectivités de ses régions assignées
4. **Given** un éditeur connecté, **When** il tente de saisir un compte pour une collectivité hors de son périmètre, **Then** l'accès lui est refusé
4. **Given** un administrateur, **When** il désactive un compte utilisateur, **Then** cet utilisateur ne peut plus se connecter

---

### User Story 7 - Moteur de recherche (Priority: P7)

Un citoyen utilise un moteur de recherche pour trouver rapidement une collectivité territoriale par son nom, plutôt que de naviguer dans les menus déroulants hiérarchiques.

**Why this priority**: Améliore l'accessibilité mais n'est pas indispensable au lancement.

**Independent Test**: Peut être testé en saisissant le nom d'une commune dans le champ de recherche et en vérifiant que les résultats pertinents s'affichent.

**Acceptance Scenarios**:

1. **Given** un citoyen sur la page d'accueil, **When** il saisit un nom de collectivité dans la barre de recherche, **Then** les collectivités correspondantes s'affichent en suggestions
2. **Given** des résultats de recherche, **When** le citoyen sélectionne une collectivité, **Then** il est redirigé vers les comptes administratifs de cette collectivité

---

### User Story 8 - Newsletter et suivi d'audience (Priority: P8)

Un citoyen peut s'inscrire à une newsletter pour être informé des mises à jour de données. L'administrateur peut suivre les statistiques de visites et de téléchargements via le back-office.

**Why this priority**: Fonctionnalités d'engagement et de suivi utiles mais secondaires.

**Independent Test**: Peut être testé en s'inscrivant à la newsletter depuis le front-office et en vérifiant la réception d'un email de confirmation, et en vérifiant que les statistiques s'incrémentent après une visite.

**Acceptance Scenarios**:

1. **Given** un citoyen sur le site, **When** il saisit son email et s'inscrit à la newsletter, **Then** il reçoit un email de confirmation
2. **Given** un administrateur dans le back-office, **When** il consulte les statistiques, **Then** il voit le nombre de visites, les pages consultées et le nombre de téléchargements
3. **Given** un administrateur, **When** il rédige une newsletter, **Then** elle est envoyée à tous les abonnés

---

### User Story 9 - Intégration GlobalLeaks (Priority: P9)

La plateforme offre un lien ou une intégration vers GlobalLeaks pour permettre aux citoyens de signaler de manière sécurisée et anonyme des irrégularités dans la gestion des revenus miniers.

**Why this priority**: Fonctionnalité complémentaire de lutte contre la corruption, prévue comme intégration future.

**Independent Test**: Peut être testé en vérifiant la présence d'un lien/bouton vers GlobalLeaks sur le front-office et que ce lien mène vers l'instance configurée.

**Acceptance Scenarios**:

1. **Given** un citoyen sur la page de résultats, **When** il voit la section signalement, **Then** un lien vers la plateforme GlobalLeaks est visible
2. **Given** le lien GlobalLeaks, **When** le citoyen clique dessus, **Then** il est redirigé vers l'instance GlobalLeaks de TI Madagascar

---

### Edge Cases

- Que se passe-t-il lorsqu'une collectivité n'a aucun compte administratif saisi pour une année donnée ? Le système affiche un message explicite indiquant l'absence de données.
- Que se passe-t-il si un administrateur supprime un compte de niveau 1 dans un template alors que des données existent ? Les comptes déjà saisis conservent leur version de template ; la suppression ne s'applique qu'aux futurs comptes.
- Que se passe-t-il si les valeurs saisies génèrent une division par zéro dans le calcul du Taux (Prévisions = 0) ? Le système affiche "N/A" ou 0% au lieu d'une erreur.
- Que se passe-t-il si un éditeur modifie un compte déjà publié ? Le compte repasse en statut brouillon ; il doit être re-validé par un administrateur pour redevenir visible.
- Que se passe-t-il si les menus déroulants contiennent un très grand nombre d'entrées ? Le système gère la performance avec un chargement progressif.
- Comment le système gère-t-il les années d'exercice sans donnée pour certains programmes ? Les programmes sans données sont masqués ou affichés vides selon la configuration.

## Requirements *(mandatory)*

### Functional Requirements

**Navigation et consultation publique**

- **FR-001**: Le système DOIT afficher une page d'accueil avec le titre "Plateforme de suivi des revenus miniers des collectivités territoriales" et le logo de TI Madagascar
- **FR-002**: Le système DOIT proposer 3 menus déroulants hiérarchiques (Province, Région, Commune) dont le contenu se charge en cascade
- **FR-003**: Le système DOIT afficher les comptes administratifs de la collectivité sélectionnée après clic sur le bouton "OK"
- **FR-004**: La sélection de la Commune DOIT être optionnelle ; si seule la Région est sélectionnée, les comptes de la région s'affichent
- **FR-005**: Le système DOIT permettre la sélection d'une année d'exercice pour afficher les comptes correspondants, avec un sélecteur permettant de basculer rapidement entre les années disponibles sans revenir à la page d'accueil
- **FR-006**: Le système DOIT afficher une section de description de la collectivité en texte riche au-dessus ou en dessous des tableaux

**Structure des tableaux de comptes**

- **FR-007**: Le tableau des recettes DOIT afficher les comptes sur 3 niveaux hiérarchiques (Niv1, Niv2, Niv3) avec les colonnes : Budget Primitif, Budget Additionnel, Modifications Budgétaires, Prévisions Définitives, OR Admis, Recouvrement, Reste à Recouvrer, Taux
- **FR-008**: Le système DOIT afficher un récapitulatif des recettes reprenant uniquement les comptes de niveau 1
- **FR-009**: Le tableau des dépenses DOIT afficher les comptes par programme (3 programmes par défaut) sur 3 niveaux hiérarchiques avec les colonnes : Budget, Engagement, Mandatement, Paiement, Reste à Payer, Taux
- **FR-010**: Le système DOIT permettre l'ajout dynamique de programmes supplémentaires au-delà des 3 par défaut
- **FR-011**: Le système DOIT afficher un récapitulatif des dépenses par programme (croisement comptes x programmes) et un récapitulatif global (niveau 1)
- **FR-012**: Le système DOIT afficher un tableau d'équilibre présentant dépenses et recettes côte à côte

**Formules de calcul**

- **FR-013**: Les valeurs de niveau 1 DOIVENT être calculées automatiquement comme la somme des valeurs de niveau 2
- **FR-014**: Les valeurs de niveau 2 DOIVENT être calculées automatiquement comme la somme des valeurs de niveau 3
- **FR-015**: Le Taux des recettes DOIT être calculé comme OR Admis / Prévisions Définitives
- **FR-016**: Le Reste à Recouvrer DOIT être calculé comme OR Admis - Recouvrement
- **FR-017**: Le Taux des dépenses DOIT être calculé comme Paiement / Budget
- **FR-018**: Le Reste à Payer DOIT être calculé comme Engagement - Paiement

**Export et impression**

- **FR-019**: Le système DOIT permettre le téléchargement des tableaux au format Excel avec les formules préservées
- **FR-020**: Le système DOIT permettre le téléchargement des tableaux au format Word
- **FR-021**: Le système DOIT proposer une mise en page optimisée pour l'impression

**Back-office - Géographie**

- **FR-022**: Le système DOIT permettre la création, modification, suppression et réordonnancement des Provinces, Régions et Communes
- **FR-023**: Chaque entité géographique DOIT pouvoir avoir une description en texte riche
- **FR-024**: La hiérarchie Province > Région > Commune DOIT être respectée (une région appartient à une seule province, une commune à une seule région)

**Back-office - Templates de tableaux**

- **FR-025**: Le système DOIT permettre à un administrateur de modifier la structure des tableaux (ajout/suppression/réordonnancement de lignes et colonnes) sans intervention technique
- **FR-026**: Le système DOIT permettre la définition de formules de calcul dans les templates
- **FR-027**: Les modifications de templates DOIVENT se refléter uniquement pour les nouveaux comptes ; les comptes existants conservent la version du template utilisée lors de leur saisie
- **FR-027b**: Le système DOIT versionner les templates de tableaux afin que chaque compte administratif soit lié à la version du template en vigueur au moment de sa création

**Back-office - Saisie des comptes**

- **FR-028**: Le système DOIT permettre la saisie des comptes administratifs par collectivité et par année d'exercice. Un seul compte administratif peut exister par couple (collectivité, année) ; toute nouvelle saisie modifie l'existant
- **FR-028b**: Les comptes administratifs DOIVENT suivre un cycle de vie brouillon → publié. L'éditeur enregistre en brouillon ; seul un administrateur peut valider et publier
- **FR-028c**: Seuls les comptes au statut "publié" DOIVENT être visibles sur le front-office
- **FR-028d**: Un administrateur DOIT pouvoir dépublier un compte publié pour le rendre invisible sur le front-office
- **FR-029**: Pour une Région, le champ Commune DOIT être optionnel lors de la saisie
- **FR-030**: Les formules de calcul DOIVENT s'exécuter automatiquement lors de la saisie

**Back-office - Utilisateurs**

- **FR-031**: Le système DOIT supporter deux rôles : administrateur (accès complet) et éditeur (saisie des comptes sur son périmètre uniquement)
- **FR-031b**: Un éditeur DOIT être affecté à une ou plusieurs régions ; il ne peut saisir des comptes que pour les régions et communes de son périmètre
- **FR-031c**: Un administrateur DOIT pouvoir assigner et modifier les régions affectées à chaque éditeur
- **FR-032**: Un administrateur DOIT pouvoir créer, modifier et désactiver des comptes utilisateurs
- **FR-033**: Le système DOIT authentifier les utilisateurs du back-office par email et mot de passe

**Fonctionnalités complémentaires**

- **FR-034**: Le système DOIT proposer un moteur de recherche textuel permettant de trouver une collectivité par son nom
- **FR-035**: Le système DOIT permettre aux visiteurs de s'inscrire à une newsletter par email
- **FR-036**: Le système DOIT collecter des statistiques de visites et de téléchargements consultables par l'administrateur
- **FR-037**: Le système DOIT proposer un lien vers la plateforme GlobalLeaks pour le signalement anonyme d'irrégularités

**Contraintes non-fonctionnelles**

- **FR-038**: L'interface DOIT être responsive (mobile, tablette, desktop)
- **FR-039**: Le système DOIT être compatible avec Chrome, Firefox et Edge (versions récentes)
- **FR-040**: Le site public DOIT être optimisé pour le référencement naturel (SEO)

### Key Entities

- **Province**: Division administrative de premier niveau. Attributs : nom, description (texte riche), ordre d'affichage. Contient plusieurs régions.
- **Region**: Division administrative de deuxième niveau. Attributs : nom, description (texte riche), ordre d'affichage. Appartient à une province, contient plusieurs communes. Peut avoir ses propres comptes administratifs.
- **Commune**: Division administrative de troisième niveau. Attributs : nom, description (texte riche), ordre d'affichage. Appartient à une région.
- **Compte Administratif**: Ensemble des données financières d'une collectivité pour une année d'exercice. Unicité : un seul par couple (collectivité, année). Lié à une région ou commune. Contient les recettes, dépenses et équilibres. Statut : brouillon ou publié. Lié à une version de template.
- **Template de Tableau**: Modèle définissant la structure d'un type de tableau (recettes, dépenses, équilibre). Contient la liste des comptes hiérarchiques, des colonnes et des formules. Modifiable par l'administrateur. Versionné : chaque modification crée une nouvelle version ; les comptes existants restent liés à leur version d'origine.
- **Compte (ligne de tableau)**: Entrée dans un tableau, organisée en 3 niveaux hiérarchiques. Attributs : code, libellé, niveau, parent, ordre.
- **Programme**: Catégorisation des dépenses. Attributs : nom, ordre. Au minimum 3 par défaut, extensible dynamiquement.
- **Utilisateur**: Compte d'accès au back-office. Attributs : email, mot de passe, rôle (administrateur ou éditeur), statut (actif/inactif). Pour les éditeurs : liste des régions assignées (périmètre de saisie).
- **Abonne Newsletter**: Inscription à la newsletter. Attributs : email, date d'inscription, statut.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un citoyen peut consulter les comptes administratifs d'une collectivité en moins de 3 clics depuis la page d'accueil (sélection Province + Région + OK)
- **SC-002**: 100% des formules de calcul (totaux, taux, restes) s'exécutent correctement et sont cohérentes entre l'affichage web et les fichiers téléchargés
- **SC-003**: Un administrateur peut modifier la structure d'un tableau (ajout d'une ligne ou colonne) en moins de 5 minutes sans assistance technique
- **SC-004**: La plateforme affiche les tableaux de comptes en moins de 3 secondes après la sélection d'une collectivité
- **SC-005**: Les fichiers Excel et Word téléchargés contiennent 100% des données affichées à l'écran
- **SC-006**: Un éditeur peut saisir un jeu complet de comptes administratifs (recettes + dépenses 3 programmes) en moins de 30 minutes
- **SC-007**: L'interface est utilisable sur écran mobile (320px de large minimum) sans perte de fonctionnalité de consultation
- **SC-008**: Le site public est indexé par les moteurs de recherche (pages de collectivités accessibles par URL unique)
- **SC-009**: Le système supporte au minimum les données des 22 régions et 1695 communes de Madagascar sans dégradation de performance
- **SC-010**: Les statistiques de visites et téléchargements sont disponibles en temps réel pour l'administrateur

## Assumptions

- La structure administrative de Madagascar (6 provinces, 22 régions, ~1695 communes) est relativement stable et ne nécessite pas de gestion de versions historiques.
- L'authentification par email/mot de passe est suffisante pour le back-office. L'authentification à deux facteurs n'est pas requise au lancement.
- Le site public est accessible sans authentification.
- Les données des comptes administratifs sont saisies manuellement (pas d'import automatique depuis un système externe au lancement).
- Le système de newsletter utilise un mécanisme d'inscription simple avec confirmation par email. L'envoi est déclenché manuellement par l'administrateur.
- L'intégration GlobalLeaks se limite à un lien externe vers l'instance existante de TI Madagascar (pas d'intégration technique profonde).
- La langue supportée est le français uniquement au lancement.
- Les formules de calcul des dépenses : Taux = Paiement / Budget, Reste à Payer = Engagement - Paiement (conventions comptables publiques malgaches).
- Le nombre de programmes de dépenses par compte administratif est variable mais commence à 3 par défaut.
