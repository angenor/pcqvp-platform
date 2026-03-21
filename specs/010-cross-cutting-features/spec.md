# Feature Specification: Fonctionnalites transverses

**Feature Branch**: `010-cross-cutting-features`
**Created**: 2026-03-21
**Status**: Draft
**Input**: User description: "Feature 9 : Fonctionnalites transverses - Newsletter, Recherche full-text, Suivi visites/telechargements, Preparation integration GlobalLeaks"

## Clarifications

### Session 2026-03-21

- Q: Mode d'affichage des resultats de recherche (dropdown autocomplete vs page dediee vs les deux) → A: Dropdown autocomplete dans le header (max 8-10 resultats, avec lien "voir tous les resultats").
- Q: Politique de retention des donnees de suivi (visit_logs) → A: 12 mois de retention. Pas de purge automatique : le systeme notifie l'admin quand des donnees depassent 12 mois, et l'admin declenche la purge manuellement.
- Q: Comportement lors de la reinscription newsletter apres desinscription → A: Reactiver l'abonnement existant (meme enregistrement, statut repasse a "actif", nouveau double opt-in requis).
- Q: Protection anti-abus sur les endpoints publics (recherche, inscription) → A: Rate limiting par IP sur les endpoints publics (recherche + inscription newsletter).
- Q: Champs recherches dans les comptes administratifs → A: Recherche par nom de commune associee + annee d'exercice (ex: "Antsirabe 2024").

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recherche full-text sur les collectivites et comptes (Priority: P1)

Un visiteur souhaite retrouver rapidement une collectivite ou un compte administratif. Il saisit un terme dans un champ de recherche dans le header, accessible depuis toutes les pages. Un dropdown autocomplete affiche jusqu'a 8-10 resultats regroupes par type (collectivites, comptes), avec un lien "voir tous les resultats" pour une recherche approfondie.

**Why this priority**: La recherche est le moyen le plus rapide pour un citoyen de trouver l'information qu'il cherche. C'est la fonctionnalite transverse qui apporte le plus de valeur immediate a tous les utilisateurs.

**Independent Test**: Peut etre teste en saisissant un terme de recherche et en verifiant que les resultats pertinents apparaissent avec les collectivites et comptes correspondants.

**Acceptance Scenarios**:

1. **Given** un visiteur sur n'importe quelle page, **When** il saisit "Antananarivo" dans le champ de recherche, **Then** les collectivites contenant "Antananarivo" apparaissent dans les resultats, tries par pertinence.
2. **Given** un visiteur qui effectue une recherche, **When** il saisit un terme correspondant a un compte administratif (ex: nom de commune avec un compte publie), **Then** les comptes correspondants apparaissent dans les resultats avec un lien vers la page de consultation.
3. **Given** un visiteur qui effectue une recherche, **When** il saisit un terme sans correspondance, **Then** un message "Aucun resultat" s'affiche avec des suggestions (ex: verifier l'orthographe).
4. **Given** un visiteur qui effectue une recherche, **When** il saisit un terme partiel ou avec des accents manquants, **Then** le systeme trouve quand meme les resultats pertinents grace a la recherche full-text.

---

### User Story 2 - Inscription a la newsletter (Priority: P2)

Un visiteur souhaite etre informe des nouveaux comptes publies ou des actualites de la plateforme. Il saisit son adresse email dans un formulaire d'inscription a la newsletter, accessible depuis le pied de page ou une page dediee. Il recoit un email de confirmation.

**Why this priority**: La newsletter permet de fideliser les visiteurs et de les alerter sur les nouvelles publications, renforcant la transparence et l'engagement citoyen.

**Independent Test**: Peut etre teste en soumettant une adresse email dans le formulaire et en verifiant que l'inscription est enregistree et qu'un email de confirmation est envoye.

**Acceptance Scenarios**:

