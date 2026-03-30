# Feature Specification: Service de signalement GlobalLeaks

**Feature Branch**: `017-globaleaks-service`
**Created**: 2026-03-30
**Status**: Draft
**Input**: User description: "installer et configurer un service GlobalLeaks pour ce projet, voici la documentation https://docs.globaleaks.org/en/stable/setup/installation.html"

## Clarifications

### Session 2026-03-30

- Q: Mode d'acces au service GlobalLeaks (sous-domaine dedie, proxy, ou domaine separe) ? → A: Instance sur un domaine independant, partagee entre plusieurs sites (pas uniquement PCQVP).
- Q: Politique de retention des signalements ? → A: Conservation indefinie, suppression manuelle par l'administrateur.
- Q: Activer l'acces Tor (.onion) pour renforcer l'anonymat ? → A: Oui, acces Tor active en plus de l'acces HTTPS classique.
- Q: Organisation des canaux de signalement ? → A: Canaux thematiques : fiscalite/paiements, environnement, social/communautaire, gouvernance/corruption.
- Q: Domaine de l'instance GlobalLeaks ? → A: `alerte.miningobs.mg`, avec acces par IP/port en attendant la configuration DNS du sous-domaine.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Signalement anonyme par un lanceur d'alerte (Priority: P1)

Un citoyen ou un acteur de la societe civile souhaite signaler de maniere anonyme une irregularite liee aux industries extractives de Madagascar. Il accede a la plateforme PCQVP, navigue vers la section de signalement, et est redirige vers l'interface GlobalLeaks securisee. Il remplit le formulaire de signalement, attache des documents justificatifs, et recoit un code d'acces unique pour suivre son signalement ulterieurement.

**Why this priority**: Le signalement anonyme est la raison d'etre de l'integration GlobalLeaks. Sans cette fonctionnalite, le service n'a aucune utilite.

**Independent Test**: Peut etre teste en accedant a l'interface de signalement, en soumettant un rapport de test, et en verifiant que le code d'acces permet de retrouver le signalement.

**Acceptance Scenarios**:

1. **Given** un visiteur sur la plateforme PCQVP, **When** il clique sur le lien/bouton de signalement, **Then** il est dirige vers l'interface securisee de GlobalLeaks pour soumettre son rapport.
2. **Given** un lanceur d'alerte qui remplit le formulaire de signalement, **When** il soumet le formulaire avec des pieces jointes, **Then** il recoit un code d'acces unique et une confirmation de soumission.
3. **Given** un lanceur d'alerte avec un code d'acces, **When** il retourne sur la plateforme et saisit son code, **Then** il peut consulter l'etat de son signalement et echanger des messages avec les destinataires.

---

### User Story 2 - Consultation et traitement des signalements par un destinataire (Priority: P2)

Un administrateur ou un membre designe de l'equipe PCQVP se connecte a l'interface d'administration de GlobalLeaks pour consulter les signalements recus. Il peut lire les rapports, telecharger les pieces jointes, envoyer des messages au lanceur d'alerte (de maniere anonyme), et marquer les signalements comme traites.

**Why this priority**: Sans destinataires capables de traiter les signalements, le service ne peut pas remplir sa mission.

**Independent Test**: Peut etre teste en se connectant a l'interface destinataire, en consultant un signalement de test, et en envoyant un commentaire.

**Acceptance Scenarios**:

1. **Given** un destinataire authentifie sur GlobalLeaks, **When** il accede a la liste des signalements, **Then** il voit tous les signalements qui lui sont assignes avec leur statut.
2. **Given** un destinataire qui consulte un signalement, **When** il envoie un message au lanceur d'alerte, **Then** le message est visible par le lanceur d'alerte lors de sa prochaine consultation.
3. **Given** un destinataire qui traite un signalement, **When** il telecharge les pieces jointes, **Then** les fichiers sont accessibles et dechiffres localement.

---

### User Story 3 - Navigation depuis la plateforme PCQVP vers GlobalLeaks (Priority: P2)

