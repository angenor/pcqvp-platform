# Feature Specification: Correctifs UX back-office (lot 018)

**Feature Branch**: `018-backoffice-ux-fixes`
**Created**: 2026-04-17
**Status**: Draft
**Input**: User description: "Après avoir parcouru le back-office et effectué des simulations, voici les fix à faire : GEOGRAPHIE > Dans la partie Description de chaque collectivité (Provinces, Régions et Communes), ajouter une option Insertion de fichiers après image bannière (documents officiels tels que Plan communal de développement, Stratégie d'Aménagement Territorial). GEOGRAPHIE > COMMUNES : Pour chaque Commune, ajouter Voir les comptes et Soumettre un compte pour faciliter l'insertion des comptes. COMPTES > COMPTES ADMINISTRATIFS : Dans ACTIONS, ajouter Supprimer. OUTILS > EDITORIAUX > CORPS DE PAGE : On n'arrive pas à insérer d'image dans l'editeur de texte."

## Clarifications

### Session 2026-04-17

- Q: Politique de suppression d'un compte administratif référencé ailleurs (statistiques, exports) → A: Bloquer avec message explicite listant les références à résoudre avant suppression
- Q: Gestion des versions d'un document officiel lors d'un remplacement → A: Le remplacement écrase le fichier en place (même entrée, nouveau contenu), sans historique conservé
- Q: Visibilité publique des documents officiels attachés → A: Publication immédiate — dès qu'un document est attaché, il est visible publiquement si la collectivité est publiée (pas d'état brouillon par document ni workflow de validation individuel)
- Q: Journal d'audit des opérations sur les documents officiels (ajout, remplacement, suppression) → A: Aucun audit spécifique — hors scope du correctif 018 (l'audit reste limité à la suppression de comptes administratifs par FR-007)
- Q: Métadonnées affichées à côté de chaque document officiel sur la page publique → A: Titre + icône de type + taille du fichier + date de dernière mise à jour (auto-dérivées, aucune saisie supplémentaire pour l'administrateur)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rétablir l'insertion d'images dans l'éditeur éditorial (Priority: P1)

Un éditeur ouvre une page éditoriale dans **OUTILS > ÉDITORIAUX > CORPS DE PAGE** et souhaite illustrer son texte avec une image (photo, infographie, visuel d'illustration). Il déclenche l'insertion d'image dans l'éditeur de texte riche, sélectionne un fichier depuis son poste, et l'image apparaît correctement dans le corps de la page, est enregistrée avec le contenu, puis s'affiche en rendu public.

**Why this priority**: Blocage complet d'un flux de production de contenu. Sans image, les pages éditoriales publiées perdent en attractivité et lisibilité. C'est un bug régressif qui doit être corrigé en priorité avant tout enrichissement fonctionnel.

**Independent Test**: Se connecter en tant qu'éditeur, créer une nouvelle page éditoriale, tenter d'insérer une image dans le corps de page, sauvegarder, puis consulter l'aperçu public. L'image doit être visible et accessible.

**Acceptance Scenarios**:

1. **Given** un éditeur connecté sur l'écran d'édition du corps de page éditoriale, **When** il déclenche l'insertion d'image et choisit un fichier local valide (PNG/JPG/WebP ≤ 5 Mo), **Then** l'image est téléversée, intégrée au bloc image de l'éditeur avec aperçu immédiat, et persistée avec le contenu de la page.
2. **Given** une page éditoriale sauvegardée contenant une image insérée, **When** un visiteur public consulte la page, **Then** l'image s'affiche au bon endroit dans le corps de page, avec texte alternatif et cadre responsive.
3. **Given** un fichier non supporté (format interdit, taille excédée), **When** l'éditeur tente de le téléverser, **Then** un message d'erreur clair s'affiche et le contenu existant n'est pas altéré.

---

### User Story 2 - Supprimer un compte administratif depuis la liste (Priority: P2)

Un administrateur consulte la liste des comptes administratifs dans **COMPTES > COMPTES ADMINISTRATIFS**. Pour un compte saisi par erreur, obsolète ou en doublon, il utilise une action « Supprimer » dans la colonne ACTIONS, confirme son intention, et le compte disparaît définitivement de la liste.

**Why this priority**: Sans cette action, les administrateurs ne peuvent corriger les saisies erronées ni nettoyer les données, ce qui pollue les tableaux publics. La fonctionnalité est attendue par symétrie avec les autres entités déjà suppressibles.

**Independent Test**: Se connecter en tant qu'administrateur, accéder à la liste des comptes administratifs, déclencher la suppression d'un compte cible, confirmer, puis vérifier que le compte ne figure plus dans la liste ni dans l'affichage public de la commune concernée.

**Acceptance Scenarios**:

1. **Given** un administrateur sur la liste des comptes administratifs, **When** il clique sur « Supprimer » sur une ligne puis confirme dans la boîte de dialogue, **Then** le compte est retiré de la liste et n'apparaît plus côté public.
2. **Given** la même action, **When** l'administrateur annule la confirmation, **Then** le compte reste intact et la liste n'est pas modifiée.
3. **Given** un utilisateur sans privilège administrateur (rôle éditeur par exemple), **When** il accède à la liste, **Then** l'action « Supprimer » n'est pas disponible et toute tentative directe est refusée.

---

### User Story 3 - Attacher des documents officiels à la description d'une collectivité (Priority: P2)

Un administrateur édite la description d'une Province, d'une Région ou d'une Commune. Juste après l'image bannière, il accède à une nouvelle section « Documents officiels » où il peut téléverser un ou plusieurs fichiers (Plan communal de développement, Stratégie d'Aménagement Territorial, etc.) avec un titre explicite. Après publication, ces documents apparaissent sur la page publique de la collectivité sous forme de liens téléchargeables.

**Why this priority**: Enrichit la présentation publique des collectivités avec des ressources officielles, pilier de la mission de transparence de la plateforme. Non bloquant mais à forte valeur ajoutée pour les citoyens et journalistes.

**Independent Test**: Éditer une commune, attacher deux documents PDF nommés, sauvegarder, consulter la page publique de la commune et télécharger chacun des documents.

**Acceptance Scenarios**:

1. **Given** l'écran d'édition d'une Province, Région ou Commune, **When** l'administrateur ajoute un fichier (PDF, DOC/DOCX, XLS/XLSX) avec un titre dans la section « Documents officiels », **Then** le fichier est téléversé, associé à la collectivité et listé dans l'ordre d'ajout.
2. **Given** une collectivité publiée ayant des documents officiels, **When** un visiteur consulte la page publique, **Then** il voit la liste des documents (titre + indication visuelle du type de fichier) et peut les télécharger en un clic.
3. **Given** un document déjà attaché, **When** l'administrateur le retire ou le remplace, **Then** la modification est persistée et reflétée immédiatement côté public après sauvegarde.
4. **Given** un fichier ne respectant pas les contraintes (format non autorisé, taille excessive), **When** l'administrateur tente le téléversement, **Then** un message d'erreur explicite s'affiche sans casser la saisie en cours.

---

### User Story 4 - Accès rapide aux comptes depuis une commune (Priority: P3)

Un utilisateur autorisé consulte la liste des communes dans **GÉOGRAPHIE > COMMUNES**. Pour chaque commune, deux raccourcis sont visibles : « Voir les comptes » (ouvre la liste des comptes administratifs déjà saisis pour cette commune) et « Soumettre un compte » (ouvre le formulaire de création pré-rempli avec la commune sélectionnée). Ces raccourcis évitent la navigation manuelle par filtres.

**Why this priority**: Amélioration UX significative pour les utilisateurs qui saisissent fréquemment des comptes par commune, mais pas un bloqueur. Complète une fonctionnalité existante.

**Independent Test**: Depuis la liste des communes, cliquer sur « Voir les comptes » d'une commune cible et vérifier que la liste filtrée s'ouvre ; revenir, cliquer sur « Soumettre un compte » et vérifier que le formulaire s'ouvre avec la commune pré-sélectionnée.

**Acceptance Scenarios**:

1. **Given** un utilisateur autorisé sur la liste des communes, **When** il clique sur « Voir les comptes » pour une commune donnée, **Then** il arrive sur la liste des comptes administratifs filtrée sur cette commune.
2. **Given** le même contexte, **When** il clique sur « Soumettre un compte », **Then** il arrive sur le formulaire de création de compte avec la commune déjà renseignée.
3. **Given** une commune sans aucun compte saisi, **When** l'utilisateur clique sur « Voir les comptes », **Then** il voit la liste filtrée vide avec un message d'invitation à créer le premier compte.

---

### Edge Cases

- **Éditeur / image** : perte de connexion pendant le téléversement de l'image — le contenu déjà saisi ne doit pas être perdu, un message d'échec clair doit s'afficher.
- **Éditeur / image** : fichier malveillant ou extension falsifiée — le système doit refuser l'insertion et journaliser la tentative.
- **Suppression de compte** : compte référencé par un autre contenu (statistique, export archivé) — la suppression est bloquée et un message liste les références à résoudre au préalable (cf. FR-006a).
- **Documents officiels** : nombre élevé de pièces jointes (> 20 par collectivité) — la liste doit rester lisible (pagination, scroll, regroupement).
- **Documents officiels** : même fichier ajouté en double — prévenir l'utilisateur ou autoriser avec avertissement.
- **Raccourcis commune** : commune désactivée ou en brouillon — les actions doivent rester cohérentes (soit masquées, soit explicitement désactivées).
- **Permissions** : les quatre fonctionnalités doivent respecter les rôles `admin` / `editor` existants sans contourner les règles d'accès.

## Requirements *(mandatory)*

### Functional Requirements

**Correctif éditeur éditorial (P1)**

- **FR-001**: Le système DOIT permettre à un utilisateur autorisé d'insérer une image dans le corps de page d'une éditoriale via l'éditeur riche existant, avec téléversement d'un fichier local.
- **FR-002**: Le système DOIT persister les images insérées avec le contenu de la page et les rendre visibles à l'identique dans l'aperçu et la page publique.
- **FR-003**: Le système DOIT valider les images téléversées (formats autorisés PNG/JPG/WebP, taille ≤ 5 Mo) et retourner un message d'erreur compréhensible si la validation échoue, sans altérer le contenu existant.

**Suppression de comptes administratifs (P2)**

- **FR-004**: Le système DOIT afficher une action « Supprimer » dans la colonne ACTIONS de chaque ligne de la liste des comptes administratifs, accessible aux seuls utilisateurs disposant du privilège requis.
- **FR-005**: Le système DOIT demander une confirmation explicite avant d'exécuter la suppression d'un compte administratif.
- **FR-006**: Le système DOIT retirer définitivement le compte supprimé des affichages back-office et public après confirmation.
- **FR-006a**: Le système DOIT bloquer la suppression d'un compte administratif référencé par d'autres contenus (statistiques, exports archivés, indicateurs) et afficher un message listant précisément les références à résoudre avant de pouvoir relancer la suppression. La suppression n'est exécutée que lorsque le compte n'est plus référencé.
- **FR-007**: Le système DOIT journaliser chaque suppression de compte administratif (acteur, cible, horodatage) à des fins d'audit.

**Documents officiels de collectivités (P2)**

- **FR-008**: Le système DOIT proposer, dans l'écran d'édition de chaque Province, Région et Commune, une section « Documents officiels » positionnée immédiatement après l'image bannière, avant le reste de la description riche.
- **FR-009**: Les utilisateurs autorisés DOIVENT pouvoir ajouter, réordonner, remplacer et supprimer des documents attachés (fichier + titre obligatoire), avant ou après publication de la collectivité.
- **FR-009a**: Le remplacement d'un document officiel DOIT écraser le fichier de l'entrée existante (même titre et même position conservés par défaut, nouveau contenu effectivement téléversé), sans conservation de l'historique des versions précédentes. L'horodatage de dernière mise à jour de l'entrée DOIT être actualisé.
- **FR-010**: Le système DOIT valider chaque document téléversé (formats PDF, DOC, DOCX, XLS, XLSX ; taille ≤ 20 Mo) et refuser les fichiers non conformes avec un message d'erreur clair.
- **FR-011**: La page publique d'une collectivité publiée DOIT afficher la liste des documents officiels attachés sous forme de liens téléchargeables, avec les métadonnées suivantes pour chaque entrée : titre, icône/indication visuelle du type de fichier, taille du fichier et date de dernière mise à jour. Ces métadonnées sont auto-dérivées (pas de saisie supplémentaire pour l'administrateur).
- **FR-011a**: Les documents officiels ne possèdent PAS d'état de publication individuel. Dès qu'un document est attaché en back-office, il est immédiatement visible publiquement si la collectivité parente est publiée ; si la collectivité est en brouillon ou dépubliée, aucun document n'est accessible au public.
- **FR-012**: Le système DOIT préserver l'ordre d'affichage choisi par l'administrateur et refléter immédiatement toute modification après sauvegarde.

**Raccourcis comptes sur communes (P3)**

- **FR-013**: La liste des communes DOIT exposer, pour chaque ligne, une action « Voir les comptes » qui redirige vers la liste des comptes administratifs filtrée sur la commune sélectionnée.
- **FR-014**: La liste des communes DOIT exposer, pour chaque ligne, une action « Soumettre un compte » qui ouvre le formulaire de création de compte administratif avec la commune pré-renseignée.
- **FR-015**: Les deux raccourcis DOIVENT respecter les règles de permissions existantes (visibilité et action conditionnées par le rôle de l'utilisateur).

### Key Entities

- **Collectivité (Province / Région / Commune)** : entité géographique publiable, dotée d'une description riche (bannière + contenu), à laquelle est désormais associée une collection ordonnée de **documents officiels** (titre, fichier, type, ordre d'affichage, horodatage).
- **Document officiel** : pièce jointe attachée à une collectivité, décrite par un titre (saisi), un fichier téléversé, un type déduit, une taille auto-dérivée, une date de dernière mise à jour auto-dérivée et un ordre de tri.
- **Compte administratif** : entité financière rattachée à une commune, désormais dotée d'une opération de suppression soumise à confirmation et journalisation.
- **Page éditoriale** : contenu riche éditable dont le corps de page accepte à nouveau l'insertion d'images via le bloc image de l'éditeur riche.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 % des tentatives d'insertion d'image dans le corps d'une page éditoriale réussissent pour les formats supportés et s'affichent correctement côté public après la correction.
- **SC-002**: Un administrateur peut supprimer un compte administratif erroné en moins de 15 secondes (de la liste jusqu'à la confirmation), et 100 % des suppressions sont tracées dans le journal d'audit.
- **SC-003**: Dans le mois suivant la mise en production, au moins 80 % des collectivités publiées sollicitées par les équipes éditoriales peuvent présenter au moins un document officiel attaché, téléchargeable sans erreur.
- **SC-004**: L'accès à la liste des comptes d'une commune ou au formulaire de création pré-renseigné se fait en un seul clic depuis la liste des communes (contre au moins trois actions avant la correction).
- **SC-005**: Les tickets support ou retours utilisateurs liés à « impossible d'insérer une image dans l'éditeur » tombent à zéro sur les 30 jours suivant la mise en production.
- **SC-006**: 100 % des téléversements (image éditoriale ou document officiel) qui violent les règles de validation (format, taille) sont bloqués avec un message d'erreur explicite, sans perte du contenu en cours de saisie.

## Assumptions

- La chaîne de téléversement de fichiers existante (endpoint de dépôt et service de validation) est réutilisée pour l'image éditoriale et les documents officiels, avec extension éventuelle des types autorisés.
- La suppression d'un compte administratif est **permanente** (pas de corbeille), conforme au pattern déjà appliqué aux autres entités supprimables, mais toujours tracée dans le journal d'audit.
- Les formats acceptés pour les documents officiels sont PDF, DOC, DOCX, XLS, XLSX avec une taille maximale de 20 Mo par fichier, en ligne avec les usages administratifs malgaches (documents ministériels et communaux).
- Les formats acceptés pour les images de l'éditeur restent PNG, JPG, WebP avec une taille maximale de 5 Mo, alignés avec le reste de la plateforme.
- Les rôles existants `admin` et `editor` couvrent les cas d'usage : la suppression d'un compte administratif est réservée à l'administrateur, les autres opérations suivent les permissions déjà en place pour les écrans concernés.
- La fonctionnalité « image bannière » actuelle des collectivités reste inchangée ; la section « Documents officiels » s'insère en complément immédiatement après, sans refonte de l'éditeur riche existant.
- Les raccourcis « Voir les comptes » et « Soumettre un compte » s'intègrent dans la colonne d'actions existante de la liste des communes, sans modification structurelle de la page.
- Le support obligatoire du mode sombre / clair sur la plateforme s'applique à toutes les nouvelles interfaces (actions, sections, listes de documents) sans exception.
