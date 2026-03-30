# Tasks: Service de signalement GlobalLeaks

**Input**: Design documents from `/specs/017-globaleaks-service/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Non demandes explicitement. Verification manuelle via la checklist quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Infrastructure Docker)

**Purpose**: Deploiement de l'instance GlobalLeaks et du service Tor via Docker

- [x] T001 Creer le fichier docker-compose.globaleaks.yml a la racine du projet avec les services globaleaks et tor, volumes globaleaks-data et tor-keys, ports 80:8080 et 443:8443, healthcheck sur /api/health
- [ ] T002 Deployer les conteneurs sur le serveur avec `docker compose -f docker-compose.globaleaks.yml up -d` et verifier que GlobalLeaks repond sur https://<IP>:443
- [ ] T003 Completer le wizard d'initialisation GlobalLeaks : langue francais, nom "Alerte Industries Extractives Madagascar", compte administrateur, premier destinataire, licence AGPL

**Checkpoint**: GlobalLeaks accessible sur IP:443, wizard termine, interface admin fonctionnelle

---

## Phase 2: Foundational (Configuration de base GlobalLeaks)

**Purpose**: Configuration essentielle qui doit etre en place avant de configurer les canaux et d'integrer PCQVP

**⚠️ CRITICAL**: Toutes les user stories dependent de cette phase

- [ ] T004 Configurer le domaine `alerte.miningobs.mg` dans Admin > Network > HTTPS et activer Let's Encrypt (apres configuration DNS A record)
- [ ] T005 [P] Recuperer l'adresse .onion avec `docker exec globaleaks-tor cat /var/lib/tor/hidden_service/hostname` et la configurer dans Admin > Network > Tor
- [ ] T006 [P] Activer le francais comme langue par defaut et ajouter le malgache dans Admin > Settings > Languages. Utiliser "Text customization" pour les traductions malgaches des elements d'interface principaux
- [ ] T007 [P] Mettre en place le script de sauvegarde automatique dans /etc/cron.daily/globaleaks-backup : `docker exec globaleaks gl-admin backup` + copie vers /backups/globaleaks/ + purge des sauvegardes > 30 jours

**Checkpoint**: HTTPS actif sur alerte.miningobs.mg, Tor fonctionnel, langues configurees, backup automatise

---

## Phase 3: User Story 1 - Signalement anonyme (Priority: P1) 🎯 MVP

**Goal**: Un lanceur d'alerte peut soumettre un signalement anonyme via un formulaire structure et recevoir un code d'acces pour le suivi

**Independent Test**: Acceder a l'interface GlobalLeaks, soumettre un signalement de test avec pieces jointes, verifier la reception du code d'acces, revenir avec le code et consulter le signalement

### Implementation for User Story 1

- [ ] T008 [US1] Creer le questionnaire "Industries Extractives - Base" dans Admin > Questionnaires avec les champs : type d'irregularite (selection), localisation geographique (texte), entites impliquees (texte multiligne), periode concernee (plage de dates), description detaillee (texte multiligne), pieces jointes (fichier)
- [ ] T009 [US1] Creer le canal "Fiscalite / Paiements" dans Admin > Channels : nom, description, image, questionnaire "Industries Extractives - Base", assigner le destinataire initial
- [ ] T010 [P] [US1] Creer le canal "Environnement" dans Admin > Channels : nom, description, image, questionnaire "Industries Extractives - Base", assigner le destinataire initial
- [ ] T011 [P] [US1] Creer le canal "Social / Communautaire" dans Admin > Channels : nom, description, image, questionnaire "Industries Extractives - Base", assigner le destinataire initial
- [ ] T012 [P] [US1] Creer le canal "Gouvernance / Corruption" dans Admin > Channels : nom, description, image, questionnaire "Industries Extractives - Base", assigner le destinataire initial
- [ ] T013 [US1] Effectuer un signalement de test complet sur chaque canal : verifier le formulaire, attacher un fichier, soumettre, noter le code d'acces, revenir avec le code et verifier l'acces au signalement

**Checkpoint**: Les 4 canaux sont visibles, un signalement de test est soumis et accessible via son code d'acces

---

## Phase 4: User Story 2 - Traitement des signalements par un destinataire (Priority: P2)

**Goal**: Un destinataire peut consulter les signalements, envoyer des messages au lanceur d'alerte et gerer le cycle de vie des rapports

**Independent Test**: Se connecter en tant que destinataire, ouvrir un signalement, envoyer un message, telecharger une piece jointe, changer le statut du signalement

### Implementation for User Story 2

- [ ] T014 [US2] Ajouter les destinataires supplementaires dans Admin > Users : nom, email, mot de passe, assigner aux canaux pertinents, recommander l'activation du 2FA
- [ ] T015 [US2] Configurer les notifications email dans Admin > Notification : serveur SMTP, adresse expediteur, templates de notification en francais
- [ ] T016 [US2] Configurer la politique de retention dans Admin > Data retention : desactiver la suppression automatique (conservation indefinie, suppression manuelle uniquement)
- [ ] T017 [US2] Tester le workflow complet : soumettre un signalement de test, se connecter en tant que destinataire, lire le signalement, envoyer un message, verifier que le lanceur d'alerte voit le message, telecharger les pieces jointes

**Checkpoint**: Les destinataires recoivent les notifications, peuvent traiter les signalements et communiquer avec les lanceurs d'alerte

---

## Phase 5: User Story 3 - Navigation depuis PCQVP (Priority: P2)

**Goal**: Les visiteurs de la plateforme PCQVP trouvent facilement le lien vers le service de signalement

**Independent Test**: Naviguer sur PCQVP, cliquer sur le lien de signalement dans le header ou la page /signaler, verifier la redirection vers GlobalLeaks

### Implementation for User Story 3

- [x] T018 [US3] Configurer l'URL GlobalLeaks dans le backend PCQVP via l'endpoint admin PUT /api/admin/config/globalleaks_url avec la valeur `https://alerte.miningobs.mg` (ou `https://<IP>:443` temporairement)
- [x] T019 [US3] Verifier que la page frontend/app/pages/signaler.vue affiche correctement le bouton "Acceder a GlobalLeaks" avec l'URL configuree
- [x] T020 [US3] Verifier que le lien "Signaler" dans le header du layout frontend/app/layouts/default.vue dirige vers /signaler et que la chaine est fonctionnelle jusqu'a GlobalLeaks