Un visiteur de la plateforme PCQVP decouvre facilement le mecanisme de signalement. Un lien ou bouton clairement visible dans l'interface principale de PCQVP le dirige vers le service GlobalLeaks heberge sur `alerte.miningobs.mg` (domaine independant partage entre plusieurs sites). L'experience est coherente visuellement.

**Why this priority**: L'integration dans le parcours utilisateur de PCQVP est essentielle pour la decouvrabilite du service.

**Independent Test**: Peut etre teste en naviguant sur la plateforme PCQVP et en verifiant la presence et le fonctionnement du lien vers GlobalLeaks.

**Acceptance Scenarios**:

1. **Given** un visiteur sur la page d'accueil de PCQVP, **When** il cherche a signaler une irregularite, **Then** il trouve un point d'entree clair vers le service de signalement sur `alerte.miningobs.mg`.
2. **Given** un visiteur qui clique sur le lien de signalement, **When** la page GlobalLeaks se charge, **Then** l'apparence est coherente avec la charte graphique de PCQVP (logo, couleurs).
3. **Given** le sous-domaine `alerte.miningobs.mg` non encore configure en DNS, **When** un utilisateur doit acceder au service, **Then** le service est accessible directement par IP/port.

---

### User Story 4 - Administration et configuration de GlobalLeaks (Priority: P3)

Un administrateur systeme configure la plateforme GlobalLeaks : personnalisation du questionnaire de signalement adapte au contexte des industries extractives, configuration des langues (francais, malgache), parametrage des notifications, et gestion des comptes destinataires.

**Why this priority**: La configuration initiale est necessaire mais se fait une seule fois. Elle peut etre affinee apres le lancement.

**Independent Test**: Peut etre teste en accedant a l'interface d'administration, en modifiant le questionnaire et les parametres, et en verifiant que les changements sont appliques.

**Acceptance Scenarios**:

1. **Given** un administrateur authentifie, **When** il personnalise le questionnaire de signalement, **Then** les modifications sont visibles pour les futurs lanceurs d'alerte.
2. **Given** un administrateur, **When** il configure les langues disponibles (francais et malgache), **Then** l'interface de signalement est accessible dans ces deux langues.
3. **Given** un administrateur, **When** il ajoute un nouveau destinataire, **Then** ce destinataire recoit les nouveaux signalements selon les regles de distribution configurees.

---

### Edge Cases

