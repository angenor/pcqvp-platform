# Chapitre 4 - Comptes administratifs

## Présentation

Les comptes administratifs représentent les données financières (recettes et dépenses) des collectivités territoriales pour une année d'exercice donnée. C'est la fonctionnalité principale de la plateforme.

Chaque compte est associé à une collectivité unique (Province, Région ou Commune) et à une année d'exercice. Il regroupe l'ensemble des données budgétaires saisies selon un template structuré, et peut être publié pour devenir visible sur l'interface publique.

---

## Cycle de vie d'un compte

1. **Brouillon** : créé et édité par un administrateur ou un éditeur. Non visible sur l'interface publique.
2. **Publié** : visible sur l'interface publique. Seul un administrateur peut publier ou dépublier un compte.

Toute modification apportée à un compte publié est journalisée : utilisateur ayant effectué la modification, date et heure, anciennes valeurs et nouvelles valeurs.

---

## Liste des comptes

**Accès** : `/admin/accounts`

La liste affiche l'ensemble des comptes administratifs créés sur la plateforme.

### Filtres disponibles

- Type de collectivité : Province, Région ou Commune
- Province : menu déroulant listant toutes les provinces
- Région : menu déroulant dépendant de la province sélectionnée
- Année d'exercice

### Colonnes du tableau

| Colonne | Description |
|---|---|
| Collectivité | Nom de la collectivité concernée |
| Type | Province, Région ou Commune |
| Année | Année d'exercice |
| Statut | Brouillon ou Publié |
| Dernière modification | Date et auteur de la dernière mise à jour |

### Actions disponibles par compte

- Voir le détail du compte
- Accéder aux recettes
- Accéder aux dépenses
- Publier ou dépublier (administrateur uniquement)

---

## Créer un compte

1. Aller à `/admin/accounts`
2. Cliquer sur "Nouveau compte"
3. Remplir le formulaire :
   - **Type de collectivité** (obligatoire) : Province, Région ou Commune
   - **Province** (obligatoire) : menu déroulant
   - **Région** (conditionnel, obligatoire si le type est Région ou Commune)
   - **Commune** (conditionnel, obligatoire si le type est Commune)
   - **Année d'exercice** (obligatoire) : valeur numérique
4. La validation garantit l'unicité de la combinaison type + collectivité + année. Un compte existant pour la même collectivité et la même année ne peut pas être recréé.
5. Après la création, la plateforme redirige automatiquement vers la page de saisie des recettes.

---

## Saisie des recettes

**Accès** : `/admin/accounts/[id]/recettes`

### Structure du tableau

La grille de saisie est basée sur le template actif de type "recette". Elle présente une structure hiérarchique à trois niveaux :

- **Niveau 1** : catégories principales, affichées en gras
- **Niveau 2** : sous-catégories, indentées
- **Niveau 3** : lignes détaillées, indentées davantage

Les données sont organisées en deux grandes sections : **Fonctionnement** et **Investissement**.

### Colonnes

| Colonne | Type | Description |
|---|---|---|
| Budget Primitif | Saisie | Budget initial voté |
| Additionnel | Saisie | Budget supplémentaire voté |
| Modifications | Saisie | Rectifications en cours d'exercice |
| Prévisions Définitives | Calculé | Budget Primitif + Additionnel + Modifications |
| OR Admis | Saisie | Ordres de recettes admis |
| Recouvrement | Saisie | Montants effectivement recouvrés |
| Reste à Recouvrer | Calculé | OR Admis - Recouvrement |
| Taux d'Exécution | Calculé | OR Admis / Prévisions Définitives |

### Sauvegarde

La sauvegarde s'effectue ligne par ligne. Chaque ligne affiche un indicateur de statut :

- **En attente** : modification non encore enregistrée
- **Succès** : enregistrement confirmé
- **Erreur** : échec de l'enregistrement (message d'erreur affiché)

### Calculs automatiques des totaux hiérarchiques

Les lignes de niveau 1 et de niveau 2 calculent automatiquement la somme de leurs lignes enfants. La saisie directe n'est autorisée qu'au niveau 3.

---

## Saisie des dépenses

**Accès** : `/admin/accounts/[id]/depenses`

### Organisation par programmes

