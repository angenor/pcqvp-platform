export interface SiteConfigResponse {
  key: string
  value: string
  updated_at: string | null
}

export interface SiteConfigUpdateRequest {
  value: string
}

export interface GlobalLeaksPublicResponse {
  url: string
}
