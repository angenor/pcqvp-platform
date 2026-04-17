# Chapitre 6 : Contenu editorial

## Presentation

La section editoriale permet de gerer dynamiquement le contenu de la page d'accueil et du pied de page du site public, sans intervention technique. Les modifications prennent effet immediatement et sont accessibles a tous les visiteurs.

## Acces

- URL : `/admin/editorial`
- Page unique organisee en 3 onglets

---

## Onglet 1 : Section Hero (bandeau principal)

Le hero est la premiere section visible sur la page d'accueil. Il donne une impression generale du site et doit refleter l'identite visuelle de la plateforme.

### Champs disponibles

| Champ | Obligatoire | Limite |
|---|---|---|
| Titre | Oui | 255 caracteres |
| Sous-titre | Non | 255 caracteres |
| Description | Non | 500 caracteres |
| Image de fond | Non | 5 Mo (JPEG, PNG, WebP, GIF) |

**Titre** : texte principal affiche en grand sur le bandeau. Ce champ est obligatoire.

**Sous-titre** : texte complementaire affiche sous le titre, generalement une formulation concise du mandat de la plateforme.

**Description** : paragraphe explicatif donnant un contexte supplementaire. Limite a 500 caracteres.

**Image de fond** : photo ou illustration affichee en arriere-plan pleine largeur. L'editeur d'image integre permet le recadrage et le redimensionnement. Trois variantes sont generees automatiquement (basse qualite, qualite moyenne, qualite originale) pour optimiser le chargement selon la connexion du visiteur. Si aucune image n'est definie, une image par defaut est utilisee.

### Affichage public

- Image en arriere-plan pleine largeur du viewport
- Titre et sous-titre superposes au centre de l'image
- Description affichee en dessous
- Mise en page responsive : la taille du texte s'adapte aux ecrans mobiles

---

## Onglet 2 : Contenu de la page (Body)

Cette section affiche un contenu contextuel apres le selecteur geographique sur la page d'accueil. Elle peut accueillir des explications, des statistiques, des images ou tout autre contenu editorial pertinent.

### Editeur riche (EditorJS)

Le contenu est saisi via EditorJS, un editeur par blocs. Chaque element de contenu est un bloc independant que l'on peut ajouter, reordonner ou supprimer.

**Types de blocs disponibles :**

- **Paragraphe** : texte simple avec mise en forme (gras, italique, liens)
- **Titre** : niveaux h1, h2 ou h3
- **Image** : upload depuis le poste de travail ou insertion par URL, avec champ de legende
- **Tableau** : grille de lignes et colonnes editables directement dans l'interface
- **Liste** : liste a puces ou liste numerotee

**Fonctionnalites de l'editeur :**

- Glisser-deposer pour reordonner les blocs
- Le collage de texte depuis une source externe (traitement de texte, site web) nettoie automatiquement le HTML non desire

### Stockage

Le contenu est enregistre au format JSON natif EditorJS et persiste en base de donnees dans le champ `content_json`. Ce format garantit une compatibilite avec le rendu cote frontend et facilite les evolutions futures de la structure.

---

## Onglet 3 : Pied de page (Footer)

Le footer est affiche sur toutes les pages du site public. Il regroupe les informations institutionnelles, les coordonnees de contact et des liens vers des ressources externes.

### Section "A propos"

Editeur riche EditorJS avec les memes fonctionnalites que le body (paragraphes, titres, listes, images, tableaux). Cette section accueille generalement un texte de presentation de l'organisation.

### Section "Contact"

Coordonnees de contact affichees dans le footer.

| Champ | Type | Limite |
|---|---|---|
| Email | Adresse email | Standard |
| Telephone | Texte | 50 caracteres |
| Adresse | Texte | 500 caracteres |

### Section "Ressources"

Liste de liens utiles presentee dans le footer. Chaque lien comporte un titre (texte cliquable) et une URL (destination).

**Actions disponibles :**

- **Ajouter un lien** : saisir un titre et une URL, puis valider
- **Modifier un lien** : edition en ligne sans rechargement de page
- **Supprimer un lien** : une confirmation est requise avant la suppression definitive
- **Reordonner** : utiliser les boutons monter/descendre pour ajuster l'ordre d'affichage

---

## Workflow de publication

Les modifications apportees dans l'interface editoriale sont publiees **immediatement** apres la sauvegarde. Il n'existe pas de workflow de validation ou de mise en attente : toute modification devient visible pour les visiteurs du site public des son enregistrement.

Si aucun contenu n'est defini pour une section, des valeurs par defaut sont affichees automatiquement. Le contenu sauvegarde est persistant sur l'ensemble des pages du site.

---

## Upload d'images

Les images peuvent etre uploadees depuis l'editeur de contenu (body, footer) ou depuis l'editeur du hero.

| Parametre | Valeur |
|---|---|
| Endpoint upload fichier | `POST /api/admin/upload/image` |
| Endpoint upload par URL | `POST /api/admin/upload/image-by-url` |
| Types autorises | JPEG, PNG, WebP, GIF |
| Taille maximale | 5 Mo |
| Nommage | UUID (sans risque de collision ni de traversee de chemin) |

Les fichiers sont identifies par un UUID genere automatiquement, ce qui evite les conflits de noms et garantit la securite du stockage.
