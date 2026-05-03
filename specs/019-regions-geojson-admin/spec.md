# Feature Specification: Carte interactive Madagascar — GeoJSON administrable depuis le back-office

**Feature Branch**: `019-regions-geojson-admin`
**Created**: 2026-05-03
**Status**: Draft
**Input**: User description: "Carte interactive Madagascar : GeoJSON administrable dynamiquement depuis le back-office. Permettre aux administrateurs d'uploader un GeoJSON de régions de Madagascar depuis le back-office. Le backend traite le fichier (filtrage des features pertinentes, déduplication, simplification, normalisation des noms, indexation par code région) et persiste la version optimisée. La carte d'accueil consomme un endpoint qui sert la version active courante. Un historique des versions est conservé avec possibilité de rollback."

## Clarifications

### Session 2026-05-03

- Q: Rôles autorisés sur la page de gestion des géodonnées (upload, prévisualisation, activation, suppression) → A: `admin` uniquement (les `editor` n'ont aucun accès à cette section).
- Q: Mécanisme de suivi du traitement asynchrone (au-delà de 5 s) → A: Polling HTTP — l'upload retourne un identifiant de tâche, l'UI interroge un endpoint admin de statut jusqu'à `done` ou `failed`.
- Q: Comportement de la carte d'accueil pour une région du GeoJSON sans correspondance dans la table `regions` → A: Région affichée en couleur grisée neutre, tooltip « Données non disponibles », clic désactivé.
- Q: Conservation du fichier source brut téléversé → A: Non conservé. Seuls le GeoJSON traité, les statistiques (taille originale, taille traitée, nombre de features, liste des noms) et les avertissements persistent.
- Q: Périmètre du journal d'audit pour les opérations sur les versions → A: Standard — auteur, horodatage, type d'opération (`upload`/`activate`/`delete`), identifiant de version cible, résultat (succès/échec), motif en cas d'échec, statistiques résumées (nombre de features, taille traitée). Pas de snapshot du GeoJSON ni de diff détaillé.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Mettre à jour la carte d'accueil après une évolution administrative (Priority: P1)

Un administrateur de la plateforme PCQVP apprend qu'une nouvelle région malgache a été créée par scission (par exemple : Vatovavy-Fitovinany scindée en Vatovavy et Fitovinany en 2021, ou Analanjirofo scindée en Analanjirofo et Ambatosoa en 2023). Il télécharge un GeoJSON officiel (par exemple un export Overpass Turbo de plusieurs dizaines de Mo) contenant l'ensemble des entités administratives de Madagascar, se connecte au back-office, accède à la page de gestion des données géographiques, et téléverse le fichier. La plateforme nettoie, simplifie et stocke automatiquement la nouvelle version, l'administrateur la prévisualise, puis l'active. La carte d'accueil reflète la nouvelle géographie immédiatement, sans déploiement de code.

**Why this priority**: C'est la valeur centrale de la fonctionnalité : permettre à l'organisation de rester alignée avec la réalité administrative malgache sans dépendre du cycle de release. Sans cette capacité, la carte d'accueil — vitrine principale du site — devient progressivement inexacte.

**Independent Test**: Peut être testée seule en uploadant un GeoJSON contenant les 23 régions actuelles dans une instance vide, en l'activant, et en vérifiant que la carte d'accueil affiche désormais les 23 régions au lieu des 22 du package figé.

**Acceptance Scenarios**:

1. **Given** un administrateur connecté au back-office, **When** il téléverse un GeoJSON valide de 22 Mo via l'interface dédiée, **Then** le système accepte le fichier, exécute le pipeline de traitement (filtrage, déduplication, normalisation, simplification), persiste la version optimisée (< 1 Mo), et affiche les statistiques avant/après ainsi que la liste des régions reconnues.
2. **Given** une nouvelle version traitée et inactive, **When** l'administrateur clique sur « Activer » et confirme dans la modale, **Then** la version cible devient active, la précédente est désactivée, un journal d'audit est écrit, et la carte d'accueil consommée par les visiteurs renvoie immédiatement le nouveau GeoJSON.
3. **Given** un visiteur anonyme qui charge la page d'accueil, **When** la carte interactive s'initialise, **Then** elle récupère et affiche la version active des régions sans erreur, en moins de 2 s sur connexion 3G simulée, avec les interactions existantes (clic, survol, légende, dark/light) préservées.

---

### User Story 2 — Conserver un historique et revenir à une version précédente (Priority: P2)

Après une activation, l'administrateur constate que la nouvelle version contient une anomalie (région manquante, nom incorrect, géométrie dégradée). Il consulte la liste des versions, prévisualise une version antérieure, et la réactive en un clic. La carte d'accueil revient à l'état précédent immédiatement.

**Why this priority**: Sécurise l'opération d'upload en permettant un retour arrière sans intervention technique. Critique pour la confiance opérationnelle, mais conditionné à l'existence préalable de l'upload.

**Independent Test**: Peut être testée en activant successivement deux versions distinctes, puis en vérifiant que le rollback vers la première rétablit le GeoJSON correspondant côté endpoint public et côté carte d'accueil.

**Acceptance Scenarios**:

1. **Given** au moins deux versions persistées dont l'une est active, **When** l'administrateur prévisualise une version inactive via la modale dédiée, **Then** une mini-carte affiche la géométrie de cette version sans modifier l'état actif.
2. **Given** une version active et une version antérieure inactive, **When** l'administrateur active la version antérieure, **Then** la précédente devient inactive, l'antérieure devient active, et l'endpoint public sert le GeoJSON correspondant immédiatement.
3. **Given** une version active, **When** l'administrateur tente de la supprimer, **Then** le système refuse l'opération avec un message clair indiquant qu'une version active ne peut pas être supprimée.

---

### User Story 3 — Refuser et signaler les fichiers invalides ou suspects (Priority: P2)

Un administrateur upload par erreur un fichier non conforme (XML, CSV, JSON arbitraire, GeoJSON malformé, GeoJSON sans features régionales, fichier > 50 Mo, fichier contenant des propriétés HTML/JS suspectes). Le système refuse, explique pourquoi, et n'altère ni la version active ni l'historique.

**Why this priority**: Protège l'intégrité du contenu public et la sécurité de la plateforme. Indispensable mais inutile sans la capacité d'upload de base.

**Independent Test**: Peut être testée en soumettant chacun des cas invalides à l'endpoint d'upload et en vérifiant le code d'erreur, le message, et l'absence de mutation de l'historique.

**Acceptance Scenarios**:

1. **Given** un fichier d'extension `.csv` ou MIME non `application/json`, **When** l'administrateur l'upload, **Then** le système retourne une erreur claire (« format non supporté ») sans créer de version.
2. **Given** un GeoJSON syntaxiquement valide mais sans features de niveau administratif régional, **When** le pipeline s'exécute, **Then** aucune version n'est créée et un message indique qu'aucune région exploitable n'a été trouvée.
3. **Given** un GeoJSON contenant des propriétés au-delà du jeu autorisé (ex. balises HTML/JS, champs métier sensibles), **When** le pipeline s'exécute, **Then** seules les propriétés autorisées (`name`, `name_official`, `region_code`, `admin_level`) sont conservées et les autres sont supprimées silencieusement.
4. **Given** un fichier de plus de 50 Mo, **When** l'upload démarre, **Then** le système refuse avant traitement avec un message indiquant la limite.
5. **Given** un même administrateur ayant déjà uploadé 10 fichiers dans l'heure écoulée, **When** il tente un 11ᵉ upload, **Then** le système applique une limitation de débit et retourne un code d'erreur explicite.

---

### User Story 4 — Détecter les écarts de cohérence entre GeoJSON et base de données (Priority: P3)

Le GeoJSON uploadé peut contenir des régions absentes de la table des régions de la base de données métier (ex. nouvelle région créée dans le GeoJSON mais pas encore référencée en base). L'administrateur reçoit un avertissement non bloquant lui permettant de prendre une décision en connaissance de cause.

**Why this priority**: Améliore la qualité de l'opération mais n'empêche pas l'usage de base ni le rollback. Réduit les surprises sans bloquer le flux principal.

**Independent Test**: Peut être testée en uploadant un GeoJSON contenant une région fictive non présente en base et en vérifiant que la liste des avertissements remonte cette discordance.

**Acceptance Scenarios**:

1. **Given** un GeoJSON contenant une région dont le nom (après normalisation) n'a aucun équivalent en base, **When** le pipeline s'exécute, **Then** la version est créée et marquée avec un avertissement listant les noms non rapprochés. L'activation reste possible.
2. **Given** un GeoJSON pour lequel le nombre de features finales sort de la fourchette attendue (20–30), **When** le pipeline s'exécute, **Then** un avertissement est ajouté à la version, sans empêcher la création.

---

### Edge Cases

- Géométrie d'une feature qui devient nulle ou ponctuelle après simplification (surface < seuil minimal) : la feature est exclue et un avertissement est ajouté.
- Doublons par nom dans le GeoJSON source : seule la feature de plus grande surface est conservée.
- Nom contenant des accents, casses ou variantes orthographiques (ex. `Matsiatra Ambony` ↔ `Haute Matsiatra`) : table de correspondance applicable et code région stable basé sur le nom canonique.
- Quota de 50 versions atteint : la version inactive la plus ancienne est supprimée automatiquement avant l'enregistrement de la nouvelle. La version active n'est jamais évincée.
- Endpoint public temporairement indisponible : la carte d'accueil affiche un état d'erreur localisé sans planter la page.
- Réutilisation par un client navigateur : si l'identifiant de version n'a pas changé, la requête conditionnelle renvoie une réponse « non modifié » sans recharger le contenu.
- Activation concurrente par deux administrateurs : une seule activation aboutit, l'autre reçoit un échec explicite ; l'invariant « une seule version active » est garanti.

## Requirements *(mandatory)*

### Functional Requirements

#### Upload & traitement

- **FR-001**: La plateforme MUST permettre à un administrateur authentifié de téléverser un fichier GeoJSON depuis une page dédiée du back-office, via un formulaire multipart standard.
- **FR-002**: Le système MUST accepter les extensions `.geojson` et `.json` et refuser explicitement toute autre extension ou tout MIME non conforme avec un message d'erreur clair.
- **FR-003**: Le système MUST limiter la taille des fichiers téléversés à 50 Mo et refuser les fichiers excédant cette limite avant tout traitement.
- **FR-004**: Le système MUST appliquer une limitation de débit aux uploads (au plus 10 par administrateur et par heure).
- **FR-005**: Le système MUST exécuter, à chaque upload accepté, un pipeline de traitement automatique qui : (a) valide la structure `FeatureCollection` ; (b) ne conserve que les features de niveau administratif régional ayant un nom non vide et une géométrie polygonale ; (c) déduplique par nom en gardant la feature de plus grande surface ; (d) applique une table de correspondance de noms configurable ; (e) génère pour chaque région un code stable basé sur le nom canonique ; (f) simplifie les géométries selon un ratio configurable préservant la lisibilité ; (g) réduit la précision des coordonnées à 4 décimales ; (h) valide que chaque géométrie résultante reste exploitable (surface non nulle, sans auto-intersection).
- **FR-006**: Le système MUST conserver uniquement les propriétés autorisées (`name`, `name_official`, `region_code`, `admin_level`) et écarter toute autre propriété afin d'éviter l'injection de contenu HTML/JS via les attributs.
- **FR-007**: Le système MUST signaler par un avertissement non bloquant tout cas atypique : nombre de features finales hors fourchette attendue (20–30), région reconnue absente de la base de données métier, doublon évincé, feature simplifiée jusqu'à devenir non exploitable.
- **FR-008**: Le système MUST calculer et exposer après traitement les statistiques suivantes : taille initiale, taille traitée, nombre de features, liste des noms de régions, liste des avertissements.
- **FR-009**: Le système MUST traiter les fichiers en synchrone si le traitement aboutit en moins de 5 s. Au-delà, il MUST basculer en traitement asynchrone : l'appel d'upload retourne immédiatement un identifiant de tâche et un statut initial (`pending` ou `running`), et un endpoint admin de statut interrogeable par polling MUST permettre de connaître la progression jusqu'aux états terminaux `done` (renvoyant l'identifiant de la version créée) ou `failed` (renvoyant le motif). L'interface d'administration MUST afficher un indicateur de progression pendant le polling.
- **FR-010**: Le système MUST refuser tout fichier dont le contenu n'est pas un GeoJSON valide après tentative de parsing et MUST refuser tout GeoJSON ne produisant aucune feature exploitable, sans créer de version.

