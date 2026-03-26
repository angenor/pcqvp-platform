# Data Model: Back-Office Design Upgrade

**Feature**: 012-backoffice-design-upgrade | **Date**: 2026-03-22

> Cette feature ne modifie aucune table de base de données. Le "data model" ici décrit les composants UI et leurs interfaces (props/events).

## Design Tokens (CSS Variables)

### Palette de couleurs

| Token | Mode clair | Mode sombre | Usage |
|-------|------------|-------------|-------|
| `--color-primary` | #3695d8 | #3695d8 | Couleur primaire TI Madagascar |
| `--color-primary-50` à `--color-primary-950` | Échelle 10 teintes | Échelle 10 teintes | Variantes de la primaire |
| `--color-success` | #10b981 | #10b981 | Succès, publié |
| `--color-warning` | #f59e0b | #f59e0b | Avertissement, brouillon |
| `--color-error` | #ef4444 | #ef4444 | Erreur, suppression |
| `--color-info` | #3b82f6 | #3b82f6 | Information |
| `--bg-page` | #f9fafb | #030712 | Fond de page |
| `--bg-card` | #ffffff | #111827 | Fond de carte/conteneur |
| `--bg-sidebar` | #ffffff | #111827 | Fond de sidebar |
| `--bg-header` | #ffffff | #111827 | Fond de header |
| `--text-primary` | #111827 | #f9fafb | Texte principal |
| `--text-secondary` | #4b5563 | #d1d5db | Texte secondaire |
| `--text-muted` | #9ca3af | #6b7280 | Texte discret |
| `--border-default` | #e5e7eb | #374151 | Bordure par défaut |

### Typographie

| Token | Valeur | Usage |
|-------|--------|-------|
| `--font-heading` | 'Barlow Condensed', sans-serif | Titres (h1-h6) |
| `--font-body` | 'Inter', sans-serif | Corps de texte |
| `--font-mono` | 'JetBrains Mono', monospace | Données numériques |

### Espacements & Dimensions

| Token | Valeur | Usage |
|-------|--------|-------|
| `--sidebar-width` | 256px | Sidebar dépliée |
| `--sidebar-collapsed` | 64px | Sidebar repliée |
| `--header-height` | 56px | Hauteur header |
| `--radius-sm` | 6px | Petits éléments |
| `--radius-md` | 8px | Éléments moyens |
| `--radius-lg` | 12px | Cartes, modales |
| `--shadow-sm` | 0 1px 2px rgba(0,0,0,0.05) | Ombre subtile |
| `--shadow-md` | 0 4px 6px rgba(0,0,0,0.1) | Ombre moyenne |

### Z-Index

| Token | Valeur | Usage |
|-------|--------|-------|
| `--z-dropdown` | 1000 | Menus déroulants |
| `--z-sticky` | 1020 | Header, sidebar |
| `--z-modal-backdrop` | 1040 | Overlay modal |
| `--z-modal` | 1050 | Contenu modal |
| `--z-toast` | 1080 | Notifications toast |

---

## Composants UI — Interfaces

### UiButton

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'primary' \| 'secondary' \| 'outline' \| 'ghost' \| 'danger' \| 'success'` | `'primary'` | Variante visuelle |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Taille |
| `loading` | `boolean` | `false` | Affiche un spinner et désactive |
| `disabled` | `boolean` | `false` | État désactivé |
| `icon` | `string[]` | — | Icône FontAwesome (ex: `['fas', 'plus']`) |
| `iconPosition` | `'left' \| 'right'` | `'left'` | Position de l'icône |
| `to` | `string` | — | Si défini, rendu comme NuxtLink |
| `block` | `boolean` | `false` | Pleine largeur |

**Slots**: `default` (contenu texte)
**Events**: `click`

---

### UiBadge

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'primary' \| 'success' \| 'warning' \| 'error' \| 'info' \| 'gray'` | `'gray'` | Variante couleur |
| `size` | `'sm' \| 'md'` | `'sm'` | Taille |
| `dot` | `boolean` | `false` | Affiche un point indicateur |

**Slots**: `default` (texte du badge)

---

### UiStatCard

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | — | Libellé du KPI |
| `value` | `string \| number` | — | Valeur affichée |
| `icon` | `string[]` | — | Icône FontAwesome |
| `variant` | `'primary' \| 'success' \| 'warning' \| 'error' \| 'info'` | `'primary'` | Couleur de l'icône |
| `trend` | `number` | — | Pourcentage de tendance (+/-) |
| `trendLabel` | `string` | — | Libellé de la tendance |
| `loading` | `boolean` | `false` | État skeleton |
| `to` | `string` | — | Lien cliquable |

