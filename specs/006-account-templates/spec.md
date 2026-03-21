# Feature Specification: Structure standardisee des tableaux de comptes administratifs

**Feature Branch**: `006-account-templates`
**Created**: 2026-03-20
**Status**: Draft
**Input**: User description: "Feature 4 : Structure standardisee des tableaux de comptes administratifs."

## Clarifications

### Session 2026-03-20

- Q: Les comptes de recettes et depenses sont divises en sections Fonctionnement et Investissement dans le document officiel. Faut-il modeliser cette notion de section ? → A: Oui, ajouter un attribut "section" (fonctionnement/investissement) sur chaque ligne de template.
- Q: Comment l'administrateur doit-il naviguer dans un template de 289 lignes dans l'editeur visuel ? → A: Liste plate scrollable avec filtre de recherche et boutons "tout deplier / tout replier".
- Q: Les sous-totaux par section (Fonctionnement, Investissement) doivent-ils etre modelises comme des lignes en base ? → A: Non, calculer dynamiquement les sous-totaux par section a l'affichage (somme des Niv1 de la section).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Importer la structure de reference des comptes (Priority: P1)

Un administrateur souhaite initialiser le systeme avec la structure standardisee des tableaux de comptes administratifs des collectivites malgaches. Cette structure comprend un template de recettes (168 comptes sur 3 niveaux hierarchiques) et un template de depenses (273 comptes sur 3 niveaux). Le systeme importe automatiquement cette structure depuis les fichiers de reference Excel officiels, creant les lignes de comptes et les colonnes associees.

**Why this priority**: Sans la structure de reference importee, aucun tableau de compte ne peut etre cree ni utilise. C'est le socle de donnees sur lequel tout le suivi des revenus repose.

**Independent Test**: Peut etre teste en executant le script d'import et en verifiant que les templates recettes et depenses sont crees avec le bon nombre de lignes et de colonnes.

**Acceptance Scenarios**:

1. **Given** le systeme est vierge, **When** l'administrateur execute l'import de la structure de reference, **Then** un template "Recettes" est cree avec 168 lignes de comptes organises en 3 niveaux (14 Niv1, 36 Niv2, 118 Niv3)
2. **Given** le systeme est vierge, **When** l'administrateur execute l'import de la structure de reference, **Then** un template "Depenses" est cree avec 273 lignes de comptes organises en 3 niveaux (16 Niv1, 59 Niv2, 198 Niv3)
3. **Given** les templates sont importes, **When** l'administrateur consulte le template Recettes, **Then** les colonnes sont : Budget primitif, Budget additionnel, Modifications, Previsions definitives (calculee), OR admis, Recouvrement, Reste a recouvrer (calculee), Taux d'execution (calcule)
4. **Given** les templates sont importes, **When** l'administrateur consulte le template Depenses, **Then** les colonnes sont : Budget primitif, Budget additionnel, Modifications, Previsions definitives (calculee), Engagement, Mandat admis, Paiement, Reste a payer (calculee), Taux d'execution (calcule)
5. **Given** les templates sont importes, **When** l'administrateur consulte la hierarchie des comptes de recettes, **Then** les comptes sont organises : Niv1 (code a 2 chiffres, ex: 70) > Niv2 (3 chiffres, ex: 708) > Niv3 (4 chiffres, ex: 7080) avec les relations parent-enfant correctes
6. **Given** l'import a deja ete execute, **When** l'administrateur relance l'import, **Then** le systeme ne cree pas de doublons (idempotent)

---

### User Story 2 - Consulter et naviguer dans la structure d'un template (Priority: P2)

Un administrateur souhaite visualiser un template de compte administratif dans une interface qui reproduit fidelement la structure du tableau officiel. Il peut voir toutes les lignes de comptes organisees par niveau hierarchique, avec les colonnes definies et les indicateurs de colonnes calculees.

**Why this priority**: La consultation visuelle est necessaire pour verifier que la structure importee est correcte et pour comprendre l'organisation des comptes avant toute modification.

**Independent Test**: Peut etre teste en accedant a la page de detail d'un template et en verifiant que les lignes sont affichees dans le bon ordre hierarchique avec les bonnes colonnes.

**Acceptance Scenarios**:

