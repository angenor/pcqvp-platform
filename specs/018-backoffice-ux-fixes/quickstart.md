# Quickstart — Validation manuelle du lot 018

Document complémentaire au plan d'implémentation. Sert de checklist opérationnelle
pour un validateur (QA, PO) sur un environnement de dev ou de préprod une fois
toutes les tâches terminées. Les critères d'acceptation formels restent ceux de
`spec.md` (US1–US4 + SC-001…SC-006).

## Pré-requis

- Backend lancé : `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` (port 8000).
- Frontend lancé : `pnpm dev` depuis `frontend/` (port 3000).
- Migration appliquée : `alembic upgrade head` (nouvelles tables `collectivity_documents` + `audit_logs`).
- Utilisateurs seed : un `admin` (accès complet) et un `editor` (accès édition).

Vérifier la bonne santé : `curl http://localhost:8000/health` → 200.

## US1 — Insertion d'image dans l'éditeur éditorial (P1)

1. Se connecter en `editor`, aller dans **OUTILS > ÉDITORIAUX**, ouvrir ou créer une page.
2. Cliquer sur l'onglet **Corps de page**.
3. Dans le bloc EditorJS, cliquer sur l'icône « + » puis sélectionner **Image**, choisir un PNG ou JPG < 5 Mo.
4. ✅ L'image doit être téléversée et apparaître inline en < 3 s.
5. Sauvegarder, ouvrir l'aperçu public → ✅ image visible au même emplacement.
6. Refaire avec un fichier interdit (ex. `.heic` ou 6 Mo) → ✅ message d'erreur explicite, contenu non altéré.

## US2 — Suppression d'un compte administratif (P2)

1. Se connecter en `admin`, aller dans **COMPTES > COMPTES ADMINISTRATIFS**.
2. Localiser un compte **en brouillon** (status = `draft`).
3. Cliquer sur l'action **Supprimer** → modal de confirmation.
4. Confirmer → ✅ le compte disparaît de la liste, toast de succès, plus visible côté public.
5. Vérifier via `SELECT * FROM audit_logs WHERE action='compte_administratif.deleted' ORDER BY created_at DESC LIMIT 5;` → ✅ une entrée avec `actor_user_id`, snapshot JSON.
6. Localiser un compte **publié**, cliquer **Supprimer** → ✅ modal affiche le message « Ce compte est publié… Repassez-le en brouillon avant suppression. » sans bouton de confirmation destructif.
7. Se connecter en `editor`, ouvrir la même liste → ✅ l'action **Supprimer** n'est pas affichée (ou appel direct renvoie 403).

## US3 — Documents officiels de collectivité (P2)

### Back-office

1. Se connecter en `admin`, aller dans **GÉOGRAPHIE > COMMUNES**, ouvrir une commune quelconque.
2. Repérer la section **Documents officiels** positionnée **après la bannière et avant la description riche**.
3. Cliquer **Ajouter un document**, choisir un PDF ≤ 20 Mo, saisir un titre (« Plan Communal de Développement 2026 ») → ✅ la ligne apparaît en fin de liste avec icône PDF + taille + date.
4. Ajouter un second document (DOCX) → ✅ idem.
5. Réordonner par glisser/déposer → ✅ ordre persisté après refresh.
6. Cliquer **Remplacer** sur le premier document, choisir une nouvelle version → ✅ même titre, même position, fichier effectivement nouveau, date de mise à jour actualisée.
7. Supprimer un document → ✅ disparu immédiatement, fichier n'est plus téléchargeable (404 sur son URL).
8. Tester les validations :
   - Format `.zip` → ✅ refus avec message clair.
   - Taille > 20 Mo → ✅ refus.
   - Titre vide → ✅ refus.
9. Répéter les étapes 1–7 sur une **Province** et sur une **Région** (même composant).

### Rendu public

10. Accéder à la page publique de la commune testée → ✅ la section **Documents officiels** apparaît après la bannière, liste chaque document avec **titre + icône de type + taille formatée + date de mise à jour**.
11. Cliquer un titre → ✅ téléchargement déclenché.
12. Dépublier la collectivité → ✅ la page publique redevient inaccessible (documents inclus).

## US4 — Raccourcis depuis la liste des communes (P3)

1. Se connecter en `editor`, aller dans **GÉOGRAPHIE > COMMUNES**.
2. Sur une ligne, cliquer **Voir les comptes** → ✅ redirection vers `/admin/accounts?collectivite_type=commune&collectivite_id={id}`, la liste est pré-filtrée.
3. Revenir, cliquer **Soumettre un compte** → ✅ redirection vers `/admin/accounts/new?...`, le sélecteur de commune est pré-rempli.
4. Tester sur une commune sans compte → ✅ liste vide avec message d'invitation à créer.

## Checks non-fonctionnels transverses

- [ ] Mode sombre vérifié sur chaque nouvelle interface (liste de documents back-office, rendu public, modal de suppression, raccourcis).
- [ ] Textes UI en français, aucune clé de traduction orpheline en console.
- [ ] Aucune erreur console (navigateur) ni warning backend non attendu.
- [ ] Ruff clean sur backend : `ruff check backend/`.
- [ ] Tests : `pytest` vert, coverage rapport ok (cibles ≥ 80 % sur les nouveaux fichiers).

## Critères de sortie

Le lot 018 peut être clôturé dès que :

- Les 4 user stories US1-US4 sont validées selon leurs critères d'acceptation (spec.md).
- Les checks non-fonctionnels ci-dessus passent.
- La migration Alembic est idempotente (upgrade / downgrade testés localement).
- Aucune régression détectée sur les écrans adjacents : création de compte administratif, édition de la bannière de collectivité, publication d'une page éditoriale.
