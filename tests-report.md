# Rapport de tests - Plateforme PCQVP

**Date :** 2026-03-21
**Environnement :** Backend http://localhost:8000 | Frontend http://localhost:3000
**Outil :** agent-browser (mode headed)

---

## Tableau des resultats

| Feature | Test | Resultat | Detail |
|---------|------|----------|--------|
| **F1 - Fondations** | GET /health contient "ok" et "connected" | PASS | `{"status":"ok","db":"connected"}` |
| **F1 - Fondations** | /docs Swagger visible | PASS | Titre "PCQVP Platform - Swagger UI" |
| **F1 - Fondations** | http://localhost:3000 charge sans erreur | PASS | Titre "Plateforme de suivi des revenus miniers - PCQVP Madagascar" |
| **F2 - Auth** | /admin/login : champs email + mdp + bouton | PASS | textbox Email, textbox Mot de passe, button Se connecter |
| **F2 - Auth** | Login mauvais identifiants : message erreur | PASS | "Email ou mot de passe incorrect." affiche |
| **F2 - Auth** | Login admin : redirige vers /admin | PASS | Redirection vers http://localhost:3000/admin |
| **F2 - Auth** | /admin sans auth : redirige vers login | PASS | Redirection vers /admin/login (session separee) |
| **F3 - Geo** | /admin/geography/provinces : liste | PASS | Province "Antananarivo" (P01) visible dans le tableau |
| **F3 - Geo** | Creer "Province Test" | PASS | Province Test (PT1) apparait dans la liste |
| **F3 - Geo** | /admin/geography/regions : filtre province | PASS | Combobox avec options Antananarivo, Province Test |
| **F3 - Geo** | /admin/geography/communes : filtre region | PASS | Combobox avec option Analamanga |
| **F3 - Geo** | Page publique / : 3 selecteurs cascade | PASS | Province > Region > Commune + bouton OK |
| **F4 - Templates** | /admin/templates : au moins 2 templates | PASS | Depenses (267 lignes, 9 col) + Recettes (149 lignes, 8 col) |
| **F4 - Templates** | Template Recettes : hierarchie + colonnes | PASS | Comptes 70, 71, 72... avec colonnes Budget primitif, etc. |
| **F5 - Comptes** | /admin/accounts : Andrafiabe 2023 | FAIL | Aucun compte administratif en base (items: [], total: 0) |
| **F5 - Comptes** | Onglet Recettes : tableau editable | FAIL | Pas de comptes disponibles - donnees manquantes |
| **F5 - Comptes** | Onglet Recapitulatifs : totaux calcules | FAIL | Pas de comptes disponibles - donnees manquantes |
| **F5 - Comptes** | Onglet Equilibre : depenses/recettes | FAIL | Pas de comptes disponibles - donnees manquantes |
| **F6 - Front office** | Page / : titre, logo, selecteurs, OK | PASS | Titre, logo TI, 3 selecteurs, bouton OK presents |
| **F6 - Front office** | Selectionner commune > OK > onglets | FAIL | "Aucun compte publie" - pas de donnees en base |
| **F6 - Front office** | Cliquer compte N1 > sous-comptes | FAIL | Pas de comptes publies |
| **F6 - Front office** | Viewport mobile 375x812 : pas de debordement | PASS | scrollWidth <= clientWidth confirme |
| **F7 - Exports** | Telecharger Excel (status 200) | FAIL | Pas de comptes disponibles pour l'export |
| **F7 - Exports** | Telecharger Word (status 200) | FAIL | Pas de comptes disponibles pour l'export |
| **F8 - Admin** | /admin/users : liste utilisateurs | FAIL | Route /admin/users absente de l'API et du menu |
| **F8 - Admin** | /admin dashboard : statistiques | FAIL | Dashboard affiche uniquement "Bienvenue" sans statistiques |
| **F9 - Extras** | Newsletter test@example.com | PASS | "Un email de confirmation a ete envoye." |
| **F9 - Extras** | Rechercher "Ambohidratrimo" | PASS | Resultat "Ambohidratrimo commune - Analamanga" trouve |

