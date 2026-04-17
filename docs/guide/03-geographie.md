# Chapitre 3 - Gestion geographique

## Hierarchie geographique

La plateforme PCQVP organise les collectivites territoriales en trois niveaux imbriques :

```
Province (niveau 1) - 6 provinces
  └── Region (niveau 2) - 22 regions
       └── Commune (niveau 3) - ~1695 communes
```

Chaque niveau dispose des attributs suivants :

- **Nom** : denomination officielle de la collectivite
- **Code** : identifiant unique (ex. `PRV-ANT`)
- **Description** : contenu riche edite via EditorJS (paragraphes, titres, images, listes, tableaux)
- **Image banniere** : photographie ou illustration representative

Les relations entre niveaux sont gerees par des cles etrangeres en mode `RESTRICT` : il est impossible de supprimer une province qui contient des regions, ou une region qui contient des communes. La suppression doit toujours s'effectuer du niveau le plus bas vers le niveau le plus haut.

---

## Navigation dans l'administration

Les trois niveaux geographiques sont accessibles depuis le menu lateral de l'interface d'administration :

- `/admin/geography/provinces`
- `/admin/geography/regions`
- `/admin/geography/communes`

### Affichage en grille

Les collectivites sont presentees sous forme de cartes disposees en grille. La mise en page s'adapte automatiquement a la taille de l'ecran :

- 3 a 4 colonnes sur grand ecran (desktop)
- 2 colonnes sur tablette
- 1 colonne sur mobile

Les cartes dont la collectivite est associee a des comptes financiers sont visuellement mises en evidence.

### Navigation en profondeur

L'interface permet une navigation hierarchique naturelle : cliquer sur une province affiche ses regions, cliquer sur une region affiche ses communes. Un fil d'Ariane en haut de page permet de revenir a n'importe quel niveau de la navigation.

### Recherche

Une barre de recherche permet de filtrer les collectivites par nom ou par code. Le filtrage est effectue cote client, sans rechargement de page.

---

## Creer une province

1. Acceder a `/admin/geography/provinces`
2. Cliquer sur le bouton **Nouvelle province**
3. Renseigner le formulaire :
   - **Nom** (obligatoire)
   - **Code** (obligatoire, unique dans la base - ex. `PRV-ANT`)
   - **Description** (facultatif) : editeur riche EditorJS permettant d'inserer des paragraphes, des titres, des images, des listes et des tableaux
   - **Image banniere** (facultatif) : voir la section dediee ci-dessous
4. Cliquer sur **Enregistrer**

---

## Creer une region

Le processus est identique a la creation d'une province, avec une contrainte supplementaire : la region doit obligatoirement etre associee a une province existante, selectionnee dans un menu deroulant.

L'acces au formulaire de creation est possible depuis deux endroits :

- La liste generale des regions (`/admin/geography/regions`)
- La vue des regions d'une province specifique (en cliquant sur la province puis sur le bouton de creation)

---

## Creer une commune

Le processus est identique, la commune devant etre associee a une region existante.

L'acces au formulaire est possible depuis :

- La liste generale des communes (`/admin/geography/communes`)
- La vue des communes d'une region specifique

---

## Image banniere

### Caracteristiques techniques

- Formats acceptes : JPEG, PNG, WebP, GIF
- Taille maximale : 5 Mo
- Trois variantes sont generees automatiquement lors du telechargement : basse resolution, resolution moyenne, et resolution originale

### Editeur d'image integre

Apres selection du fichier, un editeur integre permet de recadrer et redimensionner l'image avant enregistrement.

### Affichage public

Sur la page publique de la collectivite, l'image banniere est affichee en pleine largeur avec une hauteur d'environ 250 a 300 pixels. Le nom et le type de la collectivite sont superposes au centre, avec un overlay sombre garantissant la lisibilite en mode sombre comme en mode clair.

Si aucune image n'est definie, un titre textuel classique est affiche a la place.

### Modification ou suppression

L'image peut etre remplacee ou supprimee depuis le formulaire d'edition de la collectivite.

---

## Donnees financieres associees

Depuis la page de detail d'une region, une section **Donnees Financieres** est accessible. Elle propose deux actions :

- **Voir les comptes** : redirige vers la liste des comptes financiers pre-filtree sur cette region
- **Soumettre un compte** : ouvre le formulaire de creation d'un compte avec la region pre-selectionnee

---

## Suppression

| Niveau | Condition de suppression |
|--------|--------------------------|
| Province | Impossible si elle contient des regions (erreur 409) |
| Region | Impossible si elle contient des communes (erreur 409) |
| Commune | Suppression libre |

Dans tous les cas, une confirmation explicite est demandee avant execution de la suppression.

---

## Recherche plein texte (backend)

La base de donnees PostgreSQL est configuree avec un index GIN sur les noms des collectivites, utilisant la configuration linguistique francaise (`french`). Cette configuration rend la recherche insensible aux accents et a la casse, et prend en charge la lemmatisation des termes francais.

La recherche plein texte est utilisee par l'API de recherche globale de la plateforme (`/api/search`), distincte du filtrage local disponible dans les listes d'administration.