#### Versionnage & cycle de vie

- **FR-011**: Le système MUST persister chaque upload accepté comme une version distincte enregistrant : identifiant, date de création, auteur, nom du fichier original, taille originale, taille traitée, nombre de features, liste des noms, liste des avertissements, GeoJSON traité, état actif/inactif, notes optionnelles. Le contenu brut du fichier source téléversé n'est PAS persisté : il est libéré à la fin du pipeline ; seules les métadonnées dérivées (nom du fichier, tailles, statistiques, avertissements) et le GeoJSON traité sont conservés.
- **FR-012**: À tout instant, exactement une version peut être active, et cet invariant MUST être garanti même en cas d'opérations concurrentes.
- **FR-013**: Une nouvelle version créée par upload MUST être inactive par défaut et nécessiter une action explicite d'activation par un administrateur.
- **FR-014**: Le système MUST permettre à un administrateur de lister, prévisualiser, activer et supprimer les versions, sauf la version active qui ne peut pas être supprimée.
- **FR-015**: L'activation d'une version MUST être atomique : la version cible devient active et la précédente devient inactive dans la même opération.
- **FR-016**: Le système MUST conserver au plus 50 versions ; au-delà, la version inactive la plus ancienne MUST être supprimée automatiquement, sans jamais évincer la version active.
- **FR-017**: Le système MUST écrire un journal d'audit pour chaque upload, activation et suppression, comportant : auteur, horodatage, type d'opération (`upload`/`activate`/`delete`), identifiant de la version cible, résultat (succès/échec), motif en cas d'échec, statistiques résumées (nombre de features, taille traitée). Le journal NE contient PAS de snapshot du GeoJSON ni de diff détaillé entre versions.

