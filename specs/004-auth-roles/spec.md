# Feature Specification: Authentification et gestion des rôles

**Feature Branch**: `004-auth-roles`
**Created**: 2026-03-20
**Status**: Draft
**Input**: User description: "Feature 2 : Authentification et gestion des rôles avec endpoints backend (register, login, refresh, me), modèle User, middleware de contrôle d'accès, et interface frontend (login, layout admin avec dark/light mode, middleware auth)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Connexion administrateur (Priority: P1)

Un administrateur accède à la page de connexion de l'espace admin. Il saisit son adresse email et son mot de passe. Après validation, il est redirigé vers le tableau de bord admin et peut naviguer dans l'ensemble des sections protégées.

**Why this priority**: Sans authentification fonctionnelle, aucune fonctionnalité admin ne peut être utilisée. C'est le fondement de tout l'espace d'administration.

**Independent Test**: Peut être testé en se connectant avec un compte admin existant et en vérifiant l'accès au tableau de bord.

**Acceptance Scenarios**:

1. **Given** un administrateur avec un compte actif, **When** il saisit ses identifiants corrects sur la page de connexion, **Then** il est authentifié et redirigé vers l'espace admin.
2. **Given** un utilisateur avec des identifiants incorrects, **When** il tente de se connecter, **Then** un message d'erreur explicite est affiché et l'accès est refusé.
3. **Given** un utilisateur avec un compte désactivé, **When** il tente de se connecter, **Then** l'accès est refusé avec un message approprié.

---

### User Story 2 - Protection des routes admin (Priority: P1)

Tout utilisateur non authentifié qui tente d'accéder à une page de l'espace admin est automatiquement redirigé vers la page de connexion.

**Why this priority**: La sécurité des accès est aussi fondamentale que l'authentification elle-même.

**Independent Test**: Peut être testé en accédant directement à une URL admin sans être connecté.

**Acceptance Scenarios**:

1. **Given** un utilisateur non authentifié, **When** il accède à une URL de l'espace admin, **Then** il est redirigé vers la page de connexion.
2. **Given** un utilisateur authentifié, **When** il accède à une URL de l'espace admin, **Then** la page s'affiche normalement.
3. **Given** un utilisateur authentifié qui se déconnecte, **When** il tente d'accéder à l'espace admin, **Then** il est redirigé vers la page de connexion.

---

### User Story 3 - Initialisation du premier administrateur (Priority: P1)

Lors du premier déploiement de la plateforme, un administrateur initial est créé automatiquement via un script de configuration. Cela garantit qu'au moins un compte admin existe pour commencer à utiliser le système.

**Why this priority**: Sans administrateur initial, personne ne peut accéder au système ni créer d'autres comptes.

**Independent Test**: Peut être testé en exécutant le script d'initialisation puis en se connectant avec les identifiants de l'admin initial.

**Acceptance Scenarios**:

1. **Given** une base de données vide, **When** le script d'initialisation est exécuté, **Then** un compte administrateur est créé avec les identifiants configurés.
2. **Given** un administrateur initial existant, **When** le script est relancé, **Then** aucun doublon n'est créé.

---

### User Story 4 - Création de comptes par un administrateur (Priority: P2)

Un administrateur connecté peut créer de nouveaux comptes utilisateurs en spécifiant l'adresse email, le mot de passe et le rôle (administrateur ou éditeur). Seuls les administrateurs ont la permission de créer des comptes.

**Why this priority**: La capacité de gérer les utilisateurs est essentielle pour permettre la collaboration sur la plateforme. Dépend de l'authentification (P1).

**Independent Test**: Peut être testé en créant un nouveau compte via l'interface puis en vérifiant que ce compte peut se connecter.

**Acceptance Scenarios**:

1. **Given** un administrateur connecté, **When** il crée un compte avec un email valide, un mot de passe et un rôle, **Then** le compte est créé et l'utilisateur peut se connecter.
2. **Given** un éditeur connecté, **When** il tente de créer un compte, **Then** l'action est refusée (accès non autorisé).
3. **Given** un administrateur connecté, **When** il crée un compte avec un email déjà existant, **Then** une erreur de doublon est affichée.

