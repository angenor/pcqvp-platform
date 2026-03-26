export interface TrendItem {
  date: string
  count: number
}

export interface VisitStats {
  total: number
  by_page_type: Record<string, number>
  trend: TrendItem[]
}

export interface DownloadStats {
  total: number
  by_format: Record<string, number>
  trend: TrendItem[]
}

export interface DataRetentionInfo {
  oldest_record: string | null
  purge_eligible_count: number
  purge_eligible: boolean
}

export interface DashboardResponse {
  period: string
  visits: VisitStats
  downloads: DownloadStats
  data_retention: DataRetentionInfo
}

export interface PurgeResponse {
  purged_count: number
  message: string
}
