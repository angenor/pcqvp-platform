# Phase 0 — Research: Correctifs UX back-office (lot 018)

Ce document résout les points de conception ouverts avant l'implémentation.

## R1. Diagnostic du bug d'insertion d'image dans l'éditeur éditorial

**Decision** : aborder en trois étapes — reproduire en local, instrumenter la requête `POST /api/admin/upload/image`, puis appliquer le correctif le plus minimal (auth, MIME ou config du plugin). Aucune refonte du composant ni changement de plugin.

**Rationale** :
- `RichContentEditor.vue` configure `@editorjs/image` avec `endpoints.byFile = /api/admin/upload/image` et `field = 'image'` ; le backend `upload.py` expose exactement la même route, attend un champ `image`, répond `{success: 1, file: {url: ...}}` — c'est le contrat standard du plugin.
- Les deux causes les plus probables d'un échec silencieux sont :
  - **Propagation du Bearer token** : `@editorjs/image` fait l'upload via `fetch` interne ; selon la version du plugin, les `additionalRequestHeaders` peuvent être ignorés si l'objet est recalculé avant chaque requête. Si le token n'est pas envoyé, le backend répond 401, et l'image ne s'insère pas.
  - **Validation MIME** : Safari / certains appareils envoient `image/heic` ou un Content-Type générique ; le backend filtre strictement sur `ALLOWED_IMAGE_TYPES` (jpeg, png, webp, gif) et refuse tout le reste.
- D'autres pistes écartées : stockage disque (déjà validé par le flux bannière), CORS (frontend et backend partagent l'origine via le proxy Nuxt), taille (5 Mo alignée avec les autres entrées).

**Alternatives considered** :
- Remplacer `@editorjs/image` par un plugin custom → disproportionné, rejeté.
- Ajouter un proxy applicatif pour rattacher le token → FR-001 demande un fix minimal, rejeté.

**Action pour l'implémentation** : ajouter un test d'intégration backend qui simule l'upload attendu par `@editorjs/image` (FormData avec champ `image` + Authorization Bearer), et un test de non-régression côté frontend (manuel, checklist dans `quickstart.md`).

---

## R2. Choix du modèle de données pour les documents officiels de collectivité

**Decision** : **une seule table `collectivity_documents` avec trois colonnes FK nullables (`province_id`, `region_id`, `commune_id`) et une contrainte CHECK exigeant qu'exactement une soit renseignée.**

**Rationale** :
- La plateforme utilise déjà trois tables distinctes pour Province / Region / Commune avec `ondelete=RESTRICT` en cascade. Il n'y a pas de table parent commune « collectivité » à laquelle rattacher un polymorphisme naturel.
- Une table unique :
  - simplifie la réutilisation du composant frontend `CollectivityDocumentsEditor.vue` (un seul endpoint, un seul type TypeScript) ;
  - mutualise la migration, le schéma Pydantic, le routeur et les tests ;
  - préserve l'intégrité référentielle via trois FK strictes (`ondelete=CASCADE` : si la collectivité est supprimée, ses documents le sont aussi).
- La contrainte CHECK `(province_id IS NOT NULL)::int + (region_id IS NOT NULL)::int + (commune_id IS NOT NULL)::int = 1` garantit l'exclusivité.

**Alternatives considered** :
- **Trois tables séparées** (`province_documents`, `region_documents`, `commune_documents`) : intégrité la plus stricte mais triple le code modèle/schéma/routeur sans valeur ajoutée. Rejeté pour sur-ingénierie.
- **Polymorphisme via `collectivity_type` (string) + `collectivity_id` (UUID)** : flexible mais perd la garantie FK et les cascades. Contraire aux patterns existants du projet (`ondelete=RESTRICT` explicites). Rejeté.
- **Colonne JSONB dans la table collectivité** : casse le pattern « champ riche + upload dédié », empêche la réordo via API, pas d'URL stable pour les fichiers. Rejeté.

**Colonnes retenues** (détaillées dans `data-model.md`) : `id UUID`, `province_id / region_id / commune_id UUID nullable`, `title text NOT NULL`, `file_path text NOT NULL`, `file_mime text NOT NULL`, `file_size_bytes bigint NOT NULL`, `position int NOT NULL`, `created_at timestamptz`, `updated_at timestamptz`.