1. **Given** des templates existent, **When** l'administrateur accede a la liste des templates, **Then** il voit tous les templates avec leur nom, type (recettes/depenses), version et statut actif/inactif
2. **Given** un template existe avec ses lignes, **When** l'administrateur accede au detail du template, **Then** les lignes sont affichees dans une liste plate scrollable avec indentation visuelle selon le niveau (Niv1 en gras, Niv2 indente, Niv3 double-indente), un filtre de recherche par code ou intitule, et des boutons "tout deplier / tout replier"
3. **Given** un template a des colonnes calculees, **When** l'administrateur consulte les colonnes, **Then** les colonnes calculees sont visuellement distinguees des colonnes de saisie (marquees avec un badge "Calcule")
4. **Given** un template Depenses existe, **When** l'administrateur affiche la previsualisation, **Then** le tableau affiche est fidele a la structure du document officiel avec les memes en-tetes de colonnes

---

### User Story 3 - Modifier la structure d'un template (Priority: P3)

Un administrateur souhaite adapter la structure standardisee a des besoins specifiques : ajouter un nouveau compte qui n'existe pas dans la structure officielle, supprimer un compte obsolete, reordonner les lignes, ou modifier les colonnes. Ces modifications sont rares mais necessaires pour s'adapter a l'evolution de la nomenclature comptable.

**Why this priority**: L'adaptabilite de la structure est essentielle a long terme. La nomenclature comptable evolue et de nouveaux comptes peuvent etre crees par decret.

**Independent Test**: Peut etre teste en ajoutant une nouvelle ligne de compte a un template existant, en verifiant qu'elle apparait au bon endroit dans la hierarchie, puis en la supprimant.

**Acceptance Scenarios**:

1. **Given** un template existe, **When** l'administrateur ajoute une nouvelle ligne avec un code a 4 chiffres et un parent a 3 chiffres, **Then** la ligne apparait au bon niveau hierarchique sous son parent
2. **Given** un template a des lignes, **When** l'administrateur reordonne les lignes a un meme niveau, **Then** le nouvel ordre est preserve apres sauvegarde
3. **Given** un template a des lignes, **When** l'administrateur supprime une ligne de niveau 3 (feuille), **Then** la ligne est retiree du template
4. **Given** un template a des lignes, **When** l'administrateur tente de supprimer une ligne de niveau 1 ou 2 qui a des enfants, **Then** le systeme empeche la suppression et affiche un message d'erreur
5. **Given** un template a des colonnes, **When** l'administrateur modifie le nom ou l'ordre des colonnes, **Then** les modifications sont sauvegardees et refletees dans la previsualisation

---

### User Story 4 - Importer des donnees d'exemple pour validation (Priority: P4)

