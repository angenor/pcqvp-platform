export interface EditorJSBlock {
  id?: string
  type: 'header' | 'paragraph' | 'image' | 'table' | 'list'
  data: Record<string, any>
}

export interface EditorJSData {
  time?: number
  blocks: EditorJSBlock[]
  version?: string
}

export interface ProvinceListItem {
  id: string
  name: string
  code: string
  created_at: string
}

export interface ProvinceDetail extends ProvinceListItem {
  description_json: EditorJSData | null
  regions: RegionListItem[]
  updated_at: string | null
}

export interface RegionListItem {
  id: string
  name: string
  code: string
  province_id: string
  created_at: string
}

export interface RegionDetail extends RegionListItem {
  description_json: EditorJSData | null
  communes: CommuneListItem[]
  updated_at: string | null
}

export interface CommuneListItem {
  id: string
  name: string
  code: string
  region_id: string
  created_at: string
}

export interface CommuneDetail extends CommuneListItem {
  description_json: EditorJSData | null
  updated_at: string | null
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
}

export interface HierarchyProvince {
  id: string
  name: string
  code: string
  regions: HierarchyRegion[]
}

export interface HierarchyRegion {
  id: string
  name: string
  code: string
  communes: HierarchyCommuneItem[]
}

export interface HierarchyCommuneItem {
  id: string
  name: string
  code: string
}
