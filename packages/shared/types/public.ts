import type { CollectivityDocument } from './collectivity'
import type { CollectiviteType, CompteStatus } from './comptes'

export interface PublicAnneesResponse {
  annees: number[]
}

export interface PublicDescriptionResponse {
  name: string
  type: CollectiviteType
  description_json: { type: string; content?: string; url?: string; alt?: string }[]
  banner_image: string | null
  documents: CollectivityDocument[]
}

export interface PublicTemplateColumn {
  code: string
  name: string
  is_computed: boolean
}

export interface PublicLineData {
  template_line_id: string
  compte_code: string
  intitule: string
  level: number
  section: string
  values: Record<string, number>
  computed: Record<string, number | null>
  children: PublicLineData[]
}

export interface PublicSection {
  section: string
  lines: PublicLineData[]
}

export interface PublicCompteInfo {
  id: string
  collectivite_type: CollectiviteType
  collectivite_id: string
  collectivite_name: string
  annee_exercice: number
  status: CompteStatus
}

export interface PublicProgramme {
  id: string
  numero: number
  intitule: string
  sections: PublicSection[]
}

export interface PublicRecapRecetteCategory {
  compte_code: string
  intitule: string
  previsions_definitives: number
  or_admis: number
  recouvrement: number
  reste_a_recouvrer: number
}

export interface PublicRecapRecetteSection {
  section: string
  categories: PublicRecapRecetteCategory[]
  total_reelles: Record<string, number>
  total_ordre: Record<string, number>
  total_section: Record<string, number>
}

export interface PublicRecapDepenseProgramme {
  programme_id: string
  numero: number
  mandat_admis: number
  paiement: number
  reste_a_payer: number
}

export interface PublicRecapDepenseCategory {
  compte_code: string
  intitule: string
  programmes: PublicRecapDepenseProgramme[]
  total: { mandat_admis: number; paiement: number; reste_a_payer: number }
}

export interface PublicRecapDepenseSection {
  section: string
  categories: PublicRecapDepenseCategory[]
  total_section: { mandat_admis: number; paiement: number; reste_a_payer: number }
}

export interface PublicEquilibreSide {
  reelles: { compte_code: string; intitule: string; montant: number }[]
  total_reelles: number
  ordre: { compte_code: string; intitule: string; montant: number }[]
  total_ordre: number
  total: number
}

export interface PublicEquilibreSection {
  depenses: PublicEquilibreSide
  recettes: PublicEquilibreSide
  excedent: number
}

export interface PublicParentDocument {
  type: CollectiviteType
  id: string
  name: string
  annees: number[]
  documents: CollectivityDocument[]
}

export interface PublicDocumentsLiesResponse {
  parents: PublicParentDocument[]
}

export interface PublicCompteResponse {
  compte: PublicCompteInfo
  recettes: {
    template_columns: PublicTemplateColumn[]
    sections: PublicSection[]
  }
  depenses: {
    template_columns: PublicTemplateColumn[]
    programmes: PublicProgramme[]
  }
  recapitulatifs: {
    recettes: { sections: PublicRecapRecetteSection[] }
    depenses: { sections: PublicRecapDepenseSection[]; programmes: { id: string; numero: number; intitule: string }[] }
  }
  equilibre: {
    fonctionnement: PublicEquilibreSection
    investissement: PublicEquilibreSection
    resultat_definitif: number
  }
}
