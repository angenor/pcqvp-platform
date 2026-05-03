# Gestion des géodonnées (carte des régions)

Ce guide s'adresse aux **administrateurs** de la plateforme PCQVP. Il décrit
comment publier une nouvelle version du fond de carte des 23 régions de
Madagascar, comment revenir en arrière (rollback), et comment interpréter les
avertissements affichés.

> Rôle requis : `admin`. Les comptes `editor` n'ont pas accès au back-office
> géodonnées (FR-027).

---

## 1. Préparer le fichier GeoJSON depuis Overpass Turbo

1. Ouvrir [https://overpass-turbo.eu](https://overpass-turbo.eu).
2. Coller la requête suivante :

   ```overpassql
   [out:json][timeout:90];
   area["ISO3166-1"="MG"][admin_level=2]->.mg;
   relation(area.mg)[boundary=administrative][admin_level=4];
   out geom;
   ```

3. Cliquer sur **Run**, puis **Export → GeoJSON**.
4. Renommer le fichier exporté en `madagascar_regions_<date>.geojson` (ex.
   `madagascar_regions_2026-05-03.geojson`).

Le fichier brut peut peser entre 15 et 25 Mo : c'est attendu. La plateforme
le simplifie automatiquement à < 1 Mo lors du téléversement.

## 2. Téléverser une nouvelle version

1. Se connecter au back-office, menu **Géographie → Géodonnées**.
2. Cliquer **Téléverser une nouvelle version**.
3. Glisser-déposer le fichier `.geojson` (ou cliquer pour sélectionner).
4. Optionnel : ajouter une note (source, motif, date d'export Overpass).
5. Cliquer **Téléverser**. Le système :
   - vérifie l'extension, le type MIME, la taille (< 50 Mo) ;
   - parse en streaming, ne garde que les features `admin_level=4` ;
   - dédoublonne par nom (garde la plus grande aire) ;
   - applique les alias de noms (ex. *Matsiatra Ambony* → *Haute Matsiatra*) ;
   - assigne un `region_code` stable (ex. `MG-haute-matsiatra`) ;
   - simplifie la géométrie (Visvalingam-weighted, ratio 0.04) ;
   - élague les propriétés non autorisées (HTML/JS supprimés) ;
   - arrondit les coordonnées à 4 décimales.

Le résultat s'affiche : `features_count`, taille traitée, liste des noms,
éventuels **avertissements** (cf. § 5).

## 3. Activer la version

Une version téléversée est **inactive** par défaut. Pour la publier :

1. Dans la table des versions, cliquer **Activer** sur la ligne souhaitée.
2. Confirmer dans le modal — la carte d'accueil reflète immédiatement la
   nouvelle version (cache CDN invalidé via `ETag`).

Une seule version peut être active à tout instant (invariant INV-1).

## 4. Rollback : réactiver une ancienne version

Pour revenir sur une version antérieure (ex. erreur dans le dernier upload) :

1. Aller dans **Géodonnées**, table « Versions ».
2. Repérer la version cible (date, auteur, taille).
3. Cliquer **Prévisualiser** pour vérifier la carte (modal interactif).
4. Cliquer **Activer**. Délai estimé < 5 secondes.

L'historique conserve jusqu'à **50 versions**. Au-delà, la plus ancienne
**inactive** est automatiquement purgée (LRU). La version active n'est jamais
purgée automatiquement.

## 5. Interpréter les avertissements

| Code                           | Sens                                                                  | Action conseillée                                |
| ------------------------------ | --------------------------------------------------------------------- | ------------------------------------------------ |
| `DUPLICATE_NAME_DROPPED`       | Plusieurs polygones ayant le même nom : conservé celui de plus grande aire | Vérifier la source si récurrent                  |
| `GEOMETRY_FIXED`               | Auto-intersection corrigée par `make_valid`                           | Aucun, mais inspecter visuellement la région     |
| `FEATURE_TOO_SMALL_DROPPED`    | Polygone supprimé après simplification (aire < 0.001 deg²)            | Probablement une enclave : contrôler             |
| `FEATURE_COUNT_OUT_OF_RANGE`   | Nombre de régions hors plage attendue (20–30)                         | Vérifier que l'export contient toutes les régions |
| `REGION_NOT_IN_DATABASE`       | Le nom n'a pas de correspondance dans la table `regions`              | Aucune (la région apparaîtra grise sur la carte) |

Sur la carte d'accueil, les régions du GeoJSON sans correspondance en base
s'affichent en **gris**, avec le tooltip `Données non disponibles` et clic
désactivé (FR-029).

## 6. Suppression d'une version

- Disponible uniquement pour les versions **inactives**.
- Supprimer la version active retourne `409 Conflict`.
- L'opération est irréversible : la suppression ne peut pas être défaite.

## 7. Limites & quotas

| Paramètre                            | Valeur par défaut         |
| ------------------------------------ | ------------------------- |
| Taille maximale du fichier upload    | 50 Mo                     |
| Nombre maximal de versions conservées | 50                        |
| Limite d'uploads par admin et par heure | 10                     |
| Timeout traitement synchrone         | 5 s (sinon job async)     |
| Précision coordonnées                | 4 décimales (~11 m)       |

## 8. Audit

Toutes les actions (upload, activation, suppression) sont enregistrées dans
`audit_logs` avec auteur, horodatage et identifiant de version. Voir le menu
**Administration → Journal d'audit**.