**Checkpoint**: Le parcours PCQVP → /signaler → GlobalLeaks est fonctionnel de bout en bout

---

## Phase 6: User Story 4 - Administration et personnalisation (Priority: P3)

**Goal**: L'administrateur peut personnaliser GlobalLeaks (branding, questionnaires, langues) pour le contexte PCQVP

**Independent Test**: Se connecter en tant qu'admin, modifier le logo et les couleurs, verifier les changements sur la page publique

### Implementation for User Story 4

- [ ] T021 [US4] Personnaliser l'apparence dans Admin > Settings : logo PCQVP/MiningObs, nom du projet, description, couleurs coherentes avec la charte graphique
- [ ] T022 [P] [US4] Completer les traductions malgaches des elements d'interface via Admin > Settings > Text customization : page d'accueil, formulaire de signalement, messages de confirmation, labels des canaux
- [ ] T023 [P] [US4] Personnaliser les templates de notification email dans Admin > Notification pour les 4 canaux en francais et malgache
- [ ] T024 [US4] Documenter la procedure d'administration dans un guide operateur : ajout de destinataires, modification des questionnaires, consultation des logs, procedure de backup/restore

**Checkpoint**: GlobalLeaks est personnalise visuellement, les traductions malgaches sont en place, la documentation operateur est prete

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verification finale et documentation

- [ ] T025 [P] Tester l'acces via Tor Browser avec l'adresse .onion et verifier le fonctionnement complet (soumission + suivi)
- [ ] T026 [P] Executer une sauvegarde manuelle et verifier la restauration sur un environnement de test
- [ ] T027 Executer la checklist de verification du fichier specs/017-globaleaks-service/quickstart.md section 7
- [ ] T028 Verifier la securite : acces admin protege par 2FA, certificats HTTPS valides, pas de ports exposes inutilement

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - deploiement Docker initial
- **Foundational (Phase 2)**: Depends on Setup - HTTPS, Tor, langues, backup
- **User Story 1 (Phase 3)**: Depends on Phase 2 - canaux et questionnaires
- **User Story 2 (Phase 4)**: Depends on Phase 3 (besoin de signalements de test pour valider le traitement)
- **User Story 3 (Phase 5)**: Depends on Phase 2 seulement (peut etre fait en parallele de Phase 3/4)
- **User Story 4 (Phase 6)**: Depends on Phase 2 seulement (peut etre fait en parallele de Phase 3/4)
- **Polish (Phase 7)**: Depends on all user stories

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Phase 2 - Aucune dependance sur d'autres stories
- **User Story 2 (P2)**: Depends on US1 (besoin de signalements existants pour tester le traitement)
- **User Story 3 (P2)**: Depends on Phase 2 seulement - Independant des autres stories
- **User Story 4 (P3)**: Depends on Phase 2 seulement - Independant des autres stories

### Parallel Opportunities

- T005, T006, T007 peuvent etre executes en parallele (Phase 2)
- T010, T011, T012 peuvent etre executes en parallele (creation des canaux 2-4)
- US3 et US4 peuvent etre executes en parallele de US1/US2
- T022, T023 peuvent etre executes en parallele (traductions)
- T025, T026 peuvent etre executes en parallele (verification finale)

---

## Parallel Example: Phase 3 (User Story 1)

```bash
# Apres creation du questionnaire (T008) et du premier canal (T009) :
# Lancer la creation des 3 autres canaux en parallele :
Task: "Creer le canal Environnement dans Admin > Channels"
Task: "Creer le canal Social / Communautaire dans Admin > Channels"
Task: "Creer le canal Gouvernance / Corruption dans Admin > Channels"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Deploiement Docker
2. Complete Phase 2: Configuration de base (HTTPS, Tor, langues, backup)
3. Complete Phase 3: Canaux et questionnaires
4. **STOP and VALIDATE**: Soumettre un signalement de test, verifier le code d'acces
5. L'instance est deja utilisable pour recevoir des signalements

### Incremental Delivery

1. Setup + Foundational → GlobalLeaks en ligne avec HTTPS + Tor
2. User Story 1 → Canaux configures → **MVP utilisable**
3. User Story 2 → Destinataires configures, workflow complet
4. User Story 3 → Integration PCQVP fonctionnelle
5. User Story 4 → Personnalisation et documentation
6. Polish → Verification securite et backup

### Note importante

Ce projet est principalement un travail de **configuration** (pas de developpement logiciel). La majorite des taches s'effectuent via l'interface web d'administration de GlobalLeaks. Les seuls fichiers de code concernes sont :
- `docker-compose.globaleaks.yml` (nouveau)
- Configuration URL dans le backend PCQVP (endpoint existant)

---

## Notes

- [P] tasks = different files/actions, no dependencies
- [Story] label maps task to specific user story for traceability
- La plupart des taches sont des configurations via l'interface web GlobalLeaks Admin
- Commit le docker-compose.globaleaks.yml apres creation
- Documenter les identifiants admin dans un gestionnaire de mots de passe securise
- L'adresse .onion doit etre communiquee aux partenaires de confiance