Un administrateur ou un testeur souhaite verifier que la structure importee est fonctionnelle en chargeant un jeu de donnees reelles (Commune d'Andrafiabe, exercice 2023). Ce jeu de donnees sert de reference pour valider les formules de calcul et la coherence de la structure.

**Why this priority**: La validation avec des donnees reelles est le seul moyen fiable de confirmer que la structure est correcte et que les formules produisent les bons resultats.

**Independent Test**: Peut etre teste en executant l'import des donnees Andrafiabe, puis en verifiant que les totaux calcules correspondent aux totaux du document officiel.

**Acceptance Scenarios**:

1. **Given** les templates de reference sont importes, **When** l'administrateur importe le jeu de donnees Andrafiabe 2023, **Then** les valeurs sont correctement associees aux lignes de comptes existantes
2. **Given** les donnees Andrafiabe sont importees, **When** le systeme calcule les previsions definitives, **Then** le resultat est egal a budget primitif + budget additionnel + modifications pour chaque ligne
3. **Given** les donnees Andrafiabe sont importees, **When** le systeme calcule le reste a recouvrer (recettes), **Then** le resultat est egal a OR admis - Recouvrement
4. **Given** les donnees Andrafiabe sont importees, **When** le systeme calcule le taux d'execution (recettes), **Then** le resultat est egal a OR admis / Previsions definitives
5. **Given** les donnees Andrafiabe sont importees pour les depenses, **When** les 3 programmes sont charges (Administration, Developpement Economique, Sante), **Then** chaque programme a ses propres valeurs associees au meme template de depenses

---

### Edge Cases

- Que se passe-t-il si le fichier Excel de reference est absent ou corrompu ? Le systeme affiche un message d'erreur clair et ne cree aucun template partiel
- Que se passe-t-il si un code de compte dans le fichier Excel n'a pas de parent valide ? Le systeme signale l'anomalie dans un rapport d'import
- Que se passe-t-il si un administrateur tente d'ajouter une ligne avec un code deja existant dans le template ? Le systeme refuse et affiche un message d'erreur
- Que se passe-t-il si les previsions definitives sont a zero lors du calcul du taux d'execution ? Le systeme affiche "N/A" ou 0% au lieu de provoquer une erreur de division par zero
- Que se passe-t-il si un template actif est modifie alors que des comptes administratifs l'utilisent deja ? Le systeme doit gerer le versioning (hors scope de cette feature, mais le modele doit le permettre via le champ version)
- Que se passe-t-il si une ligne de niveau 1 n'a aucun enfant de niveau 2 ? La somme hierarchique renvoie zero
- Que se passe-t-il si les donnees d'exemple contiennent des cellules vides ? Le systeme traite les cellules vides comme des valeurs nulles (zero pour les calculs)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le systeme DOIT permettre de definir des templates de comptes administratifs avec un nom, un type (recettes ou depenses), un numero de version et un indicateur actif/inactif
- **FR-002**: Chaque template DOIT contenir des lignes de comptes organisees en 3 niveaux hierarchiques : Niveau 1 (code a 2 chiffres), Niveau 2 (code a 3 chiffres), Niveau 3 (code a 4 chiffres)
- **FR-003**: Chaque ligne de compte DOIT avoir un code, un intitule, un niveau hierarchique (1, 2 ou 3), un code parent (sauf Niv1), une section (fonctionnement ou investissement) et un ordre de tri
- **FR-004**: Chaque template DOIT contenir des definitions de colonnes avec un nom, un code, un type de donnee (nombre, texte ou pourcentage), un indicateur de colonne calculee, une formule eventuelle et un ordre de tri
- **FR-005**: Le template Recettes DOIT definir les colonnes suivantes : Budget primitif, Budget additionnel, Modifications, Previsions definitives, OR admis, Recouvrement, Reste a recouvrer, Taux d'execution
- **FR-006**: Le template Depenses DOIT definir les colonnes suivantes : Budget primitif, Budget additionnel, Modifications, Previsions definitives, Engagement, Mandat admis, Paiement, Reste a payer, Taux d'execution
- **FR-007**: Les colonnes calculees DOIVENT appliquer les formules : Previsions definitives = Budget primitif + Budget additionnel + Modifications ; Reste a recouvrer = OR admis - Recouvrement ; Reste a payer = Mandat admis - Paiement ; Taux d'execution (recettes) = OR admis / Previsions definitives ; Taux d'execution (depenses) = Mandat admis / Previsions definitives
- **FR-008**: Les lignes de niveau 1 DOIVENT afficher la somme de leurs lignes de niveau 2 enfants pour chaque colonne numerique. Les lignes de niveau 2 DOIVENT afficher la somme de leurs lignes de niveau 3 enfants. Les sous-totaux par section (Fonctionnement, Investissement) DOIVENT etre calcules dynamiquement a l'affichage (somme des Niv1 de la section) et ne sont pas stockes comme des lignes en base
- **FR-009**: Le systeme DOIT fournir un mecanisme d'import de la structure de reference depuis les fichiers Excel officiels (182 lignes de recettes, 289 lignes de depenses par programme)
- **FR-010**: L'import DOIT etre idempotent : relancer l'import ne cree pas de doublons
- **FR-011**: Le systeme DOIT permettre a un administrateur de consulter la liste des templates
- **FR-012**: Le systeme DOIT permettre a un administrateur de consulter le detail d'un template avec ses lignes et colonnes
- **FR-013**: Le systeme DOIT permettre a un administrateur d'ajouter une nouvelle ligne de compte a un template existant
- **FR-014**: Le systeme DOIT permettre a un administrateur de supprimer une ligne de compte de niveau 3 (feuille) d'un template
- **FR-015**: Le systeme DOIT empecher la suppression d'une ligne de compte qui possede des lignes enfants
- **FR-016**: Le systeme DOIT permettre a un administrateur de modifier l'ordre et les proprietes des lignes et colonnes d'un template
- **FR-017**: Le systeme DOIT offrir une previsualisation du tableau sous forme de liste plate scrollable avec indentation hierarchique, distinction visuelle des colonnes calculees, filtre de recherche par code ou intitule, et boutons "tout deplier / tout replier"
- **FR-018**: Le systeme DOIT permettre d'importer un jeu de donnees d'exemple (Andrafiabe 2023) pour valider la structure et les formules

### Key Entities

- **Template de compte (AccountTemplate)**: Represente un modele standardise de tableau de compte administratif. Possede un nom, un type (recettes ou depenses), un numero de version et un indicateur actif/inactif. Contient des lignes de comptes et des definitions de colonnes.
- **Ligne de template (AccountTemplateLine)**: Represente un compte dans la hierarchie. Possede un code de compte, un intitule, un niveau (1, 2 ou 3), un code parent pour les niveaux 2 et 3, une section (fonctionnement ou investissement) et un ordre de tri. Appartient a un template. Les comptes sont regroupes visuellement par section dans le tableau.
- **Colonne de template (AccountTemplateColumn)**: Definit une colonne du tableau. Possede un nom, un code, un type de donnee (nombre, texte, pourcentage), un indicateur de calcul automatique, une formule eventuelle et un ordre de tri. Appartient a un template.
- **Donnees de reference**: Structure standardisee des comptes issue des documents officiels malgaches. Comprend 168 comptes de recettes et 273 comptes de depenses, organises en 3 niveaux hierarchiques.
- **Jeu de donnees d'exemple**: Donnees reelles de la Commune d'Andrafiabe (exercice 2023) couvrant les recettes et les depenses sur 3 programmes (Administration et Coordination, Developpement Economique et Social, Sante).

## Assumptions

- La structure des comptes est basee sur la nomenclature comptable officielle des collectivites territoriales decentralisees de Madagascar
- Le template Recettes est unique et non associe a un programme specifique ; les templates Depenses sont utilises une fois par programme (3 programmes standard)
- Les 3 programmes standard (Administration, Developpement Economique, Sante) sont representes par 3 instances distinctes du meme template Depenses lors du remplissage des comptes administratifs
- Les fichiers Excel de reference sont fournis avec le projet et copies dans un repertoire de donnees accessible au script d'import
- Un seul template actif par type (recettes / depenses) a la fois
- Les formules de colonnes calculees sont stockees sous forme declarative (identifiants de colonnes, pas de references de cellules Excel)
- La division par zero dans le calcul du taux d'execution produit une valeur nulle ou "N/A"
- Les operations de modification de template sont reservees aux administrateurs (feature auth-roles existante)
- Le versioning des templates sera exploite par les features ulterieures de saisie des comptes administratifs ; cette feature se concentre sur la definition et la gestion de la structure

## Out of Scope

- Saisie des valeurs des comptes administratifs par les communes (feature separee)
- Affichage public des tableaux remplis
- Generation de rapports PDF ou exports Excel
- Gestion des programmes (la notion de programme releve du compte administratif, pas du template)
- Workflows de validation ou d'approbation des templates
- Historique des modifications (audit trail) des templates
- Feuilles recapitulatives inter-feuilles (RECAPITULATIF RECETTES, RECAP DEPENSES, EQUILIBRE) - ces derivations seront traitees dans la feature de saisie des comptes
- Import de templates depuis des fichiers Excel arbitraires (seule la structure de reference officielle est importee)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: La structure de reference (168 comptes de recettes et 273 comptes de depenses) est importee integralement et sans erreur lors de l'initialisation du systeme
- **SC-002**: Les formules de calcul produisent des resultats identiques aux totaux du document officiel Andrafiabe 2023 avec une marge d'erreur inferieure a 1 unite monetaire (arrondi)
- **SC-003**: Un administrateur peut visualiser la structure complete d'un template (jusqu'a 289 lignes) en moins de 3 secondes
- **SC-004**: Un administrateur peut ajouter ou supprimer une ligne de compte en moins de 5 actions (clics/saisies)
- **SC-005**: La previsualisation du tableau reproduit fidelement la structure hierarchique du document officiel (indentation, en-tetes, colonnes)
- **SC-006**: L'import est 100% idempotent : executer l'import N fois produit le meme resultat qu'une seule execution