---

## R3. Interprétation concrète de « compte référencé » pour le blocage de suppression (FR-006a)

**Decision** : bloquer la suppression si **le compte est en statut `published`**. Message : « Ce compte est publié et peut être référencé par les pages publiques et les exports. Repassez-le en brouillon avant de le supprimer. » Fournir dans la réponse 409 la liste des conséquences (recette_lines, depense_programs, change_logs qui seront supprimés en cascade si l'admin repasse en brouillon puis supprime).

**Rationale** :
- L'exploration du schéma a confirmé qu'il n'existe aujourd'hui **aucune FK externe** pointant vers `comptes_administratifs` autre que les enfants cascade (recettes, dépenses, change_logs). Les « références » évoquées dans la spec (statistiques, exports) sont **dérivées publiquement** du statut `published` du compte, pas stockées dans une table de liaison.
- Utiliser le statut `published` comme proxy de « référencé » :
  - donne une règle **concrète, testable, vérifiable** (≠ NEEDS CLARIFICATION latent) ;
  - oblige l'admin à exécuter une action explicite (`toggleStatus` → `draft`) avant la suppression, ce qui est déjà dans son vocabulaire UI ;
  - n'introduit pas de nouvelle colonne ni table de référence ;
  - respecte FR-006a (blocage avec message explicite) et FR-006 (suppression définitive une fois autorisée).

**Alternatives considered** :
- **Scan d'une table d'exports archivés** : aucune table de ce type n'existe encore, créerait une dépendance fantôme. Rejeté.
- **Suppression logique (soft delete)** : rejetée par clarification (FR-006 = définitive).
- **Autorisation inconditionnelle avec avertissement** : rejetée par Q1 (option A = blocage).

**Conséquence pour l'UI** : le bouton « Supprimer » reste visible pour tous les comptes, mais l'action déclenche un modal qui, en cas de statut `published`, affiche uniquement le message de blocage sans option de confirmation (et propose un bouton « Repasser en brouillon » qui appelle l'endpoint existant).

---

## R4. Stratégie d'upload pour les documents officiels (PDF / DOC / DOCX / XLS / XLSX)

**Decision** : étendre le routeur existant `backend/app/routers/upload.py` avec un nouvel endpoint `POST /api/admin/upload/document` dédié, distinct de `POST /api/admin/upload/image`.

**Rationale** :
- Le routeur existant expose déjà un pattern éprouvé (validation MIME + taille, nommage de fichier aléatoire, stockage sous `/uploads/images/`). Un endpoint jumeau `document` reproduit ce pattern sous `/uploads/documents/` sans mélange de listes MIME.
- Garder un endpoint séparé évite deux pièges :
  1. Un administrateur ne peut pas uploader un PDF via la route image (séparation stricte de la surface d'attaque).
  2. Les limites de taille diffèrent (5 Mo image vs 20 Mo document).
- Le payload de réponse reste symétrique : `{success: 1, file: {url, name, size, mime}}` — `name`, `size`, `mime` sont **retournés** pour que le frontend persiste les métadonnées dans `collectivity_documents` sans seconde requête.

**Alternatives considered** :
- **Endpoint unique générique `/api/admin/upload`** avec type déduit du MIME : complique la validation et mélange les limites. Rejeté.
- **Upload direct vers un stockage objet (S3, MinIO)** : aucun fournisseur en place dans le projet, hors scope. Rejeté.

**Formats MIME acceptés** :
| Extension | MIME accepté |
|-----------|--------------|
| pdf | `application/pdf` |
| doc | `application/msword` |
| docx | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| xls | `application/vnd.ms-excel` |
| xlsx | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |

Limite : **20 Mo** (constante `MAX_DOCUMENT_SIZE = 20 * 1024 * 1024`).

---

## R5. Journalisation de la suppression d'un compte administratif (FR-007)

**Decision** : créer un service minimaliste `app/services/audit_log.py` qui insère une ligne dans une table `audit_logs` (colonnes : `id`, `actor_user_id`, `action` ∈ `{compte_administratif.deleted}`, `target_type`, `target_id`, `payload jsonb`, `created_at`). Réutilisé pour cette feature uniquement, extensible par design mais non étendu ici (cf. Q4 = C, audit documents hors scope).

**Rationale** :
- Aucun système d'audit n'existe à ce jour (vérifié : pas de modèle `audit_log` dans `backend/app/models/`).
- Une table dédiée est plus simple qu'un stream de logs applicatifs pour satisfaire FR-007 de manière mesurable (SC-002 : « 100 % des suppressions tracées »).
- Le payload JSONB permet de stocker le snapshot du compte (id, titre, collectivité, année, statut) au moment de la suppression — utile pour restitution ou audit a posteriori.

**Alternatives considered** :
- **Logs structurés uniquement** (loguru / logging) : non requêtable en base, insuffisant pour démontrer la conformité. Rejeté.
- **Extension de la table `change_logs` existante** (liée au compte) : problème de cascade — `change_logs.compte_administratif_id` est en cascade DELETE, donc les logs disparaîtraient au moment même où l'audit est requis. Rejeté.

**Migration** : ajouter la table `audit_logs` dans la même révision Alembic que `collectivity_documents`.

---

## R6. Ordre de tri (`position`) sur `collectivity_documents`

**Decision** : colonne `position INT NOT NULL` avec convention : la première entrée d'un parent a `position = 0`, chaque ajout incrémente. Réordo via endpoint dédié `PATCH /api/admin/collectivity-documents/reorder` qui accepte une liste ordonnée d'IDs pour un parent donné, réécrit les positions en bloc dans une transaction.

**Rationale** :
- Algorithme simple, déterministe, testable. Évite le « gap-based positioning » (positions float type 1.5) qui rendrait les requêtes SQL plus fragiles.
- Index `(province_id, position)`, `(region_id, position)`, `(commune_id, position)` pour garantir une lecture ordonnée rapide.

**Alternatives considered** :
- **Drag & drop avec positions flottantes** : nécessite rééquilibrage périodique, sur-ingénierie pour < 50 documents par collectivité. Rejeté.
- **Tri par `created_at` uniquement** : ne permet pas à l'admin de repositionner. Rejeté (FR-009 exige « réordonner »).

---

## R7. Permissions par action

**Decision** :
| Action | Rôle requis |
|--------|-------------|
| Upload image éditeur | `admin` ou `editor` (déjà en place) |
| CRUD documents officiels | `admin` ou `editor` (cohérent avec l'édition des collectivités) |
| Upload document officiel | `admin` ou `editor` |
| DELETE compte administratif | `admin` uniquement |
| Consultation publique | anonyme (toute page publique déjà ouverte) |

**Rationale** : aligne avec les permissions existantes des écrans concernés (édition géographique = editor+, gestion de comptes = admin).

---

## R8. Affichage public : emplacement et rendu

**Decision** : sur chaque page publique de collectivité (`pages/provinces/[id].vue`, `pages/regions/[id].vue`, `pages/communes/[id].vue`), afficher la section « Documents officiels » **immédiatement après la bannière** et **avant la description riche**. Rendu sous forme de liste verticale avec, pour chaque document : icône FontAwesome correspondant au type, titre (lien téléchargement), taille formatée (`1.2 Mo`), date de mise à jour au format `DD/MM/YYYY`.

**Rationale** : cohérent avec FR-008 côté back-office (documents positionnés après la bannière) pour donner au visiteur la même structure visuelle que l'admin voit côté édition. Icônes FontAwesome déjà dans le stack (`@fortawesome/vue-fontawesome`).

**Alternatives considered** :
- **Sidebar dédiée** : casse la cohérence avec l'ordre de saisie et duplique la structure entre mobile / desktop. Rejeté.
- **Drawer / modal** : enterre l'information. Rejeté.

---

## Résolution des NEEDS CLARIFICATION

Le Technical Context du plan ne contient **aucun marqueur NEEDS CLARIFICATION**. Les choix techniques sont tranchés par les clarifications de la spec (Q1-Q5), les patterns existants du projet, et les décisions R1-R8 ci-dessus.