#### Lecture publique

- **FR-018**: Le système MUST exposer un endpoint public, sans authentification, renvoyant le GeoJSON traité de la version active courante.
- **FR-019**: La réponse publique MUST inclure des en-têtes de cache permettant la mise en cache navigateur pendant au moins une heure et un identifiant fort lié à la version active permettant une revalidation par requête conditionnelle.
- **FR-020**: Le système MUST renvoyer une réponse « non modifié » si le client présente un identifiant de version courant.

#### Initialisation & migration

- **FR-021**: Le système MUST inclure, dès la première mise en service de la fonctionnalité, une version initiale active correspondant aux 23 régions administratives actuelles de Madagascar, dérivée d'un GeoJSON de référence et déjà passée par le pipeline.
- **FR-022**: La migration créant la table de versions et insérant la version initiale MUST être réversible.

#### Carte d'accueil

- **FR-023**: La carte interactive de Madagascar de la page d'accueil MUST consommer le GeoJSON via l'endpoint public plutôt qu'un package figé.
- **FR-024**: La carte d'accueil MUST conserver l'ensemble des interactions existantes : clic, survol, légende, indicateurs de chargement, compatibilité dark/light.
- **FR-025**: La carte d'accueil MUST gérer un état d'erreur dégradé si l'endpoint est indisponible : afficher un message localisé dans la zone carte sans rendre la page non fonctionnelle.
- **FR-026**: La correspondance entre les régions affichées sur la carte et les régions référencées en base MUST se faire sur la base du nom normalisé (sans accents, casse uniformisée), et non sur un mapping codé en dur.
- **FR-029**: Lorsqu'une région du GeoJSON actif ne trouve aucune correspondance dans la table `regions` après normalisation, la carte d'accueil MUST afficher cette région avec une couleur grisée neutre, un tooltip indiquant « Données non disponibles » (localisé), et désactiver toute interaction de clic (pas de navigation). La région reste visible géographiquement.