---

### UiDataTable

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `columns` | `Column[]` | — | Définition des colonnes |
| `data` | `any[]` | `[]` | Données à afficher |
| `loading` | `boolean` | `false` | Affiche skeleton loader |
| `searchable` | `boolean` | `true` | Active la barre de recherche |
| `searchPlaceholder` | `string` | `'Rechercher...'` | Placeholder recherche |
| `sortable` | `boolean` | `true` | Active le tri |
| `emptyIcon` | `string[]` | `['fas', 'inbox']` | Icône état vide |
| `emptyMessage` | `string` | `'Aucune donnée'` | Message état vide |
| `pagination` | `boolean` | `true` | Active la pagination |
| `pageSize` | `number` | `20` | Éléments par page |

**Type Column**: `{ key: string, label: string, sortable?: boolean, align?: 'left' \| 'center' \| 'right' }`
**Slots**: `cell-{key}` (rendu custom par colonne), `actions` (colonne d'actions), `toolbar` (actions en-tête), `empty-action` (bouton état vide)
**Events**: `search(query)`, `sort(key, direction)`, `page-change(page)`

---

### UiModal

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `modelValue` | `boolean` | `false` | Visibilité (v-model) |
| `title` | `string` | — | Titre de la modale |
| `description` | `string` | — | Description optionnelle |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Taille |
| `closable` | `boolean` | `true` | Fermeture par backdrop/X |
| `danger` | `boolean` | `false` | Style destructif (rouge) |

**Slots**: `default` (contenu), `footer` (boutons d'action)
**Events**: `update:modelValue`, `close`

---

### UiFormInput

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `modelValue` | `string \| number` | — | Valeur (v-model) |
| `type` | `'text' \| 'email' \| 'password' \| 'number' \| 'date'` | `'text'` | Type d'input |
| `label` | `string` | — | Libellé |
| `placeholder` | `string` | — | Placeholder |
| `required` | `boolean` | `false` | Champ obligatoire |
| `error` | `string` | — | Message d'erreur |
| `disabled` | `boolean` | `false` | Désactivé |
| `icon` | `string[]` | — | Icône préfixe |

**Events**: `update:modelValue`

---

### UiFormSelect

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `modelValue` | `string \| number` | — | Valeur sélectionnée (v-model) |
| `options` | `{ value: string \| number, label: string }[]` | `[]` | Options |
| `label` | `string` | — | Libellé |
| `placeholder` | `string` | — | Placeholder |
| `required` | `boolean` | `false` | Obligatoire |
| `error` | `string` | — | Message d'erreur |
| `disabled` | `boolean` | `false` | Désactivé |

**Events**: `update:modelValue`

---

### UiFormTextarea

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `modelValue` | `string` | — | Valeur (v-model) |
| `label` | `string` | — | Libellé |
| `rows` | `number` | `4` | Nombre de lignes |
| `required` | `boolean` | `false` | Obligatoire |
| `error` | `string` | — | Message d'erreur |
| `disabled` | `boolean` | `false` | Désactivé |

**Events**: `update:modelValue`

---

### UiAlert

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'success' \| 'warning' \| 'error' \| 'info'` | `'info'` | Type d'alerte |
| `dismissible` | `boolean` | `false` | Peut être fermée |
| `icon` | `string[]` | — | Icône custom (défaut selon variant) |

**Slots**: `default` (message)
**Events**: `dismiss`

---

### UiLoadingSpinner

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Taille du spinner |
| `color` | `string` | `'primary'` | Couleur |

---

### AdminSidebar

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `collapsed` | `boolean` | `false` | État replié |

**Events**: `toggle` (demande de basculement)

**Structure du menu** (hardcoded dans le composant) :
```
- Tableau de bord (fas:home)
- Géographie
  - Provinces (fas:map)
  - Régions (fas:map-marked)
  - Communes (fas:city)
- Comptes
  - Templates (fas:file-alt)
  - Comptes administratifs (fas:calculator)
- Outils
  - Utilisateurs (fas:users)
  - Newsletter (fas:envelope)
  - Analytics (fas:chart-bar)
  - Configuration (fas:cog)
```

---

### AdminHeader

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `sidebarCollapsed` | `boolean` | `false` | Pour ajuster le margin-left |

**Events**: `toggle-sidebar`

**Contenu** : Bouton hamburger (mobile), fil d'Ariane (auto via route), toggle mode sombre, email utilisateur, bouton déconnexion

---

### AdminBreadcrumb

Composant auto-générant le fil d'Ariane à partir de `useRoute()`. Aucune prop — se base sur les segments de l'URL pour générer les liens.