---

## Resume

| | Total |
|---|---|
| **Tests passes** | 18 |
| **Tests echoues** | 10 |
| **Total** | 28 |
| **Taux de reussite** | 64% |

---

## Bugs et problemes identifies

### BUG 1 - Aucun compte administratif en base (critique)
- **Impact :** Features 5, 6 (partiellement), 7 entierement bloquees
- **Detail :** L'API `/api/admin/comptes` retourne `{"items": [], "total": 0}`. Aucun compte Andrafiabe 2023 n'existe. La commune Andrafiabe elle-meme n'est pas dans les donnees geographiques.
- **Screenshot :** `screenshots/f5_accounts_empty.png`
- **Action :** Executer un script de seed pour creer les comptes administratifs de demo (Andrafiabe 2023)

### BUG 2 - Gestion des utilisateurs absente
- **Impact :** Feature 8
- **Detail :** Pas de route `/admin/users` dans l'API OpenAPI. Pas de lien "Utilisateurs" dans le menu admin.
- **Screenshot :** `screenshots/f8_dashboard.png`
- **Action :** Implementer le CRUD utilisateurs admin

### BUG 3 - Dashboard admin sans statistiques
- **Impact :** Feature 8
- **Detail :** Le dashboard affiche uniquement "Bienvenue sur la plateforme PCQVP." sans aucune statistique (nombre de comptes, communes, etc.)
- **Screenshot :** `screenshots/f8_dashboard.png`
- **Action :** Ajouter des cartes de statistiques sur le dashboard (l'API `/api/admin/analytics/dashboard` existe)

### BUG 4 - Exports impossibles sans donnees
- **Impact :** Feature 7
- **Detail :** Pas de bouton d'export visible car aucun compte publie n'existe
- **Screenshot :** `screenshots/f7_no_export_data.png`
- **Action :** Depend de la resolution du BUG 1

### BUG 5 - Session auth perdue lors de navigation par URL
- **Impact :** Ergonomie des tests
- **Detail :** La commande `agent-browser open` ou `eval window.location.href` depuis /admin/ perd la session JWT. Navigation uniquement possible via les liens du menu.
- **Severite :** Mineure (comportement lie au stockage JWT en memoire)

---

## Screenshots

| Fichier | Description |
|---------|-------------|
| `screenshots/f1_health.png` | Health check API |
| `screenshots/f1_swagger.png` | Swagger UI |
| `screenshots/f1_frontend.png` | Page d'accueil frontend |
| `screenshots/f2_login_form.png` | Formulaire de login |
| `screenshots/f2_login_error.png` | Erreur de login |
| `screenshots/f2_login_success.png` | Login reussi - dashboard |
| `screenshots/f2_no_auth_redirect.png` | Redirection sans auth |
| `screenshots/f3_provinces_list.png` | Liste des provinces |
| `screenshots/f3_province_created.png` | Province Test creee |
| `screenshots/f3_regions_filter.png` | Filtre regions par province |
| `screenshots/f3_communes_filter.png` | Filtre communes par region |
| `screenshots/f3_public_selectors.png` | Selecteurs cascade publics |
| `screenshots/f4_templates_list.png` | Liste des templates |
| `screenshots/f4_template_recettes.png` | Detail template Recettes |
| `screenshots/f5_accounts_empty.png` | Comptes admin - vide |
| `screenshots/f6_homepage.png` | Page d'accueil publique |
| `screenshots/f6_collectivite_no_data.png` | Page collectivite sans donnees |
| `screenshots/f6_mobile.png` | Vue mobile 375x812 |
| `screenshots/f7_no_export_data.png` | Export impossible |
| `screenshots/f8_dashboard.png` | Dashboard admin |
| `screenshots/f9_newsletter.png` | Inscription newsletter |
| `screenshots/f9_search.png` | Recherche fonctionnelle |
