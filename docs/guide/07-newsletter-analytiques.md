# Chapitre 7 - Newsletter et analytiques

## Newsletter

### Presentation

La plateforme permet aux visiteurs de s'abonner a une newsletter par email. L'administration gere la liste des abonnes et peut consulter leur statut, rechercher par email et exporter les donnees.

### Acces admin

- URL : `/admin/newsletter`

### Fonctionnalites

- **Liste paginee** des abonnes (50 par page)
- **Filtrer par statut** :
  - `actif` : abonne confirme
  - `en_attente` : en attente de confirmation (double opt-in)
  - `desinscrit` : desabonne
- **Rechercher** par email
- **Exporter en CSV** : fichier avec horodatage dans le nom (ex : `subscribers_2024-03-15.csv`)
  - Contenu : email, statut, date d'inscription
- **Supprimer** un abonne individuellement (confirmation requise)
- Affichage du nombre total d'abonnes

### Cote public

- Formulaire d'inscription dans le footer ou page dediee
- Double opt-in : un email de confirmation est envoye apres inscription
- Lien de desinscription inclus dans chaque email envoye
- Limitation de debit par adresse IP (protection anti-spam)

---

## Analytiques

### Presentation

Le tableau de bord analytique permet de suivre l'utilisation de la plateforme : visites et telechargements. Les donnees sont collectees de maniere automatique et transparente, sans impact sur les performances.

### Acces

- URL : `/admin/analytics`

### Tableau de bord

#### Selection de periode

Trois periodes sont disponibles :

- 7 derniers jours
- 30 derniers jours
- 12 derniers mois

#### Suivi des visites

- Nombre total de visites par type de page
- Tendance des visites (14 derniers jours, graphique en barres)
- Tracking automatique et silencieux (pas d'impact sur les performances)
- Filtrage des bots par User-Agent

#### Suivi des telechargements

- Nombre total de telechargements sur la periode selectionnee
- Repartition par format de fichier (PDF, Excel, Word)

### Retention des donnees

- Duree de conservation maximale : 12 mois
- Le tableau de bord affiche une alerte si des enregistrements de plus de 12 mois sont detectes
- **Purge manuelle** (reserve aux administrateurs) :
  1. L'alerte apparait automatiquement dans le tableau de bord
  2. Cliquer sur le bouton "Purger"
  3. Confirmer l'operation dans la modale de confirmation (operation **irreversible**)
  4. Les enregistrements anciens sont supprimes de la base de donnees
  5. Le compteur est mis a jour immediatement

### Statistiques du tableau de bord principal

Le tableau de bord principal (`/admin`) affiche en permanence un recapitulatif de l'etat de la plateforme :

- Nombre de comptes (total, publies, brouillons)
- Nombre de collectivites (provinces, regions, communes)
- Nombre d'utilisateurs enregistres
- Nombre total de telechargements