---

### User Story 5 - Navigation admin avec identité utilisateur et thème (Priority: P2)

L'espace admin dispose d'une interface avec une barre latérale de navigation et un en-tête affichant le nom de l'utilisateur connecté, un bouton de déconnexion, et un sélecteur de thème (mode clair / mode sombre). Le choix de thème est mémorisé pour les visites suivantes.

**Why this priority**: Fournit le cadre d'interface pour toutes les futures fonctionnalités admin. Le choix dark/light mode améliore le confort visuel des utilisateurs.

**Independent Test**: Peut être testé en vérifiant visuellement la présence de la sidebar, du nom utilisateur, du bouton de déconnexion et du sélecteur de thème après connexion.

**Acceptance Scenarios**:

1. **Given** un utilisateur connecté dans l'espace admin, **When** la page se charge, **Then** l'en-tête affiche son email, un bouton de déconnexion et un sélecteur de thème.
2. **Given** un utilisateur connecté, **When** il clique sur le bouton de déconnexion, **Then** sa session est terminée et il est redirigé vers la page de connexion.
3. **Given** un utilisateur en mode clair, **When** il active le mode sombre, **Then** l'interface passe en thème sombre et ce choix est conservé lors de sa prochaine visite.
4. **Given** un utilisateur sans préférence enregistrée, **When** il accède à l'espace admin, **Then** le thème par défaut correspond à la préférence système du navigateur.

---

### User Story 6 - Maintien de session et renouvellement automatique (Priority: P3)

Un utilisateur connecté reste authentifié pendant sa session de travail. Lorsque sa session courte expire, le système renouvelle automatiquement son accès sans intervention manuelle, tant que sa session longue est valide.

**Why this priority**: Assure une expérience fluide sans déconnexions intempestives, mais n'est pas bloquant pour les fonctionnalités de base.

**Independent Test**: Peut être testé en vérifiant qu'un utilisateur reste connecté après l'expiration de la session courte (30 minutes), jusqu'à expiration de la session longue (7 jours).

**Acceptance Scenarios**:

1. **Given** un utilisateur connecté dont la session courte a expiré, **When** il effectue une action, **Then** le système renouvelle automatiquement sa session sans déconnexion.
2. **Given** un utilisateur dont la session longue a expiré, **When** il tente une action, **Then** il est redirigé vers la page de connexion.

---

### Edge Cases