#### Sécurité & traçabilité

- **FR-027**: Toutes les opérations d'administration (upload, listing, prévisualisation, activation, suppression) MUST exiger une authentification avec le rôle `admin`. Les utilisateurs portant uniquement le rôle `editor` n'ont aucun accès à cette section, ni en lecture ni en écriture.
- **FR-028**: Le système MUST écarter toute propriété GeoJSON susceptible de contenir du HTML, du JavaScript ou des données métier non autorisées avant persistance.

### Key Entities *(include if feature involves data)*

- **Version GeoJSON régions** : représente un instantané administrable de la géographie régionale de Madagascar. Attributs : identifiant, date de création, auteur, nom de fichier original, taille originale, taille traitée, nombre de features, liste des noms de régions, GeoJSON traité, état actif/inactif, avertissements, notes. Relation : appartient à un administrateur (auteur). Invariant : au plus une version active à un instant donné.
- **Avertissement de traitement** : message attaché à une version, décrivant un cas atypique détecté par le pipeline (région inconnue, doublon, nombre de features hors plage, géométrie évincée). Non bloquant.
- **Table de correspondance de noms** : ensemble de règles de normalisation appliquées pendant le pipeline pour aligner les noms du GeoJSON source avec les noms canoniques utilisés par la plateforme.
- **Journal d'audit géodonnées** : enregistrement immuable des actions administratives sur les versions (upload, activation, suppression), pour traçabilité.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un administrateur peut publier une nouvelle géographie régionale (upload + activation + propagation à la carte d'accueil) en moins de 5 minutes, sans intervention de l'équipe technique ni redéploiement.
- **SC-002**: La carte d'accueil affiche la version active en moins de 2 secondes sur une connexion 3G simulée, et la charge utile servie reste inférieure à 1 Mo (cible 300–800 Ko).
- **SC-003**: Pour un fichier source de 22 Mo, le pipeline produit une version traitée en moins de 30 secondes (synchrone ou asynchrone), avec un taux de réduction de taille d'au moins 95 %.
- **SC-004**: 100 % des fichiers non conformes (mauvaise extension, MIME invalide, taille excessive, GeoJSON malformé, absence de features régionales) sont refusés avec un message d'erreur compréhensible, sans création de version.
- **SC-005**: Le rollback vers une version antérieure rétablit la carte d'accueil dans l'état correspondant en moins de 5 secondes après confirmation.
- **SC-006**: Aucune régression visible sur les 22 régions historiques après bascule de la source figée vers l'endpoint dynamique (les interactions clic, survol, légende, dark/light fonctionnent à l'identique).
- **SC-007**: 100 % des opérations administratives sur les versions (upload, activation, suppression) sont tracées dans le journal d'audit avec auteur et horodatage.
- **SC-008**: L'invariant « une seule version active » est respecté à 100 % en scénarios concurrents (deux activations simultanées : une seule réussit).
- **SC-009**: Le quota de stockage (50 versions maximum) est respecté en continu : aucune version active n'est jamais évincée par le mécanisme de purge.

