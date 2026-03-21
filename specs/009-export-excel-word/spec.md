# Feature Specification: Export des comptes administratifs en Excel et Word

**Feature Branch**: `009-export-excel-word`
**Created**: 2026-03-21
**Status**: Draft
**Input**: User description: "Feature 7 : Export des comptes en Excel et Word"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Telecharger le compte administratif au format Excel (Priority: P1)

Un visiteur consulte la page publique d'une collectivite et souhaite obtenir un fichier Excel officiel du compte administratif. Il clique sur le bouton "Telecharger Excel". Un indicateur de chargement apparait pendant la generation. Le fichier telecharge reproduit fidelement la structure du document officiel de compte administratif de Madagascar : un classeur avec des feuilles distinctes (Recettes, Recap Recettes, une feuille par programme de depenses, Recap Depenses par Programme, Recap Depenses, Equilibre). Chaque feuille presente la meme hierarchie de comptes, les memes colonnes et la meme mise en forme que le template de reference : en-tetes en gras, bordures de cellules, largeurs de colonnes ajustees, lignes de niveau 1 en gras, lignes de niveau 2 et 3 en retrait. Les totaux et colonnes calculees (previsions definitives, restes, taux d'execution) sont pre-calcules comme valeurs statiques. Le nom du fichier inclut le nom de la collectivite et l'annee d'exercice.

**Why this priority**: L'export Excel est le format le plus demande pour l'analyse et le partage des donnees financieres des collectivites. Il reproduit le document officiel utilise par les administrations malgaches.

**Independent Test**: Peut etre teste en telechargeant le fichier Excel d'Andrafiabe 2023 et en comparant la structure, les valeurs et la mise en forme avec le fichier de reference COMPTE_ADMINISTRATIF_COMMUNE_ANDRAFIABE_2023.xlsx.

**Acceptance Scenarios**:

1. **Given** un visiteur consulte un compte publie, **When** il clique sur "Telecharger Excel", **Then** un indicateur de chargement apparait puis un fichier .xlsx est telecharge
2. **Given** le fichier est telecharge, **When** l'utilisateur l'ouvre, **Then** il contient les feuilles correspondant a la structure du template : Recettes, Recap Recettes, une feuille par programme de depenses existant, Recap Depenses par Programme, Recap Depenses, Equilibre
3. **Given** la feuille Recettes est ouverte, **When** l'utilisateur examine la structure, **Then** elle contient un titre avec le nom de la collectivite, les en-tetes de colonnes (Compte, Intitules, Budget Primitif, Budget Additionnel, Modifications +/-, Previsions Definitives, OR Admis, Recouvrement, Reste a Recouvrer, Taux d'Execution) et les lignes hierarchiques avec separation Fonctionnement / Investissement
4. **Given** une feuille de depenses par programme est ouverte, **When** l'utilisateur examine les colonnes, **Then** elles correspondent au template : Compte, Intitules, Budget Primitif, Budget Additionnel, Modifications +/-, Previsions Definitives, Engagement, Mandat Admis, Paiement, Reste a Payer, Taux d'Execution
5. **Given** les lignes de niveau 1 (ex: "70 IMPOTS SUR LES REVENUS"), **When** l'utilisateur examine la mise en forme, **Then** elles sont en gras avec une police plus marquee
6. **Given** les lignes de niveau 2 et 3, **When** l'utilisateur examine l'alignement, **Then** les intitules sont decales vers la droite proportionnellement au niveau hierarchique
7. **Given** les colonnes calculees, **When** l'utilisateur verifie les valeurs, **Then** les previsions definitives, restes et taux d'execution correspondent aux calculs attendus (valeurs statiques pre-calculees, pas de formules Excel)
8. **Given** le fichier telecharge, **When** l'utilisateur verifie le nom, **Then** il suit le format "Compte_Administratif_[NomCollectivite]_[Annee].xlsx"

---

### User Story 2 - Telecharger le compte administratif au format Word (Priority: P2)

Un visiteur souhaite obtenir un document Word du compte administratif pour l'integrer dans un rapport ou le partager. Il clique sur le bouton "Telecharger Word". Le document genere contient un en-tete avec le nom de la collectivite et l'annee d'exercice, puis un tableau Word par section du compte (Recettes, chaque programme de depenses, Recapitulatif Recettes, Recapitulatif Depenses, Equilibre). Les tableaux reproduisent la meme structure de donnees que l'export Excel.

**Why this priority**: Le format Word est utile pour l'integration dans des rapports mais moins critique que l'Excel pour l'analyse de donnees.

**Independent Test**: Peut etre teste en telechargeant le fichier Word d'Andrafiabe 2023 et en verifiant que tous les tableaux sont presents avec les bonnes donnees.

**Acceptance Scenarios**:

1. **Given** un visiteur consulte un compte publie, **When** il clique sur "Telecharger Word", **Then** un fichier .docx est telecharge avec un indicateur de chargement pendant la generation
2. **Given** le document est ouvert, **When** l'utilisateur examine la structure, **Then** il contient un en-tete avec le nom de la collectivite et l'annee, puis des sections titrees avec un tableau par section
3. **Given** le tableau des recettes dans le Word, **When** l'utilisateur compare avec l'Excel, **Then** les donnees sont identiques (memes valeurs, memes colonnes)
4. **Given** le fichier telecharge, **When** l'utilisateur verifie le nom, **Then** il suit le format "Compte_Administratif_[NomCollectivite]_[Annee].docx"

---

### User Story 3 - Boutons de telechargement sur la page de consultation (Priority: P1)

Un visiteur se trouve sur la page de consultation d'une collectivite. Il voit des boutons "Telecharger Excel" et "Telecharger Word" clairement visibles. Lorsqu'il clique sur l'un des boutons, un indicateur de chargement (spinner ou texte) s'affiche et le bouton est desactive pendant la generation du fichier. Une fois le telechargement lance, le bouton revient a son etat normal.

**Why this priority**: Les boutons sont le point d'entree indispensable pour acceder aux exports. Sans eux, les fonctions d'export sont inaccessibles aux visiteurs.

**Independent Test**: Peut etre teste en visitant la page d'une collectivite et en verifiant la presence, le comportement et l'accessibilite des boutons de telechargement.

**Acceptance Scenarios**:

1. **Given** un visiteur est sur la page de consultation d'un compte publie, **When** la page se charge, **Then** les boutons "Telecharger Excel" et "Telecharger Word" sont visibles
2. **Given** le visiteur clique sur un bouton de telechargement, **When** la generation est en cours, **Then** un indicateur de chargement est affiche et le bouton est desactive pour eviter les clics multiples
3. **Given** la generation est terminee, **When** le fichier commence a se telecharger, **Then** le bouton revient a son etat normal
4. **Given** une erreur survient pendant la generation, **When** le systeme ne peut pas generer le fichier, **Then** un message d'erreur est affiche et le bouton redevient cliquable
5. **Given** le visiteur est sur mobile, **When** il voit les boutons de telechargement, **Then** ils sont accessibles et utilisables sans defilement excessif

---

### Edge Cases