- Que se passe-t-il si un utilisateur tente de se connecter avec un email inexistant ? Le système affiche un message d'erreur générique (pas de distinction entre email inconnu et mot de passe incorrect, pour des raisons de sécurité).
- Que se passe-t-il si les deux sessions (courte et longue) expirent simultanément ? L'utilisateur est redirigé vers la page de connexion.
- Que se passe-t-il si un administrateur désactive son propre compte ? L'action devrait être interdite pour éviter de verrouiller le système.
- Que se passe-t-il si le dernier administrateur tente d'être supprimé ou désactivé ? Le système doit empêcher cette action.
- Que se passe-t-il en cas de requêtes simultanées avec un token expiré ? Chaque requête doit pouvoir déclencher un renouvellement sans conflit.
- Que se passe-t-il après 5 tentatives de connexion échouées consécutives ? Le compte est temporairement verrouillé pendant 15 minutes. L'utilisateur est informé du verrouillage sans détail sur la durée exacte.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT permettre l'authentification des utilisateurs par email et mot de passe.
- **FR-002**: Le système DOIT gérer deux rôles distincts : administrateur et éditeur.
- **FR-003**: Seuls les administrateurs DOIVENT pouvoir créer de nouveaux comptes utilisateurs.
- **FR-004**: Le système DOIT fournir un mécanisme de session courte (30 minutes) et de session longue (7 jours).
- **FR-005**: Le système DOIT renouveler automatiquement la session courte tant que la session longue est valide.
- **FR-006**: Le système DOIT stocker les mots de passe de manière sécurisée (hashage irréversible).
- **FR-007**: Le système DOIT permettre à un utilisateur connecté de consulter son propre profil (email, rôle).
- **FR-008**: Le système DOIT rediriger tout utilisateur non authentifié vers la page de connexion lorsqu'il accède à l'espace admin.
- **FR-009**: Le système DOIT afficher un message d'erreur générique en cas d'échec de connexion (sans révéler si l'email existe ou non).
- **FR-010**: Le système DOIT permettre la déconnexion explicite d'un utilisateur.
- **FR-011**: Le système DOIT fournir un mécanisme d'initialisation pour créer le premier administrateur.
- **FR-012**: Le système DOIT empêcher la création de comptes avec un email déjà utilisé.
- **FR-013**: Le système DOIT permettre la désactivation de comptes utilisateurs.
- **FR-014**: Le système DOIT empêcher la connexion des comptes désactivés.
- **FR-015**: L'espace admin DOIT disposer d'une interface avec barre latérale de navigation et en-tête affichant l'identité de l'utilisateur connecté.
- **FR-016**: L'espace admin DOIT proposer un sélecteur de thème (mode clair / mode sombre) dont le choix est persisté localement.
- **FR-017**: Le thème par défaut DOIT correspondre à la préférence système du navigateur de l'utilisateur.
- **FR-018**: Le système DOIT verrouiller temporairement un compte après 5 tentatives de connexion échouées consécutives, avec un blocage de 15 minutes.
- **FR-019**: Le système DOIT exiger un mot de passe d'au moins 8 caractères à la création de compte, sans contrainte de composition.

### Key Entities

- **Utilisateur (User)**: Représente une personne ayant accès à la plateforme. Attributs clés : identifiant unique, adresse email (unique), mot de passe hashé, rôle (administrateur ou éditeur), statut actif/inactif, date de création.
- **Session**: Représente la période d'accès authentifié d'un utilisateur. Comprend une session courte (accès immédiat, 30 min) et une session longue (renouvellement, 7 jours).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un utilisateur peut se connecter et accéder à l'espace admin en moins de 5 secondes.
- **SC-002**: 100% des tentatives d'accès non authentifié aux pages admin sont redirigées vers la page de connexion.
- **SC-003**: Un administrateur peut créer un nouveau compte utilisateur en moins de 30 secondes.
- **SC-004**: Les sessions restent actives sans interruption pendant toute la durée de la session longue (7 jours), avec renouvellement transparent de la session courte.
- **SC-005**: Les messages d'erreur d'authentification ne révèlent aucune information sur l'existence des comptes.
- **SC-006**: Le script d'initialisation permet de rendre la plateforme opérationnelle (premier admin créé) en une seule commande.
- **SC-007**: Le basculement entre mode clair et mode sombre est instantané et le choix persiste entre les sessions.

## Clarifications

### Session 2026-03-20

- Q: Protection contre les tentatives de connexion par force brute ? → A: Verrouillage temporaire après 5 échecs consécutifs, blocage 15 minutes.
- Q: Règles de complexité des mots de passe à la création ? → A: Minimum 8 caractères, sans contrainte de composition (recommandation NIST SP 800-63B).

## Assumptions

- Les adresses email servent d'identifiant unique pour les utilisateurs.
- Deux rôles suffisent pour cette phase : administrateur (accès complet) et éditeur (accès restreint aux futures fonctionnalités métier).
- La session courte de 30 minutes et la session longue de 7 jours sont des durées appropriées pour l'usage prévu.
- Le script d'initialisation du premier admin utilise des identifiants configurés via des variables d'environnement.
- Les pages admin métier (géographie, comptes, etc.) ne font PAS partie du périmètre de cette fonctionnalité.
- Le choix de thème (dark/light) est stocké localement dans le navigateur, pas côté serveur.

## Out of Scope

- Pages admin métier (géographie, comptes ITIE, sociétés, etc.)
- Réinitialisation de mot de passe (fonctionnalité "mot de passe oublié")
- Authentification via fournisseurs tiers (SSO, OAuth externe)
- Gestion avancée des permissions (au-delà des rôles admin/éditeur)
- Interface de gestion des utilisateurs (liste, modification, suppression)
- Audit trail / journal des connexions