## Assumptions

- Les administrateurs disposent déjà d'un compte avec privilèges d'administration sur le back-office et savent récupérer un GeoJSON régional auprès d'une source officielle (ex. export Overpass Turbo).
- La fonctionnalité cible exclusivement les régions de Madagascar dans cette itération ; la solution reste générique pour une réutilisation future, mais l'extension multi-pays n'est pas livrée.
- La fonctionnalité ne propose pas d'éditeur graphique de polygones : l'administrateur prépare son GeoJSON en amont avec des outils tiers.
- La table des régions de la base de données métier est réputée alignée avec la géographie active à un instant donné. Les écarts éventuels (régions manquantes en base après création administrative récente) sont gérés hors-périmètre direct, par une migration métier séparée. La carte affichera les régions sans données comme « non renseignées » sans bloquer.
- La page d'accueil tolère une fenêtre courte d'erreur si l'endpoint est indisponible : un message localisé est acceptable, l'absence totale de carte également ; le crash de la page ne l'est pas.
- Le journal d'audit existant de la plateforme (utilisé par d'autres entités administrables) est réutilisé pour enregistrer les opérations sur les versions de géodonnées.
- Le seuil de bascule synchrone/asynchrone (5 s) est calibré en fonction de la performance observée sur le matériel cible ; un dépassement régulier déclencherait l'activation par défaut du mode asynchrone.
- La table de correspondance de noms est gérée par les administrateurs techniques (configuration applicative) et non exposée comme entité administrable dans cette itération.
