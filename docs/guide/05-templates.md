# Chapitre 5 - Templates de comptes

## Presentation

Les templates definissent la structure des tableaux comptables (recettes et depenses). Ils determinent les lignes, colonnes et formules de calcul utilises lors de la saisie des comptes administratifs. Chaque compte cree par un administrateur territorial est base sur un template actif, qui fixe le cadre de saisie des donnees financieres.

---

## Acces

- **URL** : `/admin/templates`
- La liste des templates affiche les informations suivantes pour chaque entree :
  - Nom du template
  - Type : Recette ou Depense
  - Version (ex : v1, v2...)
  - Statut : Actif ou Inactif
  - Nombre de lignes comptables
  - Nombre de colonnes
  - Date de creation

---

## Structure d'un template

Un template est compose de deux ensembles : les lignes comptables et les colonnes.

### Lignes (account_template_lines)

Chaque ligne represente une rubrique du tableau comptable. Elle est definie par les attributs suivants :

| Attribut | Description |
|---|---|
| **Code comptable** | Identifiant unique de la ligne (ex : `71`, `711`, `7111`) |
| **Intitule** | Nom ou description de la ligne (ex : `Impots et taxes`) |
| **Niveau** | Niveau hierarchique : 1, 2 ou 3 |
| **Code parent** | Reference au code comptable de la ligne parente |
| **Section** | Fonctionnement ou Investissement |
| **Ordre** | Position d'affichage dans le tableau |

Les niveaux determinent la hierarchie d'affichage et le mode de saisie :

- **Niveau 1** : Categories principales, affichees en gras. Leurs valeurs sont calculees automatiquement a partir des sous-categories.
- **Niveau 2** : Sous-categories, regroupant les lignes de detail.
- **Niveau 3** : Lignes de detail. Ce sont les seules lignes sur lesquelles la saisie directe est possible.

### Colonnes (account_template_columns)

Chaque colonne represente un champ du tableau comptable. Elle est definie par les attributs suivants :

| Attribut | Description |
|---|---|
| **Nom** | En-tete de la colonne (ex : `Budget Primitif`) |
| **Code** | Identifiant technique (ex : `budget_primitif`) |
| **Type de donnee** | `number`, `text` ou `percentage` |
| **Calculee** | Indique si la colonne est calculee automatiquement (`oui`) ou saisie manuellement (`non`) |
| **Formule** | Expression de calcul si la colonne est calculee |
| **Ordre** | Position d'affichage dans le tableau |

---

## Templates par defaut

La plateforme est livree avec deux templates de reference, importes depuis les fichiers Excel officiels.

### Template Recettes

- **168 lignes comptables** : 14 de niveau 1, 36 de niveau 2, 118 de niveau 3
- **8 colonnes** :
  1. Budget Primitif
  2. Additionnel
  3. Modifications
  4. Previsions Definitives
  5. OR Admis
  6. Recouvrement
  7. Reste a Recouvrer
  8. Taux Execution
- **Sections** : Fonctionnement et Investissement

### Template Depenses

- **273 lignes comptables par programme** : 16 de niveau 1, 59 de niveau 2, 198 de niveau 3
- **9 colonnes** :
  1. Budget Primitif
  2. Additionnel
  3. Modifications
  4. Previsions Definitives
  5. Engagement
  6. Mandat Admis
  7. Paiement
  8. Reste a Payer
  9. Taux Execution
- **3 programmes par defaut** : Administration, Developpement, Sante

---

## Consultation d'un template

Pour consulter le detail d'un template :

1. Cliquer sur le nom du template dans la liste.
2. L'interface affiche une vue arborescente hierarchique (niveaux 1, 2 et 3).
3. Les lignes sont regroupees par section (Fonctionnement / Investissement).
4. Un champ de recherche permet de filtrer les lignes par code comptable ou par intitule.
5. Des boutons permettent de replier ou de deplier l'ensemble de l'arbre.

---

## Modification d'un template

### Ajouter une ligne

Remplir le formulaire avec les champs obligatoires :

- Code comptable
- Intitule
- Niveau (1, 2 ou 3)
- Code parent (obligatoire pour les niveaux 2 et 3)
- Section (Fonctionnement ou Investissement)

### Supprimer une ligne

La suppression d'une ligne est soumise a validation. Une ligne ne peut pas etre supprimee si des comptes administratifs l'utilisent deja. Un message d'erreur est affiche dans ce cas.

---

## Versionnement

Le versionnement garantit la coherence des donnees financieres dans le temps :

- Chaque template possede un numero de version (v1, v2...).
- Un seul template peut etre actif par type (Recette ou Depense) a un instant donne.
- Les comptes administratifs sont lies a la version du template en vigueur au moment de leur creation.
- Toute modification structurelle d'un template (ajout ou suppression de lignes ou colonnes) entraine la creation d'une nouvelle version. L'ancienne version est conservee et reste associee aux comptes existants.

---

## Import

- Les templates sont importes depuis les fichiers Excel de reference officiels fournis par l'administration.
- L'import est **idempotent** : relancer l'operation n'engendre pas de doublons si les donnees sont identiques.
- L'import s'effectue via le script de seed :

```bash
python -m app.seed
```
