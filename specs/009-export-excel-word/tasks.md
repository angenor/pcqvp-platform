# Tasks: Export des comptes administratifs en Excel et Word

**Input**: Design documents from `/specs/009-export-excel-word/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Helpers partages necessaires a tous les exports (Excel et Word)

- [x] T001 Ajouter une fonction `sanitize_filename(name: str) -> str` dans `apps/backend/app/services/export_service.py` qui remplace les caracteres speciaux (accents, apostrophes, espaces) par des equivalents ASCII-safe pour les noms de fichiers. Exemple : "Commune d'Andrafiabé" → "Commune_dAndrafiabe"
- [x] T002 Mettre a jour le endpoint export dans `apps/backend/app/routers/public_comptes.py` pour utiliser le format `Compte_Administratif_{NomCollectivite}_{Annee}.{ext}` dans le header Content-Disposition, en utilisant `sanitize_filename()` pour nettoyer le nom. Le nom de la collectivite est deja recupere via `get_collectivite_name()`

**Checkpoint**: Le nommage de fichier est conforme a FR-015 pour les deux formats

---

## Phase 2: User Story 1 - Telecharger le compte administratif au format Excel (Priority: P1)

**Goal**: Le fichier Excel reproduit fidelement la structure et la mise en forme du template officiel malgache avec toutes les colonnes et feuilles requises

**Independent Test**: Telecharger le fichier Excel d'un compte et comparer avec le template de reference (structure des feuilles, colonnes, mise en forme)

### Implementation for User Story 1

- [x] T003 [US1] Mettre a jour la feuille Recettes dans `apps/backend/app/services/export_service.py` : passer de 8 a 10 colonnes en ajoutant "Modifications +/-" (valeur `values.modifications`) apres "Budget Additionnel" et "Taux d'Execution" (valeur `computed.taux_execution` formatee en pourcentage) en derniere colonne. Ajouter des lignes d'en-tete de section "RECETTES DE FONCTIONNEMENT" et "RECETTES D'INVESTISSEMENT" basees sur le champ `section` des lignes. L'ordre des colonnes doit etre : Compte, Intitules, Budget Primitif, Budget Additionnel, Modifications +/-, Previsions Definitives, OR Admis, Recouvrement, Reste a Recouvrer, Taux d'Execution
- [x] T004 [US1] Mettre a jour les feuilles Depenses par programme dans `apps/backend/app/services/export_service.py` : passer de 8 a 11 colonnes en ajoutant "Modifications +/-" (valeur `values.modifications`) apres "Budget Additionnel", "Engagement" (valeur `values.engagement`) apres "Previsions Definitives", et "Taux d'Execution" (valeur `computed.taux_execution` formatee en pourcentage) en derniere colonne. Ajouter des lignes d'en-tete de section "DEPENSES DE FONCTIONNEMENT" et "DEPENSES D'INVESTISSEMENT". L'ordre des colonnes doit etre : Compte, Intitules, Budget Primitif, Budget Additionnel, Modifications +/-, Previsions Definitives, Engagement, Mandat Admis, Paiement, Reste a Payer, Taux d'Execution
- [x] T005 [US1] Ajouter une nouvelle feuille "Recap Dep par Prog" dans `apps/backend/app/services/export_service.py` en utilisant les donnees de `calculate_depenses_recap()`. La feuille doit presenter un croisement categories (lignes) x programmes (colonnes) avec 3 groupes de colonnes : Mandatement (Prog I, Prog II, ..., Total), Paiement (Prog I, Prog II, ..., Total), Reste a Payer (Prog I, Prog II, ..., Total). Chaque categorie affiche les valeurs `mandat_admis`, `paiement`, `reste_a_payer` par programme. Inserer cette feuille entre les feuilles Depenses et Recap Depenses
- [x] T006 [US1] Mettre a jour la feuille "Recap Depenses" dans `apps/backend/app/services/export_service.py` pour afficher 5 colonnes (Compte, Intitules, Mandat Admis, Paiement, Reste a Payer) au lieu du format actuel avec colonnes par programme. Les valeurs sont les totaux tous programmes confondus depuis `total_section` de `calculate_depenses_recap()`. Ajouter les separations Fonctionnement/Investissement
- [x] T007 [US1] Mettre a jour la feuille "Equilibre" dans `apps/backend/app/services/export_service.py` pour presenter les depenses et recettes en vis-a-vis sur les memes lignes : colonnes gauche (Compte, Intitules, Mandat Admis, Paiement, Reste a Payer) et colonnes droite (Compte, Intitules, OR Admis, Recouvrement, Reste a Recouvrer). Ajouter les sous-totaux par section (Fonctionnement, Investissement), les lignes d'operations d'ordre, et le resultat definitif (excedent/deficit)
- [x] T008 [US1] Appliquer la mise en forme conforme au template de reference dans `apps/backend/app/services/export_service.py` sur toutes les feuilles : (1) bordures thin (openpyxl Border/Side) sur toutes les cellules de donnees et en-tetes, (2) largeurs de colonnes fixes pour les colonnes numeriques (15 caracteres) et dynamiques pour les intitules, (3) lignes de niveau 1 en gras sans retrait, lignes de niveau 2 avec 2 espaces de retrait, lignes de niveau 3 avec 4 espaces de retrait, (4) en-tetes de colonnes en gras avec fond colore (header_fill existant), (5) lignes de section (FONCTIONNEMENT/INVESTISSEMENT) en gras avec fond section_fill

**Checkpoint**: L'export Excel contient les 8 feuilles avec toutes les colonnes et la mise en forme conforme au template. Verifiable via `curl -o test.xlsx "http://localhost:8000/api/public/collectivites/commune/{id}/comptes/{annee}/export?format=xlsx"`

---

## Phase 3: User Story 3 - Boutons de telechargement sur la page de consultation (Priority: P1)

**Goal**: Les boutons de telechargement affichent un etat de chargement pendant la generation et gerent les erreurs

**Independent Test**: Visiter la page d'une collectivite, cliquer sur les boutons de telechargement et verifier les etats visuels (loading, disabled, erreur)

### Implementation for User Story 3

- [x] T009 [P] [US3] Mettre a jour `apps/frontend/app/composables/usePublicComptes.ts` pour que `downloadExport()` extraie le nom de fichier du header Content-Disposition de la reponse au lieu d'utiliser un nom genere cote client. Utiliser `response.headers.get('content-disposition')` pour parser le filename. Retourner aussi une indication de succes/echec pour la gestion d'erreur
- [x] T010 [P] [US3] Mettre a jour `apps/frontend/app/pages/collectivite/[type]-[id].vue` pour ajouter les etats de chargement : (1) ajouter deux refs `downloadingExcel` et `downloadingWord` (type boolean, defaut false), (2) desactiver le bouton correspondant et afficher un spinner (icone ou texte "Chargement...") pendant la generation, (3) afficher un message d'erreur (toast ou inline) si le telechargement echoue, (4) remettre le bouton a l'etat normal une fois le telechargement termine ou en erreur. Les boutons doivent etre accessibles en mode sombre (dark:) et responsive mobile

**Checkpoint**: Les boutons reagissent visuellement au clic, se desactivent pendant le telechargement, et affichent les erreurs

---

## Phase 4: User Story 2 - Telecharger le compte administratif au format Word (Priority: P2)

**Goal**: Le document Word contient tous les tableaux avec tous les niveaux et les sections recap

**Independent Test**: Telecharger le fichier Word et verifier que tous les tableaux sont presents avec les 3 niveaux hierarchiques et les sections Recapitulatifs

### Implementation for User Story 2

- [x] T011 [US2] Mettre a jour la generation des tableaux Recettes et Depenses dans `apps/backend/app/services/export_service.py` fonction `generate_word()` : (1) supprimer le filtre `if line["level"] > 2: continue` pour inclure les 3 niveaux, (2) ajouter les colonnes manquantes pour etre identique a l'Excel (Modifications +/-, Taux d'Execution pour recettes ; Modifications +/-, Engagement, Taux d'Execution pour depenses), (3) ajouter le retrait visuel via espaces dans les intitules (2 espaces niv2, 4 espaces niv3), (4) mettre en gras les lignes de niveau 1 via les runs dans les cellules Word
- [x] T012 [US2] Ajouter les sections Recapitulatif Recettes et Recapitulatif Depenses dans `apps/backend/app/services/export_service.py` fonction `generate_word()` : (1) apres les tableaux de depenses, ajouter un heading "Recapitulatif des recettes" avec un tableau reproduisant la structure de la feuille Recap Recettes (Compte, Intitules, Previsions Definitives, OR Admis, Recouvrement, Reste a Recouvrer) en utilisant `calculate_recettes_recap()`, (2) ajouter un heading "Recapitulatif des depenses" avec un tableau synthese (Compte, Intitules, Mandat Admis, Paiement, Reste a Payer) en utilisant `calculate_depenses_recap()`. Positionner ces sections avant la section Equilibre

**Checkpoint**: Le document Word contient tous les tableaux (Recettes 3 niveaux, Depenses par programme 3 niveaux, Recap Recettes, Recap Depenses, Equilibre) avec les memes donnees que l'Excel

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Verification finale et validation croisee

- [x] T013 Verification manuelle des edge cases dans `apps/backend/app/services/export_service.py` : (1) generer un export pour un compte sans donnees (toutes valeurs a zero) et verifier que les feuilles sont presentes avec la structure correcte, (2) verifier qu'un compte avec 2 programmes produit 2 feuilles de depenses (pas 3), (3) verifier le nommage de fichier avec une collectivite ayant des accents dans le nom
- [x] T014 Executer `ruff check apps/backend/` pour verifier que le code Python modifie respecte les regles de linting du projet

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Pas de dependance - peut commencer immediatement
- **US1 - Excel (Phase 2)**: Depend de Phase 1 (T001, T002 pour le nommage)
- **US3 - Frontend (Phase 3)**: Depend de Phase 1 (T002 pour Content-Disposition) - peut etre fait EN PARALLELE de Phase 2
- **US2 - Word (Phase 4)**: Depend de Phase 1 (T001, T002) ; recommande apres Phase 2 pour reutiliser les patterns de mise en forme
- **Polish (Phase 5)**: Depend de toutes les phases precedentes

### User Story Dependencies

- **US1 (P1 - Excel)**: Depend uniquement de Setup. Peut commencer des que T001/T002 sont termines
- **US3 (P1 - Frontend)**: Depend uniquement de Setup. PEUT etre fait en PARALLELE de US1 (fichiers differents : frontend vs backend)
- **US2 (P2 - Word)**: Depend de Setup. Recommande apres US1 (meme fichier `export_service.py`, patterns similaires)

### Within Each User Story

- US1 : T003 → T004 → T005 → T006 → T007 → T008 (meme fichier, sequentiel)
- US3 : T009 et T010 sont sur des fichiers differents → parallelisables [P]
- US2 : T011 → T012 (meme fichier, sequentiel)

### Parallel Opportunities

```
Phase 1: T001, T002 (sequentiels, meme fichier router)
Phase 2 + Phase 3 EN PARALLELE:
  Backend (US1): T003 → T004 → T005 → T006 → T007 → T008
  Frontend (US3): T009 [P] + T010 [P]
