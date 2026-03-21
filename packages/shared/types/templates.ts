export type TemplateType = 'recette' | 'depense'
export type SectionType = 'fonctionnement' | 'investissement'
export type ColumnDataType = 'number' | 'text' | 'percentage'

export interface TemplateListItem {
  id: string
  name: string
  type: TemplateType
  version: number
  is_active: boolean
  lines_count: number
  columns_count: number
  created_at: string
}

export interface TemplateDetail {
  id: string
  name: string
  type: TemplateType
  version: number
  is_active: boolean
  created_at: string
  updated_at: string | null
  lines: TemplateLine[]
  columns: TemplateColumn[]
}

export interface TemplateLine {
  id: string
  compte_code: string
  intitule: string
  level: number
  parent_code: string | null
  section: SectionType
  sort_order: number
}

export interface TemplateColumn {
  id: string
  name: string
  code: string
  data_type: ColumnDataType
  is_computed: boolean
  formula: string | null
  sort_order: number
}

export interface TemplateListResponse {
  items: TemplateListItem[]
  total: number
}
