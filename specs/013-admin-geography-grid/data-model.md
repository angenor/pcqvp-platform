# Data Model: Navigation Géographique Admin en Grille

**Feature**: 013-admin-geography-grid | **Date**: 2026-03-26

## Entités existantes (aucune modification backend)

Cette feature est purement frontend. Les entités backend restent inchangées.

### Province
| Champ | Type | Description |
|-------|------|-------------|
| id | UUID | Identifiant unique |
| name | string (255) | Nom de la province |
| code | string (20) | Code unique |
| created_at | datetime | Date de création |

### Region
| Champ | Type | Description |
|-------|------|-------------|
| id | UUID | Identifiant unique |
| name | string (255) | Nom de la région |
| code | string (20) | Code unique |
| province_id | UUID (FK) | Province parente |
| created_at | datetime | Date de création |

### Commune
| Champ | Type | Description |
|-------|------|-------------|
| id | UUID | Identifiant unique |
| name | string (255) | Nom de la commune |
| code | string (20) | Code unique |
| region_id | UUID (FK) | Région parente |
| created_at | datetime | Date de création |

### CompteAdministratif (référence — lien depuis les régions)
| Champ | Type | Description |
|-------|------|-------------|
| id | UUID | Identifiant unique |
| collectivite_type | enum | province / region / commune |
| collectivite_id | UUID | ID de la collectivité |
| annee_exercice | int | Année d'exercice |
| status | enum | draft / published |

## Nouveaux composants frontend

### GeographyCard (composant Vue)
| Prop | Type | Description |
|------|------|-------------|
| id | string | UUID de l'entité |
| name | string | Nom affiché |
| code | string | Code affiché |
| type | 'province' \| 'region' \| 'commune' | Type d'entité |
| clickRoute | string \| null | Route de navigation au clic |
| showFinancialLink | boolean | Afficher le lien "Voir les comptes" (régions uniquement) |
| onEdit | () => void | Callback édition depuis le menu ⋮ |
| onDelete | () => void | Callback suppression depuis le menu ⋮ |

### UiDropdownMenu (composant Vue)
| Prop | Type | Description |
|------|------|-------------|
| items | DropdownItem[] | Liste des actions |
| position | 'left' \| 'right' | Position du menu déroulant |

### DropdownItem (type)
| Champ | Type | Description |
|-------|------|-------------|
| label | string | Texte de l'action |
| icon | string[] | Icône FontAwesome |
| action | () => void | Callback |
| variant | 'default' \| 'danger' | Style (danger pour supprimer) |

## Relations et flux de données

```
Page Provinces (index.vue)
  └─ fetchProvinces() → ProvinceListItem[]
      └─ Clic carte → /admin/geography/provinces/:id/regions

Page Régions d'une Province ([id]/regions.vue)
  └─ fetchProvinceDetail(id) → ProvinceDetail (avec regions[])
      └─ Clic carte région → /admin/geography/regions/:id/communes
      └─ Voir les comptes → /admin/accounts?collectivite_type=region&collectivite_id=:id

Page Régions (index.vue)
  └─ fetchRegions(provinceId?) → RegionListItem[]
      └─ Filtre province → fetchRegions(selectedProvinceId)
      └─ Clic carte → /admin/geography/regions/:id/communes

Page Communes d'une Région ([id]/communes.vue)
  └─ fetchRegionDetail(id) → RegionDetail (avec communes[])

Page Communes (index.vue)
  └─ fetchCommunes(regionId?) → CommuneListItem[]
      └─ Filtre province → fetchRegions(provinceId)
      └─ Filtre région → fetchCommunes(selectedRegionId)
```