- Que se passe-t-il si un compte n'a aucune donnee de recettes ou depenses saisie ? Le fichier exporte contient les feuilles avec les en-tetes et la structure du template mais des valeurs a zero
- Que se passe-t-il si un compte a moins de 3 programmes de depenses (ex: seuls les Programmes I et II existent) ? Le fichier Excel contient uniquement les feuilles des programmes existants ; la feuille Recap Depenses par Programme ne montre que les programmes presents
- Que se passe-t-il si la generation du fichier prend trop de temps ? Le systeme impose un delai maximal raisonnable et affiche un message d'erreur en cas de depassement
- Que se passe-t-il si le visiteur clique plusieurs fois rapidement sur le bouton de telechargement ? Le bouton est desactive des le premier clic ; un seul telechargement est declenche
- Que se passe-t-il si le nom de la collectivite contient des caracteres speciaux (accents, apostrophes) ? Le nom du fichier est nettoye pour etre compatible avec tous les systemes de fichiers
- Que se passe-t-il si le compte est depublie entre la consultation et le clic sur "Telecharger" ? Le systeme retourne une erreur indiquant que le compte n'est plus disponible

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le systeme DOIT fournir un point d'acces pour telecharger un compte administratif publie au format Excel (.xlsx), accessible sans authentification
- **FR-002**: Le fichier Excel genere DOIT contenir des feuilles reproduisant la structure du template officiel : Recettes, Recap Recettes, une feuille par programme de depenses, Recap Depenses par Programme, Recap Depenses, Equilibre
- **FR-003**: Le nombre de feuilles de depenses par programme DOIT correspondre au nombre de programmes existants dans le compte (pas de feuille vide pour un programme inexistant)
- **FR-004**: La feuille Recettes DOIT contenir les colonnes : Compte, Intitules, Budget Primitif, Budget Additionnel, Modifications +/-, Previsions Definitives, OR Admis, Recouvrement, Reste a Recouvrer, Taux d'Execution
- **FR-005**: Chaque feuille de depenses par programme DOIT contenir les colonnes : Compte, Intitules, Budget Primitif, Budget Additionnel, Modifications +/-, Previsions Definitives, Engagement, Mandat Admis, Paiement, Reste a Payer, Taux d'Execution
- **FR-006**: La feuille Recap Depenses par Programme DOIT presenter un croisement categories (lignes) / programmes (colonnes) avec les sous-totaux Mandatement, Paiement et Reste a Payer par programme et au total
- **FR-007**: La feuille Equilibre DOIT presenter les depenses et recettes en vis-a-vis avec les totaux par section (Fonctionnement, Investissement) et le resultat global (excedent ou deficit)
- **FR-008**: Les colonnes calculees (Previsions Definitives, Reste a Recouvrer, Reste a Payer, Taux d'Execution, totaux hierarchiques) DOIVENT etre exportees comme valeurs statiques pre-calculees, sans formules Excel natives
- **FR-009**: La mise en forme du fichier Excel DOIT reproduire le style du template de reference : en-tetes en gras avec fond colore, bordures de cellules, largeurs de colonnes ajustees au contenu, lignes de niveau 1 en gras, intitules de niveau 2 et 3 avec retrait visuel
- **FR-010**: Chaque feuille Excel DOIT afficher en en-tete le titre du tableau et le nom de la collectivite
- **FR-011**: Les sections Fonctionnement et Investissement DOIVENT etre separees visuellement par des lignes d'en-tete de section dans chaque feuille
- **FR-012**: Le systeme DOIT fournir un point d'acces pour telecharger un compte administratif publie au format Word (.docx), accessible sans authentification
- **FR-013**: Le document Word DOIT contenir un en-tete avec le nom de la collectivite et l'annee d'exercice, puis un tableau par section du compte (Recettes, chaque programme de depenses, Recapitulatif Recettes, Recapitulatif Depenses, Equilibre)
- **FR-014**: Les donnees exportees en Word DOIVENT etre identiques aux donnees exportees en Excel pour le meme compte
- **FR-015**: Le nom des fichiers telecharges DOIT suivre le format "Compte_Administratif_[NomCollectivite]_[Annee].[extension]" avec les caracteres speciaux remplaces pour la compatibilite des systemes de fichiers
- **FR-016**: Les points d'acces d'export NE DOIVENT retourner que les comptes dont le statut est "publie" ; un compte en brouillon retourne une erreur
- **FR-017**: L'interface de consultation DOIT afficher des boutons "Telecharger Excel" et "Telecharger Word" sur la page de chaque collectivite
- **FR-018**: Les boutons de telechargement DOIVENT afficher un indicateur de chargement pendant la generation et se desactiver pour eviter les clics multiples
- **FR-019**: Les boutons de telechargement DOIVENT etre visibles et accessibles en mode responsive (mobile et desktop)
- **FR-020**: Les boutons de telechargement DOIVENT fonctionner en mode clair et en mode sombre

### Key Entities

- **Export Excel**: Fichier .xlsx multi-feuilles reproduisant la structure du template officiel de compte administratif. Contient des donnees pre-calculees (valeurs statiques, pas de formules). Genere a la demande a partir des donnees d'un compte administratif publie.
- **Export Word**: Document .docx structure contenant un en-tete et des tableaux par section. Genere a la demande avec les memes donnees que l'export Excel.
- **Bouton de telechargement**: Element d'interface sur la page publique de consultation permettant de declencher le telechargement d'un fichier avec gestion d'etat (inactif, en cours, erreur).

## Assumptions

- Les comptes administratifs, templates, lignes de recettes et depenses sont geres par les Features 006 et 007
- Les calculs (colonnes derivees, sommes hierarchiques, recapitulatifs, equilibre) sont deja implementes dans les services existants du backend
- La page publique de consultation des comptes (Feature 008) est en place et fournit le contexte pour les boutons de telechargement
- Le template de reference officiel est stocke dans le depot pour guider la mise en forme, mais les fichiers exportes sont generes dynamiquement a partir des donnees
- Le nombre de programmes de depenses est dynamique (generalement 3, mais peut varier selon la collectivite)
- Les fichiers generes sont de taille raisonnable (quelques centaines de lignes par feuille) et ne necessitent pas de generation asynchrone

## Out of Scope

- Export au format PDF
- Export groupant plusieurs collectivites ou plusieurs annees dans un seul fichier
- Personnalisation du format d'export par l'utilisateur (choix des feuilles, des colonnes)
- Generation de graphiques ou de visualisations dans les fichiers exportes
- Envoi des fichiers par email
- Cache des fichiers generes cote serveur
- Export des annexes (comptes matiere, engagements non ordonnances, ordres de recettes non recouvres)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un visiteur peut telecharger le fichier Excel d'un compte en moins de 5 secondes apres avoir clique sur le bouton
- **SC-002**: Le fichier Excel telecharge contient les feuilles correspondant a la structure du template de reference pour le meme compte
- **SC-003**: Les valeurs dans les fichiers exportes (Excel et Word) sont identiques a celles affichees dans l'interface de consultation en ligne (zero ecart)
- **SC-004**: Le fichier Excel reproduit la mise en forme du template de reference : en-tetes en gras, bordures, retraits par niveau hierarchique
- **SC-005**: Les boutons de telechargement sont accessibles et fonctionnels sur mobile (ecran 375px de large)
- **SC-006**: Le visiteur voit un indicateur de chargement pendant la generation et ne peut pas declencher plusieurs telechargements simultanement
