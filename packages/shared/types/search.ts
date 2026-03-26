export interface SearchResultItem {
  id: string
  name: string
  type: 'province' | 'region' | 'commune'
  parent_name: string | null
  url: string
}

export interface SearchCompteItem {
  id: string
  collectivite_name: string
  collectivite_type: string
  annee_exercice: number
  url: string
}

export interface SearchResponse {
  results: {
    collectivites: SearchResultItem[]
    comptes: SearchCompteItem[]
  }
  total: number
}
