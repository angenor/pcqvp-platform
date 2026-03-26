# Research: Back-Office Design Upgrade

**Feature**: 012-backoffice-design-upgrade | **Date**: 2026-03-22

## R1: Stratégie de chargement des polices

**Decision**: Google Fonts via `<link>` dans `nuxt.config.ts` (app.head)

**Rationale**: Google Fonts est la solution la plus simple et la plus performante pour charger Barlow Condensed, Inter et JetBrains Mono. Le CDN Google offre un cache partagé entre sites, des formats optimisés (woff2), et un chargement conditionnel. Nuxt permet de déclarer les liens dans `app.head` de `nuxt.config.ts`.

**Alternatives considered**:
- Auto-hébergement (@fontsource) : plus de contrôle mais setup plus complexe, pas de cache CDN partagé
- @nuxtjs/google-fonts module : abstraction supplémentaire non nécessaire pour 3 polices statiques

**Poids des polices sélectionnées** :
- Barlow Condensed : 400, 600, 700 (titres)
- Inter : 400, 500, 600 (corps de texte)
- JetBrains Mono : 400, 500 (données numériques)

---

## R2: Intégration FontAwesome dans Nuxt 4

**Decision**: Plugin Nuxt avec import explicite des icônes utilisées

**Rationale**: L'ancienne plateforme utilise cette approche avec succès (152+ icônes). L'import explicite évite le tree-shaking problématique et contrôle la taille du bundle. Le plugin enregistre `FontAwesomeIcon` comme composant global.

**Packages requis** :
- `@fortawesome/fontawesome-svg-core` (core)
- `@fortawesome/free-solid-svg-icons` (icônes solides)
- `@fortawesome/free-regular-svg-icons` (icônes outline)
- `@fortawesome/vue-fontawesome` (composant Vue)

**Alternatives considered**:
- Heroicons : moins d'icônes, pas de cohérence avec l'ancienne plateforme
- Lucide Icons : bon choix mais l'utilisateur veut explicitement le même design
- Nuxt Icon module : abstraction supplémentaire, moins de contrôle

---

## R3: Design system CSS — variables vs Tailwind extend

**Decision**: Variables CSS custom dans `main.css` avec utilisation via `var()` dans les classes Tailwind

**Rationale**: L'ancienne plateforme utilise cette approche avec succès. Les variables CSS permettent :
- Basculement mode clair/sombre en changeant les valeurs des variables (pas les classes)
- Centralisation des tokens de design (une seule source de vérité)
- Compatibilité avec Tailwind CSS 4 (config CSS-native)
- Réutilisation dans les composants via `bg-[var(--bg-card)]`, `text-[var(--text-primary)]`, etc.

**Alternatives considered**:
- Tailwind theme extend : nécessite un fichier de config JS séparé, moins flexible pour le mode sombre
- CSS-in-JS : pas adapté à l'écosystème Vue/Nuxt

---

## R4: Composants UI — préfixe et organisation

**Decision**: Préfixe `Ui` dans `components/ui/` (ex: `UiButton.vue`, `UiDataTable.vue`)

**Rationale**: Nuxt auto-importe les composants par nom de fichier. Le préfixe `Ui` :
- Évite les conflits avec les composants HTML natifs (`<button>` vs `<UiButton>`)
- Permet un regroupement visuel clair dans l'IDE
- Est cohérent avec les conventions Nuxt (auto-import par chemin)
- `<UiButton>` est plus explicite que `<Button>` dans les templates

**Alternatives considered**:
- Préfixe `Base` : convention alternative mais `Ui` est plus descriptif
- Pas de préfixe avec dossier : conflits potentiels avec les éléments natifs
- Nuxt UI module : trop opinionated, conflit potentiel avec le design system custom

---

## R5: Persistance état sidebar

**Decision**: Composable `useSidebar()` avec `localStorage`

**Rationale**: Solution simple et standard. Le composable expose un état réactif (`isCollapsed`) et le persiste dans `localStorage` sous une clé dédiée. Au chargement, la valeur sauvegardée est restaurée. Sur mobile/tablette, le comportement responsive prend le dessus (overlay mobile, replié tablette).

**Alternatives considered**:
- Cookie (via useCookie) : SSR-compatible mais inutile pour un état UI purement client
- Pinia store : over-engineering pour un seul booléen
- State dans le layout : pas réutilisable et pas persistant

---

## R6: Stratégie de migration des pages existantes

**Decision**: Migration complète en une seule feature branch — toutes les 19 pages admin + 9 composants existants

**Rationale**: L'utilisateur a explicitement choisi la migration complète (clarification Q3). Avantages :
- Cohérence visuelle immédiate (pas de "deux vitesses")
- Un seul passage de revue/test
- Les composants UI sont créés une fois puis réutilisés partout

**Ordre de migration** :
1. Design system (main.css) + polices + FontAwesome
2. Composants UI (ui/)
3. Layout admin (sidebar + header)
4. Pages admin (par groupes : dashboard, géographie, comptes, templates, outils)
5. Composants existants (adaptation au design system)

**Alternatives considered**:
- Migration progressive (page par page) : rejetée par l'utilisateur
- Layout seul + design system : ne couvre pas les composants des pages

---

## R7: Pages admin inventoriées pour migration

**Decision**: 19 pages identifiées, groupées par domaine

| Groupe | Pages | Fichiers |
|--------|-------|----------|
| Dashboard | 1 | `admin/index.vue` |
| Login | 1 | `admin/login.vue` |
| Géographie | 6 | `provinces/index.vue`, `provinces/[id].vue`, `regions/index.vue`, `regions/[id].vue`, `communes/index.vue`, `communes/[id].vue` |
| Comptes | 5 | `accounts/index.vue`, `accounts/new.vue`, `accounts/[id]/recettes.vue`, `accounts/[id]/depenses.vue`, `accounts/[id]/recap.vue` |
| Templates | 2 | `templates/index.vue`, `templates/[id].vue` |
| Outils | 4 | `users/index.vue`, `newsletter.vue`, `analytics.vue`, `config.vue` |

**Composants existants** : AccountDataTable, RecapTable, EquilibreTable, GeographySelector, SearchBar, NewsletterForm, AccountTable, RichContentEditor, RichContentRenderer