1. **Given** un visiteur sur le site, **When** il saisit une adresse email valide dans le formulaire newsletter et soumet, **Then** l'inscription est enregistree et un message de confirmation s'affiche.
2. **Given** un visiteur qui soumet le formulaire, **When** l'adresse email est deja inscrite, **Then** un message indique que l'adresse est deja enregistree (sans reveler d'information sensible).
3. **Given** un visiteur qui soumet le formulaire, **When** l'adresse email est invalide, **Then** un message d'erreur de validation s'affiche.
4. **Given** un visiteur inscrit, **When** il clique sur le lien de desinscription dans un email, **Then** son adresse est retiree de la liste des abonnes.

---

### User Story 3 - Gestion des abonnes newsletter en admin (Priority: P3)

Un administrateur souhaite consulter et gerer la liste des abonnes a la newsletter. Il peut voir le nombre total d'abonnes, exporter la liste, et supprimer des abonnes si necessaire.

**Why this priority**: La gestion admin est necessaire pour exploiter la liste d'abonnes et maintenir la base de donnees propre.

**Independent Test**: Peut etre teste en accedant a la page admin des abonnes, en verifiant que la liste s'affiche et que les actions d'export et de suppression fonctionnent.

**Acceptance Scenarios**:

1. **Given** un administrateur connecte, **When** il accede a la page de gestion des abonnes, **Then** la liste des abonnes s'affiche avec email, date d'inscription et statut.
2. **Given** un administrateur sur la page des abonnes, **When** il exporte la liste, **Then** un fichier contenant tous les abonnes actifs est telecharge.
3. **Given** un administrateur sur la page des abonnes, **When** il supprime un abonne, **Then** l'abonne est retire de la liste apres confirmation.

---

### User Story 4 - Suivi des visites et telechargements (Priority: P3)

Un administrateur souhaite comprendre l'utilisation de la plateforme : quelles pages sont les plus consultees, quels fichiers (exports Excel/Word) sont les plus telecharges. Un tableau de bord en admin affiche ces statistiques.

**Why this priority**: Le suivi d'utilisation permet de mesurer l'impact de la plateforme et d'orienter les priorites de contenu.

**Independent Test**: Peut etre teste en naviguant sur le site, en effectuant des telechargements, puis en verifiant que le tableau de bord admin reflete ces activites.

**Acceptance Scenarios**:

1. **Given** un visiteur qui navigue sur le site, **When** il consulte une page de collectivite ou de compte, **Then** la visite est enregistree silencieusement (sans impact sur la performance).
2. **Given** un visiteur qui telecharge un export, **When** le telechargement est initie, **Then** l'evenement est enregistre avec le type de fichier et la collectivite concernee.
3. **Given** un administrateur connecte, **When** il accede au tableau de bord de suivi, **Then** il voit les statistiques de visites par page, les telechargements par type, et les tendances sur une periode configurable.
4. **Given** un administrateur sur le tableau de bord, **When** il selectionne une periode (7 jours, 30 jours, 12 mois), **Then** les statistiques s'actualisent pour la periode choisie.

---

### User Story 5 - Integration GlobalLeaks (Priority: P4)

Un visiteur souhaite signaler un probleme de maniere anonyme et securisee. Un lien ou une section dediee sur le site le redirige vers l'instance GlobalLeaks existante, avec une explication claire du processus.

**Why this priority**: L'integration GlobalLeaks est une preparation (lien/redirection), pas un developpement lourd. Elle complete l'ecosysteme de transparence.

**Independent Test**: Peut etre teste en cliquant sur le lien/bouton GlobalLeaks et en verifiant qu'il redirige vers l'instance externe avec les informations contextuelles appropriees.

**Acceptance Scenarios**:

1. **Given** un visiteur sur le site, **When** il clique sur le lien "Signaler" dans la navigation ou le pied de page, **Then** il est redirige vers une page dediee expliquant le processus de signalement.
2. **Given** un visiteur sur la page de signalement, **When** il clique sur le bouton d'acces a GlobalLeaks, **Then** il est redirige vers l'instance GlobalLeaks externe dans un nouvel onglet.
3. **Given** un administrateur, **When** il configure l'URL de l'instance GlobalLeaks dans les parametres, **Then** le lien sur le site public pointe vers cette URL.

---

### Edge Cases

- Que se passe-t-il quand la recherche contient des caracteres speciaux ou des tentatives d'injection ?
- Comment le systeme reagit-il si l'instance GlobalLeaks est indisponible ?
- Que se passe-t-il si un meme visiteur s'inscrit plusieurs fois a la newsletter avec la meme adresse ?
- Comment sont gerees les visites des bots/crawlers dans le suivi (ne pas fausser les statistiques) ?
- Que se passe-t-il si la base d'abonnes depasse un volume important (pagination, export partiel) ?
- Comment le systeme gere-t-il la recherche sur des donnees en malgache avec des caracteres specifiques ?

## Requirements *(mandatory)*

### Functional Requirements

**Recherche full-text**

- **FR-001**: Le systeme DOIT offrir un champ de recherche global accessible depuis toutes les pages du site public.
- **FR-002**: Le systeme DOIT effectuer une recherche full-text sur les noms des collectivites (provinces, regions, communes) et sur les comptes administratifs publies (nom de commune associee + annee d'exercice).
- **FR-003**: Le systeme DOIT trier les resultats par pertinence et les regrouper par type (collectivites, comptes).
- **FR-004**: Le systeme DOIT supporter la recherche insensible aux accents et a la casse.
- **FR-005**: Le systeme DOIT afficher les resultats sous forme de dropdown autocomplete dans le header (max 8-10 resultats, regroupes par type), avec recherche en temps reel (debounce) et un lien "voir tous les resultats" menant a une page de resultats complets paginee (/recherche?q=...).

**Newsletter**

- **FR-006**: Le systeme DOIT permettre l'inscription a la newsletter via un formulaire email.
- **FR-007**: Le systeme DOIT valider le format de l'adresse email avant enregistrement.
- **FR-008**: Le systeme DOIT envoyer un email de confirmation lors de l'inscription (double opt-in).
- **FR-009**: Le systeme DOIT permettre la desinscription via un lien unique dans chaque email.
- **FR-010**: Le systeme DOIT empecher les inscriptions en double pour une meme adresse email. Si l'adresse existe deja avec le statut "desinscrit", le systeme DOIT reactiver l'abonnement existant (statut repasse a "actif") et declencher un nouveau double opt-in.
- **FR-011**: Le systeme DOIT fournir une interface admin pour consulter, rechercher et exporter la liste des abonnes.
- **FR-012**: Le systeme DOIT permettre a un administrateur de supprimer manuellement un abonne.

**Suivi des visites et telechargements**

- **FR-013**: Le systeme DOIT enregistrer les visites sur les pages publiques (page visitee, horodatage, type de page).
- **FR-014**: Le systeme DOIT enregistrer les evenements de telechargement (type de fichier, collectivite, horodatage).
- **FR-015**: Le systeme DOIT fournir un tableau de bord admin affichant les statistiques de visites et telechargements.
- **FR-016**: Le systeme DOIT permettre le filtrage des statistiques par periode (7 jours, 30 jours, 12 mois).
- **FR-017**: Le systeme DOIT exclure les bots connus des statistiques de visites (filtrage par User-Agent).
- **FR-018**: Le systeme DOIT notifier l'administrateur lorsque des donnees de suivi depassent 12 mois d'anciennete, via une banniere d'alerte visible dans le tableau de bord analytics.
- **FR-019**: Le systeme DOIT permettre a l'administrateur de declencher manuellement la purge des donnees de suivi de plus de 12 mois.

**Integration GlobalLeaks**

- **FR-020**: Le systeme DOIT afficher un lien vers GlobalLeaks dans la navigation et/ou le pied de page.
- **FR-021**: Le systeme DOIT fournir une page dediee expliquant le processus de signalement anonyme.
- **FR-022**: Le systeme DOIT permettre a un administrateur de configurer l'URL de l'instance GlobalLeaks.

**Securite**

- **FR-023**: Le systeme DOIT appliquer un rate limiting par IP sur les endpoints publics de recherche et d'inscription newsletter afin de prevenir les abus.

### Key Entities

- **NewsletterSubscriber**: Represente un abonne a la newsletter. Attributs principaux : email, date d'inscription, statut (actif/desinscrit/en attente de confirmation), token de desinscription. Cycle de vie : inscription → en attente → actif (apres opt-in) → desinscrit → reactif possible (nouveau opt-in).
- **VisitLog**: Represente un evenement de visite ou telechargement. Attributs principaux : type d'evenement (visite/telechargement), page ou ressource concernee, collectivite associee, horodatage, User-Agent. Retention : 12 mois, purge manuelle par l'admin apres notification.
- **SiteConfiguration**: Represente les parametres configurables du site (ex: URL GlobalLeaks). Attributs principaux : cle, valeur, date de modification.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Les utilisateurs trouvent une collectivite ou un compte en moins de 10 secondes via la recherche.
- **SC-002**: 95% des recherches retournent des resultats pertinents en moins d'1 seconde.
- **SC-003**: Le processus d'inscription a la newsletter se complete en moins de 30 secondes (hors confirmation email).
- **SC-004**: Le tableau de bord admin affiche les statistiques de la periode selectionnee en moins de 3 secondes.
- **SC-005**: 100% des telechargements d'exports sont traces dans les statistiques.
- **SC-006**: Le lien GlobalLeaks est accessible en 2 clics maximum depuis n'importe quelle page.
- **SC-007**: L'administrateur peut exporter la liste complete des abonnes en un clic.

## Assumptions

- L'envoi d'emails (newsletter confirmation, desinscription) sera gere par un service SMTP configure cote backend. Le choix du fournisseur SMTP est hors perimetre de cette spec.
- L'instance GlobalLeaks existe deja et est hebergee separement. Cette feature ne couvre que le lien/la redirection, pas l'hebergement ou la configuration de GlobalLeaks.
- Le suivi des visites est interne (pas d'outil analytics tiers). Les donnees sont stockees dans la base de donnees de la plateforme.
- La recherche full-text utilise les capacites natives de la base de donnees (pas de moteur de recherche externe).
- Le filtrage des bots se base sur une liste de User-Agents connus (approche simple et suffisante pour le volume attendu).
- La newsletter ne couvre pas l'envoi de campagnes email — uniquement l'inscription/desinscription et la gestion des abonnes. L'envoi de campagnes pourra etre ajoute dans une future feature.

## Scope Boundaries

**Inclus** :
- Formulaire d'inscription newsletter et gestion admin des abonnes
- Recherche full-text sur collectivites et comptes
- Suivi des visites de pages et des telechargements avec dashboard admin
- Page et lien de redirection vers GlobalLeaks
- Configuration admin de l'URL GlobalLeaks

**Exclus** :
- Envoi de campagnes/newsletters (hors perimetre, future feature)
- Hebergement ou configuration de l'instance GlobalLeaks
- Analytics avances (entonnoirs, parcours utilisateur, heatmaps)
- Recherche sur le contenu riche (descriptions JSONB) — limite aux noms et metadonnees
- Segmentation des abonnes newsletter
