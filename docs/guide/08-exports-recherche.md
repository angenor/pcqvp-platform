# Chapitre 8 - Exports et recherche

## Export Excel (.xlsx)

### Presentation

Les comptes administratifs publies peuvent etre exportes au format Excel pour analyse hors ligne. Cette fonctionnalite est accessible depuis la page de consultation publique de chaque compte.

### Structure du classeur

Le classeur genere contient une feuille par programme de depenses, ainsi que plusieurs feuilles recapitulatives :

- **Recap Recettes** : synthese de l'ensemble des recettes du compte
- **Recap Depenses par Programme** : ventilation des depenses selon les programmes
- **Recap Depenses** : synthese globale des depenses
- **Equilibre** : tableau de l'equilibre budgetaire (recettes / depenses)

### Mise en forme

Le fichier Excel est genere avec une mise en forme adaptee a la lecture et a l'impression :

- En-tetes de colonnes en gras
- Largeurs de colonnes ajustees automatiquement au contenu
- Indentation hierarchique selon les niveaux (niveau 1, 2, 3)
- Bordures de section pour delimiter les blocs de donnees
- Valeurs pre-calculees : les totaux sont inscrits directement, sans formules Excel, ce qui garantit la stabilite du fichier quel que soit le logiciel utilisé pour l'ouvrir

Le nom du fichier suit la convention suivante : `Compte_Administratif_[NomCollectivite]_[Annee].xlsx`

### Utilisation

Le bouton **Exporter Excel** est disponible sur la page de consultation publique d'un compte. Pendant la generation du fichier :

- Un indicateur de chargement s'affiche
- Le bouton est desactive pour eviter les doublons de telechargement
- Un message d'erreur s'affiche si la generation echoue

---

## Export Word (.docx)

### Structure

Le document Word genere reprend la meme organisation que le fichier Excel :

- Un en-tete avec le nom de la collectivite et l'annee d'exercice
- Un tableau par section, avec les memes donnees que l'export Excel

Le nom du fichier suit la convention suivante : `Compte_Administratif_[NomCollectivite]_[Annee].docx`

### Utilisation

L'export Word utilise la meme interface que l'export Excel. Le bouton **Exporter Word** est place a cote du bouton Excel sur la page de consultation publique. Le comportement (indicateur de chargement, desactivation du bouton, message d'erreur) est identique.

---

## Recherche plein texte

### Fonctionnement

Un champ de recherche global est disponible dans l'en-tete sur toutes les pages publiques de la plateforme. La page de resultats est accessible a l'URL `/recherche`.

### Index de recherche

La recherche s'appuie sur des index TSVECTOR PostgreSQL appliques aux tables suivantes :

- Provinces (champ nom)
- Regions (champ nom)
- Communes (champ nom)

Les index sont de type GIN, ce qui assure des performances optimales meme sur un volume important de donnees.

### Fonctionnalites

- **Auto-completion** : un menu deroulant affiche 8 a 10 resultats pendant la saisie, regroupes par type de collectivite (Province, Region, Commune)
- **Recherche etendue** : les resultats couvrent les noms de collectivites et les comptes administratifs publies (commune + annee)
- **Insensible aux accents et a la casse** : la recherche traite de maniere equivalente les variantes accentuees et les differences de casse
- **Configuration linguistique francaise** : la lemmatisation et le traitement des mots vides sont adaptes au francais
- **Limitation de debit par IP** : un mecanisme anti-abus limite le nombre de requetes par adresse IP afin de proteger la plateforme contre les usages excessifs

### Resultats

Les resultats de recherche sont organises de la facon suivante :

- Regroupes par type de collectivite (Province, Region, Commune)
- Chaque resultat contient un lien direct vers la page de la collectivite
- Si un compte administratif publie existe pour la collectivite, un lien vers la consultation du compte est egalement affiche

### Recherche dans l'interface d'administration

L'interface d'administration dispose de fonctions de filtrage et de recherche propres a chaque section :

- **Pages geographiques** (provinces, regions, communes) : recherche par nom ou par code
- **Comptes administratifs** : filtrage par type de collectivite, province, region et annee d'exercice
- **Newsletter** : recherche par adresse email
- **Templates** : recherche par code de ligne budgetaire ou par intitule de ligne
