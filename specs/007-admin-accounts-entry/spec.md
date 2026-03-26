# Feature Specification: Saisie et stockage des comptes administratifs

**Feature Branch**: `007-admin-accounts-entry`
**Created**: 2026-03-21
**Status**: Draft
**Input**: User description: "Feature 5 : Saisie et stockage des comptes administratifs"

## Clarifications

### Session 2026-03-21

- Q: Quelle strategie de sauvegarde pour la saisie des recettes et depenses ? → A: Sauvegarde automatique ligne par ligne avec synchronisation des donnees (chaque modification d'une cellule est persistee immediatement)
- Q: La saisie est-elle bloquee quand un compte est publie ? → A: Non, la saisie reste possible quel que soit le statut. Toute modification sur un compte publie est tracee (utilisateur responsable et detail de la modification) dans un journal
- Q: Quels roles peuvent creer, saisir et publier des comptes ? → A: Admin et editor peuvent creer et saisir ; seul admin peut publier/depublier
- Q: Les programmes de depenses peuvent-ils etre supprimes ou renommes ? → A: Renommage et suppression libres de tous les programmes, y compris les 3 par defaut
- Q: Le tableau d'equilibre doit-il distinguer operations reelles et operations d'ordre ? → A: Oui, la distinction est presente dans la structure du template (lignes d'ordre identifiees par leur position apres le sous-total des operations reelles). Le tableau d'equilibre reproduit cette separation pour correspondre au document officiel

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Creer un compte administratif pour une collectivite (Priority: P1)

Un administrateur souhaite initier la saisie du compte administratif d'une collectivite territoriale (commune, region ou province) pour une annee d'exercice donnee. Il selectionne le type de collectivite, la collectivite concernee dans la hierarchie geographique existante, et l'annee d'exercice. Le systeme cree un compte administratif en mode brouillon, pre-initialise avec la structure du template de recettes et 3 programmes de depenses par defaut.

**Why this priority**: Sans creation du compte administratif, aucune saisie de donnees n'est possible. C'est le point d'entree obligatoire de tout le processus.

**Independent Test**: Peut etre teste en creant un compte administratif pour une commune existante et en verifiant que le brouillon est cree avec les structures vides pret a recevoir les donnees.

**Acceptance Scenarios**:

1. **Given** des collectivites existent dans le systeme, **When** l'administrateur selectionne "commune", choisit Andrafiabe, et saisit l'annee 2023, **Then** un compte administratif est cree en statut "brouillon" lie a cette commune et cette annee
2. **Given** un compte administratif est cree pour une commune, **When** l'administrateur consulte le compte, **Then** 3 programmes de depenses sont pre-crees (Administration et Coordination, Developpement economique et social, Sante)
3. **Given** un compte administratif existe deja pour la commune Andrafiabe en 2023, **When** l'administrateur tente d'en creer un autre pour la meme commune et la meme annee, **Then** le systeme refuse la creation et affiche un message d'erreur indiquant le doublon
4. **Given** l'administrateur selectionne "region" comme type de collectivite, **When** il remplit le formulaire, **Then** la selection de commune n'est pas requise (seule la region est necessaire)
5. **Given** l'administrateur est sur la page de creation, **When** il ne renseigne pas l'annee d'exercice, **Then** le systeme refuse la creation (annee obligatoire)

---

### User Story 2 - Saisir les donnees de recettes (Priority: P1)

Un administrateur ouvre le volet recettes d'un compte administratif existant et saisit les valeurs financieres pour chaque ligne de compte. Le tableau de saisie reproduit la structure hierarchique du template de recettes officiel : lignes de comptes a 3 niveaux (2, 3 et 4 chiffres), separees en sections Fonctionnement et Investissement. Pour chaque ligne de detail (niveau 3, comptes a 4 chiffres), l'administrateur saisit les valeurs dans les colonnes editables : budget primitif, budget additionnel, modifications, OR admis et recouvrement. Les colonnes calculees (previsions definitives, reste a recouvrer, taux d'execution) et les sommes hierarchiques des niveaux superieurs sont calculees dynamiquement par le systeme a chaque consultation.

**Why this priority**: Les recettes constituent la premiere moitie du compte administratif. Leur saisie est aussi critique que la creation du compte.

**Independent Test**: Peut etre teste en saisissant les recettes d'Andrafiabe 2023 et en verifiant que les totaux calcules correspondent au document officiel.

**Acceptance Scenarios**:

1. **Given** un compte administratif existe en brouillon, **When** l'administrateur accede a la page de saisie des recettes, **Then** un tableau editable affiche toutes les lignes du template recettes avec les colonnes appropriees, les lignes de detail (Niv3) etant editables et les lignes de niveau superieur en lecture seule
2. **Given** l'administrateur saisit les valeurs budget primitif, budget additionnel et modifications pour une ligne, **When** le systeme recalcule, **Then** la prevision definitive est egale a la somme de ces 3 valeurs
3. **Given** l'administrateur saisit OR admis et recouvrement pour une ligne, **When** le systeme recalcule, **Then** le reste a recouvrer est egal a OR admis moins recouvrement, et le taux d'execution est egal a OR admis divise par les previsions definitives
4. **Given** des lignes de niveau 3 ont des valeurs saisies, **When** le systeme recalcule, **Then** les lignes de niveau 2 et 1 affichent la somme de leurs enfants respectifs pour chaque colonne numerique
5. **Given** les previsions definitives d'une ligne sont a zero, **When** le systeme calcule le taux d'execution, **Then** le resultat affiche est "N/A" ou 0% (pas d'erreur de division par zero)
6. **Given** l'administrateur saisit des valeurs partielles (certaines lignes vides), **When** le systeme synchronise, **Then** les lignes sans valeur sont traitees comme des zeros dans les calculs
7. **Given** l'administrateur modifie une cellule, **When** il quitte la cellule, **Then** la valeur est automatiquement persistee et un indicateur de synchronisation confirme l'enregistrement

---

### User Story 3 - Saisir les depenses par programme (Priority: P1)

Un administrateur ouvre le volet depenses d'un compte administratif et saisit les donnees financieres pour chaque programme. Par defaut, 3 programmes existent (Administration et Coordination, Developpement economique et social, Sante). L'administrateur navigue entre les programmes via des onglets. Pour chaque programme, il saisit les valeurs dans un tableau identique au template de depenses : lignes de comptes a 3 niveaux, sections Fonctionnement et Investissement. Les colonnes editables sont : budget primitif, budget additionnel, modifications, engagement, mandat admis et paiement. Les colonnes calculees (previsions definitives, reste a payer, taux d'execution) et les sommes hierarchiques sont calculees dynamiquement.

**Why this priority**: Les depenses constituent la seconde moitie du compte administratif. La saisie par programme est la particularite cle du systeme.

**Independent Test**: Peut etre teste en saisissant les depenses du Programme I d'Andrafiabe 2023 et en verifiant la coherence des calculs.

**Acceptance Scenarios**:

1. **Given** un compte administratif existe avec 3 programmes par defaut, **When** l'administrateur accede a la page de saisie des depenses, **Then** 3 onglets sont affiches (un par programme) avec le numero et l'intitule de chaque programme
2. **Given** l'administrateur est sur l'onglet du Programme I, **When** il saisit les valeurs pour les lignes de detail, **Then** les colonnes calculees sont mises a jour : previsions definitives = budget primitif + budget additionnel + modifications ; reste a payer = mandat admis - paiement ; taux d'execution = mandat admis / previsions definitives
3. **Given** l'administrateur souhaite un 4eme programme, **When** il clique sur "Ajouter un programme", **Then** un nouveau programme est cree avec un numero sequentiel et un intitule modifiable, et un nouvel onglet apparait
5. **Given** un programme existe avec des depenses saisies, **When** l'administrateur supprime ce programme, **Then** le programme et toutes ses lignes de depense sont supprimes apres confirmation
6. **Given** un programme existe, **When** l'administrateur modifie son intitule, **Then** le nouvel intitule est affiche dans l'onglet et dans les recapitulatifs
4. **Given** des depenses sont saisies dans plusieurs programmes, **When** le systeme recalcule les sommes hierarchiques, **Then** chaque programme a ses propres totaux independants (les programmes ne s'additionnent pas entre eux dans la vue de saisie)

---

### User Story 4 - Consulter les recapitulatifs et l'equilibre (Priority: P2)

Un administrateur souhaite verifier la coherence globale du compte administratif avant publication. Il accede a la page de recapitulation qui presente trois vues calculees en lecture seule : (1) le recapitulatif des recettes, qui synthetise les recettes par categorie de niveau 1, (2) le recapitulatif des depenses croise par programme, qui presente les montants (mandat, paiement, reste a payer) ventiles par programme et par categorie de compte, et (3) le tableau d'equilibre qui met en regard les recettes et les depenses avec le resultat (excedent ou deficit). Toutes ces vues sont calculees dynamiquement a partir des donnees saisies, rien n'est stocke.

**Why this priority**: Les recapitulatifs sont essentiels pour la verification et la coherence, mais ils dependent des donnees saisies dans les stories P1.

**Independent Test**: Peut etre teste en saisissant les donnees completes d'Andrafiabe 2023 et en comparant les recapitulatifs calcules avec les feuilles RECAP RECETTE, RECAP DEP et EQUILIBRE du document officiel.

**Acceptance Scenarios**:

1. **Given** des recettes sont saisies, **When** l'administrateur accede au recapitulatif des recettes, **Then** un tableau affiche une ligne par categorie de niveau 1 (comptes 70 a 77) avec les previsions definitives, OR admis, recouvrement et reste a recouvrer, plus des sous-totaux par section (Fonctionnement, Investissement)
2. **Given** des depenses sont saisies dans 3 programmes, **When** l'administrateur accede au recapitulatif des depenses, **Then** un tableau croise affiche les categories de comptes en lignes et les programmes en colonnes, avec pour chaque croisement les montants mandat, paiement et reste a payer, plus une colonne de total inter-programmes
3. **Given** recettes et depenses sont saisies, **When** l'administrateur accede au tableau d'equilibre, **Then** les depenses et recettes sont presentees cote a cote par section (fonctionnement puis investissement), en separant operations reelles et operations d'ordre au sein de chaque section, avec le calcul de l'excedent ou du deficit par section et au global
4. **Given** les donnees d'Andrafiabe 2023 sont integralement saisies, **When** le systeme calcule le resultat definitif dans le tableau d'equilibre, **Then** le resultat correspond a la valeur du document officiel (recettes fonctionnement : 51 988 701 Ar, depenses fonctionnement : 41 849 200 Ar, investissement : 2 220 000 Ar, resultat definitif : 7 939 501 Ar) avec une marge d'erreur inferieure a 1 Ar

---

### User Story 5 - Publier et gerer le statut d'un compte administratif (Priority: P2)

Un administrateur ayant termine la saisie souhaite publier le compte administratif pour le rendre visible. Il peut aussi depublier un compte publie pour le corriger. La liste des comptes permet de filtrer par type de collectivite, collectivite specifique et annee d'exercice.

**Why this priority**: La publication est l'etape finale du workflow. La liste filtree facilite la gestion quotidienne.

**Independent Test**: Peut etre teste en publiant un compte brouillon et en verifiant le changement de statut, puis en le depubliant.

**Acceptance Scenarios**:

1. **Given** un compte administratif est en statut brouillon, **When** l'administrateur clique sur "Publier", **Then** le statut passe a "publie"
2. **Given** un compte administratif est publie, **When** l'administrateur clique sur "Depublier", **Then** le statut repasse a "brouillon"
5. **Given** un compte administratif est publie, **When** l'administrateur modifie une valeur de recette ou depense, **Then** la modification est enregistree et le systeme trace l'utilisateur, la date, la ligne modifiee, l'ancienne et la nouvelle valeur dans un journal
3. **Given** plusieurs comptes existent, **When** l'administrateur accede a la liste des comptes, **Then** il peut filtrer par type de collectivite (province, region, commune), par collectivite specifique et par annee d'exercice
4. **Given** la liste des comptes est affichee, **When** l'administrateur consulte un compte, **Then** il voit le statut actuel (brouillon ou publie), la collectivite, l'annee d'exercice, et la date de derniere modification

---

### Edge Cases

- Que se passe-t-il si la synchronisation automatique echoue (perte de connexion) ? Le systeme affiche un indicateur d'erreur sur les cellules non synchronisees et retente automatiquement lorsque la connexion est retablie
- Que se passe-t-il si une ligne de template est ajoutee apres qu'un compte a deja ete cree ? Les nouvelles lignes apparaissent sans valeur (traitees comme zero) lors de la prochaine consultation
- Que se passe-t-il si deux administrateurs modifient le meme compte simultanement ? Le dernier a sauvegarder ecrase les donnees de l'autre (pas de gestion de conflit dans cette version)
- Que se passe-t-il si un programme de depenses est vide (aucune ligne saisie) ? Il est inclus dans les recapitulatifs avec des valeurs a zero
- Que se passe-t-il si toutes les recettes et depenses sont a zero ? Le tableau d'equilibre affiche un resultat de zero sans erreur
- Que se passe-t-il si l'administrateur supprime tous les programmes de depenses ? Le systeme autorise un compte sans programme ; les recapitulatifs de depenses et le tableau d'equilibre affichent des valeurs a zero cote depenses
- Que se passe-t-il si une collectivite est supprimee alors qu'un compte y est associe ? La suppression de la collectivite est bloquee (contrainte existante RESTRICT sur les FK geographiques)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le systeme DOIT permettre aux utilisateurs de role admin ou editor de creer un compte administratif en associant un type de collectivite (province, region ou commune), une collectivite specifique et une annee d'exercice
- **FR-002**: Le systeme DOIT empecher la creation de deux comptes administratifs pour la meme collectivite et la meme annee d'exercice
- **FR-003**: Le systeme DOIT creer automatiquement 3 programmes de depenses par defaut lors de la creation d'un compte (Administration et Coordination, Developpement economique et social, Sante)
- **FR-004**: Le systeme DOIT permettre l'ajout, le renommage et la suppression de programmes de depenses, y compris les 3 programmes par defaut
- **FR-005**: Le systeme DOIT permettre la saisie des valeurs de recettes ligne par ligne, en ne rendant editables que les lignes de detail (niveau 3, comptes a 4 chiffres), avec sauvegarde automatique a chaque modification de cellule
- **FR-006**: Le systeme DOIT permettre la saisie des valeurs de depenses par programme, avec la meme structure de saisie que les recettes (lignes de detail editables, sauvegarde automatique)
- **FR-019**: Le systeme DOIT synchroniser automatiquement chaque valeur modifiee avec le serveur et afficher un indicateur visuel de l'etat de synchronisation (en cours, reussi, erreur)
- **FR-007**: Les colonnes editables pour les recettes DOIVENT etre : budget primitif, budget additionnel, modifications, OR admis, recouvrement
- **FR-008**: Les colonnes editables pour les depenses DOIVENT etre : budget primitif, budget additionnel, modifications, engagement, mandat admis, paiement
- **FR-009**: Le systeme DOIT calculer dynamiquement a chaque consultation (sans stockage) les colonnes derivees : previsions definitives (somme des 3 budgets), reste a recouvrer/payer, taux d'execution
- **FR-010**: Le systeme DOIT calculer dynamiquement les sommes hierarchiques : chaque ligne de niveau 1 et 2 affiche la somme de ses enfants directs pour toutes les colonnes numeriques
- **FR-011**: Le systeme DOIT fournir un recapitulatif des recettes par categorie de niveau 1 avec sous-totaux par section (fonctionnement, investissement)
- **FR-012**: Le systeme DOIT fournir un recapitulatif des depenses croise entre categories de comptes (lignes) et programmes (colonnes), avec les montants mandat, paiement et reste a payer
- **FR-013**: Le systeme DOIT fournir un tableau d'equilibre mettant en regard recettes et depenses par section (fonctionnement, investissement), en distinguant les operations reelles et les operations d'ordre au sein de chaque section, avec calcul de l'excedent ou du deficit par section et au global
- **FR-014**: Le systeme DOIT gerer un cycle de vie brouillon/publie pour chaque compte administratif, avec possibilite de publier et depublier. La saisie reste possible quel que soit le statut. Seul le role admin peut publier ou depublier
- **FR-020**: Le systeme DOIT enregistrer un journal des modifications effectuees sur un compte publie, incluant l'identite de l'utilisateur responsable, la date et le detail de la modification (ligne, colonne, ancienne et nouvelle valeur)
- **FR-015**: Le systeme DOIT permettre de filtrer la liste des comptes par type de collectivite, collectivite specifique et annee d'exercice
- **FR-016**: L'annee d'exercice DOIT etre obligatoire pour tout compte administratif
- **FR-017**: Si le type de collectivite est "region" ou "province", la selection d'une commune NE DOIT PAS etre requise
- **FR-018**: Les valeurs de recettes et de depenses DOIVENT etre stockees sous forme structuree (cle-valeur par colonne) pour chaque ligne de compte, en reference au template de structure

### Key Entities

- **Compte administratif (CompteAdministratif)**: Represente le document comptable annuel d'une collectivite. Lie a un type de collectivite, une collectivite specifique (via son identifiant), une annee d'exercice et un statut (brouillon ou publie). Un seul compte par couple collectivite-annee. Associe a un createur (utilisateur) et des horodatages de creation et modification.
- **Ligne de recette (RecetteLine)**: Represente les valeurs financieres saisies pour une ligne du template de recettes dans un compte administratif donne. Chaque ligne reference une ligne de template et stocke les valeurs sous forme de paires cle-valeur (budget primitif, budget additionnel, modifications, OR admis, recouvrement).
- **Programme de depenses (DepenseProgram)**: Represente un programme budgetaire au sein d'un compte administratif. Possede un numero d'ordre et un intitule. Par defaut 3 programmes, extensible dynamiquement.
- **Ligne de depense (DepenseLine)**: Represente les valeurs financieres saisies pour une ligne du template de depenses au sein d'un programme donne. Reference une ligne de template et stocke les valeurs (budget primitif, budget additionnel, modifications, engagement, mandat admis, paiement).

## Assumptions

- Les templates de comptes (recettes et depenses) issus de la Feature 006 sont deja importes et actifs dans le systeme avant toute creation de compte administratif
- La hierarchie geographique (provinces, regions, communes) est deja en place (Feature 005)
- Le systeme d'authentification et les roles admin/editor sont fonctionnels (Feature 004)
- Les 3 programmes par defaut (Administration et Coordination, Developpement economique et social, Sante) correspondent a la nomenclature officielle malgache
- Les valeurs financieres sont des entiers (en Ariary, pas de decimales)
- Les formules de calcul (sommes hierarchiques, colonnes derivees, recapitulatifs, equilibre) sont toutes calculees cote serveur a chaque lecture et jamais persistees
- Un compte administratif reference les lignes de template par identifiant, ce qui permet de retrouver la structure (code, intitule, niveau, section) depuis le template
- Les donnees du compte administratif de la Commune d'Andrafiabe 2023 servent de jeu de test de reference pour valider les calculs

## Out of Scope

- Affichage public des comptes administratifs (feature separee)
- Import automatique de comptes depuis des fichiers Excel externes
- Generation de rapports PDF ou export Excel des comptes
- Workflows de validation multi-etapes (relecture, approbation hierarchique)
- Audit trail complet sur les comptes en brouillon (seules les modifications sur les comptes publies sont tracees)
- Gestion des conflits d'edition simultanee
- Comparaison inter-annuelle des comptes administratifs
- Les annexes du compte administratif (engagements non ordonnances, recettes non recouvrees, compte matiere)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un administrateur peut creer un compte administratif et commencer la saisie des recettes en moins de 2 minutes depuis la page de liste
- **SC-002**: Les recapitulatifs calcules pour les donnees d'Andrafiabe 2023 correspondent aux valeurs du document officiel avec une marge d'erreur inferieure a 1 Ariary
- **SC-003**: La page de saisie des recettes ou depenses (jusqu'a 289 lignes) se charge et affiche les calculs en moins de 3 secondes
- **SC-004**: Un administrateur peut naviguer entre les onglets de programmes de depenses sans delai perceptible (moins de 1 seconde)
- **SC-005**: Le tableau d'equilibre presente les resultats corrects des qu'au moins une ligne de recette et une ligne de depense sont saisies
- **SC-006**: 100% des formules de calcul (previsions definitives, restes, taux d'execution, sommes hierarchiques) produisent les resultats attendus sur le jeu de test Andrafiabe 2023
