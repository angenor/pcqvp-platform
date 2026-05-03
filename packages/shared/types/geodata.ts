export type GeodataWarningCode =
  | 'FEATURE_COUNT_OUT_OF_RANGE'
  | 'REGION_NOT_IN_DATABASE'
  | 'DUPLICATE_NAME_DROPPED'
  | 'FEATURE_TOO_SMALL_DROPPED'
  | 'GEOMETRY_FIXED'

export interface GeodataWarning {
  code: GeodataWarningCode
  message: string
  details?: Record<string, unknown>
}

export interface GeodataVersionAuthor {
  id: string
  email: string
}

export interface GeodataVersionListItem {
  id: string
  created_at: string
  created_by: GeodataVersionAuthor
  original_filename: string
  original_size_bytes: number
  processed_size_bytes: number
  features_count: number
  is_active: boolean
  has_warnings: boolean
  notes: string | null
}

export interface GeodataVersionDetail extends GeodataVersionListItem {
  region_names: string[]
  warnings: GeodataWarning[]
  geojson_processed: Record<string, unknown>
}

export interface GeodataVersionList {
  items: GeodataVersionListItem[]
  total: number
}

export interface GeodataUploadResponse {
  version_id: string
  uploaded_at: string
  original_filename: string
  original_size_bytes: number
  processed_size_bytes: number
  features_count: number
  region_names: string[]
  warnings: GeodataWarning[]
  is_active: false
  notes: string | null
}

export interface GeodataJobAccepted {
  job_id: string
  status: 'pending' | 'running'
  submitted_at: string
}

export type GeodataJobStatusValue = 'pending' | 'running' | 'done' | 'failed'

export interface GeodataJobStatus {
  job_id: string
  status: GeodataJobStatusValue
  submitted_at: string
  started_at: string | null
  completed_at: string | null
  version_id: string | null
  error_message: string | null
}
