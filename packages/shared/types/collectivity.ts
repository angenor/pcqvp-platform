export type CollectivityParentType = 'province' | 'region' | 'commune'

export interface CollectivityDocument {
  id: string
  parent_type: CollectivityParentType
  parent_id: string
  title: string
  file_path: string
  file_mime: string
  file_size_bytes: number
  position: number
  download_url: string
  created_at: string
  updated_at: string
}

export interface CollectivityDocumentCreate {
  parent_type: CollectivityParentType
  parent_id: string
  title: string
  file_path: string
  file_mime: string
  file_size_bytes: number
}

export interface CollectivityDocumentUpdate {
  title: string
}

export interface CollectivityDocumentFileReplace {
  file_path: string
  file_mime: string
  file_size_bytes: number
}

export interface CollectivityDocumentsReorder {
  parent_type: CollectivityParentType
  parent_id: string
  ordered_ids: string[]
}

export interface CollectivityDocumentUploadResponse {
  success: number
  file?: {
    url: string
    name: string
    size: number
    mime: string
  }
  detail?: string
}