Phase 4 (US2): T011 → T012 (apres Phase 2)
Phase 5: T013, T014 (apres tout)
```

---

## Parallel Example: Phase 2 + Phase 3

```bash
# Backend Excel (US1) et Frontend boutons (US3) en parallele :
Agent 1: "Mettre a jour feuille Recettes avec 10 colonnes dans export_service.py"
Agent 2: "Ajouter etats loading aux boutons dans [type]-[id].vue"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 3)

1. Complete Phase 1: Setup (nommage fichier)
2. Complete Phase 2 + Phase 3 en parallele: Excel + Boutons frontend
3. **STOP and VALIDATE**: Tester l'export Excel complet depuis la page publique
4. Le visiteur peut telecharger un Excel conforme au template avec boutons reactifs

### Incremental Delivery

1. Setup (Phase 1) → Nommage de fichier conforme
2. US1 Excel (Phase 2) + US3 Frontend (Phase 3) en parallele → MVP fonctionnel
3. US2 Word (Phase 4) → Export Word complet
4. Polish (Phase 5) → Validation finale

---

## Notes

- [P] tasks = fichiers differents, pas de dependances
- [Story] label lie la tache a la user story pour tracabilite
- Tous les fichiers modifies existent deja - aucun nouveau fichier de production
- Les services de calcul (account_service.py) ne sont PAS modifies - seul export_service.py est touche
- Les donnees manquantes (modifications, engagement, taux_execution) sont deja disponibles dans les retours des services existants
- Commit apres chaque tache ou groupe logique