Les dépenses sont organisées par **programmes**, présentés sous forme d'onglets. Trois programmes sont créés par défaut lors de la création du compte :

- Administration
- Développement
- Santé

### Gestion des programmes

| Action | Description |
|---|---|
| Ajouter un programme | Saisir l'intitulé du nouveau programme |
| Modifier le nom | Édition en ligne du nom du programme |
| Supprimer un programme | Suppression avec confirmation obligatoire |

### Colonnes

| Colonne | Type | Description |
|---|---|---|
| Budget Primitif | Saisie | Budget initial voté |
| Additionnel | Saisie | Budget supplémentaire voté |
| Modifications | Saisie | Rectifications en cours d'exercice |
| Prévisions Définitives | Calculé | Budget Primitif + Additionnel + Modifications |
| Engagement | Saisie | Montants engagés |
| Mandat Admis | Saisie | Mandats de paiement admis |
| Paiement | Saisie | Montants effectivement payés |
| Reste à Payer | Calculé | Mandat Admis - Paiement |
| Taux d'Exécution | Calculé | Mandat Admis / Prévisions Définitives |

La structure hiérarchique à trois niveaux et la sauvegarde ligne par ligne fonctionnent de la même manière que pour les recettes.

---

## Formules automatiques

Toutes les colonnes calculées sont mises à jour automatiquement lors de la saisie. Aucune intervention manuelle n'est requise.

### Recettes

| Colonne | Formule |
|---|---|
| Prévisions Définitives | Budget Primitif + Additionnel + Modifications |
| Reste à Recouvrer | OR Admis - Recouvrement |
| Taux d'Exécution | OR Admis / Prévisions Définitives |

### Dépenses

| Colonne | Formule |
|---|---|
| Prévisions Définitives | Budget Primitif + Additionnel + Modifications |
| Reste à Payer | Mandat Admis - Paiement |
| Taux d'Exécution | Mandat Admis / Prévisions Définitives |

### Totaux hiérarchiques

- Niveau 3 : valeurs saisies manuellement
- Niveau 2 : somme automatique des lignes de niveau 3 enfants
- Niveau 1 : somme automatique des lignes de niveau 2 enfants

---

## Récapitulatifs

**Accès** : `/admin/accounts/[id]/recap`

La page de récapitulatifs présente une synthèse des données financières du compte en trois sections.

### 1. Récapitulatif des recettes

Synthèse par catégories de niveau 1, avec sous-totaux par section (Fonctionnement et Investissement). Permet d'avoir une vue d'ensemble des recettes sans entrer dans le détail de chaque ligne.

### 2. Récapitulatif des dépenses

Tableau croisé présentant les catégories en lignes et les programmes en colonnes. Permet de comparer la répartition des dépenses entre les différents programmes pour chaque catégorie.

### 3. Equilibre

Comparaison des recettes et des dépenses par section (Fonctionnement et Investissement). Met en évidence les excédents ou déficits par section et au niveau global du compte.

---

## Publication (administrateur uniquement)

La publication rend un compte visible sur l'interface publique de la plateforme.

### Publier un compte

- Depuis la liste des comptes ou depuis la page de détail d'un compte
- Cliquer sur "Publier"
- Le statut passe à **Publié**, affiché avec un badge vert

### Dépublier un compte

- Cliquer sur "Dépublier"
- Le statut repasse à **Brouillon**, affiché avec un badge gris
- Le compte n'est plus accessible sur l'interface publique

Les boutons de publication et dépublication sont réservés aux utilisateurs ayant le rôle **administrateur**. Les éditeurs ne peuvent pas modifier le statut de publication.

---

## Détail d'un compte

**Accès** : `/admin/accounts/[id]`

La page de détail affiche les informations générales du compte ainsi que des liens de navigation rapide.

### Informations affichées

- Collectivité et type (Province, Région ou Commune)
- Année d'exercice
- Statut (Brouillon ou Publié)
- Date de création et date de dernière modification
- Auteur de la dernière modification

### Navigation rapide

Liens directs vers :

- La saisie des recettes
- La saisie des dépenses
- Les récapitulatifs

### Programmes de dépenses

La page liste également les programmes de dépenses associés au compte, avec leur intitulé et le nombre de lignes de données saisies.
