export type CollectiviteType = 'province' | 'region' | 'commune'
export type CompteStatus = 'draft' | 'published'

export interface CompteAdministratif {
  id: string
  collectivite_type: CollectiviteType
  collectivite_id: string
  collectivite_name: string
  annee_exercice: number
  status: CompteStatus
  created_by: string
  programmes: DepenseProgramResponse[]
  created_at: string
  updated_at: string | null
}

export interface CompteListItem {
  id: string
  collectivite_type: CollectiviteType
  collectivite_id: string
  collectivite_name: string
  annee_exercice: number
  status: CompteStatus
  created_by: string
  created_at: string
  updated_at: string | null
}

export interface CompteListResponse {
  items: CompteListItem[]
  total: number
}

export interface RecetteLineValues {
  budget_primitif?: number
  budget_additionnel?: number
  modifications?: number
  or_admis?: number
  recouvrement?: number
}

export interface RecetteLineComputed {
  previsions_definitives: number
  reste_a_recouvrer: number
  taux_execution: number | null
}

export interface RecetteLineResponse {
  id: string
  template_line_id: string
  values: RecetteLineValues
  computed: RecetteLineComputed
}

export interface RecetteLineUpsert {
  template_line_id: string
  values: RecetteLineValues
}

export interface DepenseLineValues {
  budget_primitif?: number
  budget_additionnel?: number
  modifications?: number
  engagement?: number
  mandat_admis?: number
  paiement?: number
}

export interface DepenseLineComputed {
  previsions_definitives: number
  reste_a_payer: number
  taux_execution: number | null
}

export interface DepenseLineResponse {
  id: string
  template_line_id: string
  values: DepenseLineValues
  computed: DepenseLineComputed
}

export interface DepenseLineUpsert {
  template_line_id: string
  values: DepenseLineValues
}

export interface DepenseProgramResponse {
  id: string
  numero: number
  intitule: string
  created_at: string
  updated_at?: string | null
}

export interface CompteDetail extends CompteAdministratif {
  recettes: {
    lines: (RecetteLineResponse & {
      compte_code: string
      intitule: string
      level: number
      parent_code: string | null
      section: string
      sort_order: number
    })[]
    hierarchical_sums: Record<string, Record<string, number>>
  }
}

export interface RecapCategory {
  compte_code: string
  intitule: string
  previsions_definitives: number
  or_admis: number
  recouvrement: number
  reste_a_recouvrer: number
}

export interface RecapSectionTotals {
  previsions_definitives: number
  or_admis: number
  recouvrement: number
  reste_a_recouvrer: number
}

export interface RecapRecettesSection {
  section: string
  categories: RecapCategory[]
  total_reelles: RecapSectionTotals
  total_ordre: RecapSectionTotals
  total_section: RecapSectionTotals
}

export interface RecapRecettesResponse {
  sections: RecapRecettesSection[]
}

export interface RecapDepenseProgramme {
  programme_id: string
  numero: number
  mandat_admis: number
  paiement: number
  reste_a_payer: number
}

export interface RecapDepenseCategory {
  compte_code: string
  intitule: string
  programmes: RecapDepenseProgramme[]
  total: { mandat_admis: number; paiement: number; reste_a_payer: number }
}

export interface RecapDepensesSection {
  section: string
  categories: RecapDepenseCategory[]
  total_section: { mandat_admis: number; paiement: number; reste_a_payer: number }
}

export interface RecapDepensesResponse {
  sections: RecapDepensesSection[]
  programmes: DepenseProgramResponse[]
}

export interface EquilibreSide {
  reelles: { compte_code: string; intitule: string; montant: number }[]
  total_reelles: number
  ordre: { compte_code: string; intitule: string; montant: number }[]
  total_ordre: number
  total: number
}

export interface EquilibreSection {
  depenses: EquilibreSide
  recettes: EquilibreSide
  excedent: number
}

export interface EquilibreResponse {
  fonctionnement: EquilibreSection
  investissement: EquilibreSection
  resultat_definitif: number
}

export interface ChangeLogEntry {
  id: string
  user_email: string
  change_type: string
  detail: Record<string, unknown>
  created_at: string
}

export interface ChangeLogResponse {
  items: ChangeLogEntry[]
  total: number
}

export interface StatusUpdate {
  status: CompteStatus
}