- Que se passe-t-il si le service GlobalLeaks est temporairement indisponible ? Le lien depuis PCQVP doit afficher un message d'erreur adapte.
- Comment le systeme gere-t-il les soumissions avec des fichiers tres volumineux ? Les limites de taille doivent etre clairement communiquees au lanceur d'alerte.
- Que se passe-t-il si un lanceur d'alerte perd son code d'acces ? Il ne peut pas recuperer son signalement (par conception, pour preserver l'anonymat).
- Comment le systeme se comporte-t-il en cas de tentative d'acces malveillant ou de spam de signalements ?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le systeme DOIT fournir une instance GlobalLeaks operationnelle deployee via Docker en tant que service compagnon du projet existant.
- **FR-002**: Le systeme DOIT permettre a un lanceur d'alerte de soumettre un signalement de maniere anonyme sans creer de compte.
- **FR-003**: Le systeme DOIT fournir un code d'acces unique au lanceur d'alerte apres chaque soumission pour le suivi ulterieur.
- **FR-004**: Le systeme DOIT permettre aux lanceurs d'alerte de joindre des fichiers (documents, images) a leur signalement.
- **FR-005**: Le systeme DOIT permettre une communication bidirectionnelle anonyme entre les lanceurs d'alerte et les destinataires.
- **FR-006**: Le systeme DOIT proposer un questionnaire de signalement adapte au contexte des industries extractives, avec 4 canaux thematiques : fiscalite/paiements, environnement, social/communautaire, gouvernance/corruption. Chaque canal collecte : type d'irregularite, localisation geographique, entites impliquees, periode concernee.
- **FR-007**: Le systeme DOIT etre disponible en francais et en malgache au minimum.
- **FR-008**: Le systeme DOIT notifier les destinataires lors de la reception d'un nouveau signalement.
- **FR-009**: Le systeme DOIT chiffrer les donnees des signalements au repos et en transit, et proposer un acces via service Tor (.onion) en plus de l'acces HTTPS classique.
- **FR-010**: Le systeme DOIT permettre aux destinataires de gerer le cycle de vie des signalements (nouveau, en cours, traite, archive).
- **FR-011**: La plateforme PCQVP DOIT integrer un lien ou bouton visible dirigeant les utilisateurs vers le service de signalement.
- **FR-012**: Le systeme DOIT inclure une procedure de sauvegarde et restauration des donnees de signalement.
- **FR-013**: Le systeme DOIT etre accessible sur le domaine `alerte.miningobs.mg` (instance independante partagee entre plusieurs sites), avec acces temporaire par IP/port en attendant la configuration DNS.
- **FR-014**: Le systeme DOIT conserver les signalements de maniere indefinie ; la suppression se fait manuellement par l'administrateur.

### Key Entities

- **Signalement (Report)**: Soumission anonyme contenant les details de l'irregularite, les pieces jointes, les messages echanges, et un statut de traitement. Identifie par un code d'acces unique.
- **Lanceur d'alerte (Whistleblower)**: Personne anonyme soumettant un signalement. N'a pas de compte, identifie uniquement par le code d'acces de son signalement.
- **Destinataire (Recipient)**: Membre de l'equipe PCQVP autorise a recevoir et traiter les signalements. Dispose d'un compte authentifie sur GlobalLeaks.
- **Questionnaire**: Formulaire structure definissant les informations a collecter lors d'un signalement, personnalise pour le contexte des industries extractives.
- **Canal (Channel)**: Categorie thematique de signalement (fiscalite/paiements, environnement, social/communautaire, gouvernance/corruption) permettant de router les rapports vers les destinataires appropries.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un lanceur d'alerte peut soumettre un signalement complet (formulaire + pieces jointes) en moins de 10 minutes.
- **SC-002**: Le service de signalement est accessible 99% du temps sur une periode mensuelle.
- **SC-003**: Un destinataire peut acceder a un nouveau signalement et envoyer une premiere reponse en moins de 5 minutes apres connexion.
- **SC-004**: 100% des donnees de signalement sont chiffrees au repos et en transit.
- **SC-005**: L'interface de signalement est disponible en francais et en malgache avec une couverture de traduction de 100% des elements d'interface.
- **SC-006**: Le lien vers le service de signalement est accessible en moins de 2 clics depuis n'importe quelle page de la plateforme PCQVP.
- **SC-007**: La procedure de sauvegarde et restauration permet une reprise complete du service en moins de 1 heure.

## Assumptions

- GlobalLeaks sera deploye via Docker en tant que service independant sur le serveur, avec son propre `docker-compose.yml` ou ajoute a l'infrastructure existante.
- Le service GlobalLeaks sera accessible sur `alerte.miningobs.mg` (acces par IP/port en attendant le DNS). L'instance est partagee entre PCQVP et d'autres sites.
- L'infrastructure serveur existante dispose de suffisamment de ressources (RAM, stockage) pour heberger le service GlobalLeaks en plus des services existants.
- Les utilisateurs cibles (citoyens malgaches, societe civile) disposent d'un acces internet basique et utilisent des navigateurs modernes.
- La personnalisation visuelle de GlobalLeaks (logo, couleurs) sera realisee via les options de configuration integrees de GlobalLeaks, sans modification du code source.
- La gestion des utilisateurs destinataires sera independante du systeme d'authentification de la plateforme PCQVP (comptes separes sur GlobalLeaks).
- Les notifications aux destinataires se feront par email via le service de messagerie existant ou un service dedie configure dans GlobalLeaks.
- GlobalLeaks version 5.x sera utilisee, conformement a la documentation officielle fournie.
- Le service Tor (.onion) sera active nativement dans GlobalLeaks pour offrir un canal d'acces anonyme renforce.
- Les signalements sont conserves indefiniment ; seul l'administrateur peut les supprimer manuellement.
