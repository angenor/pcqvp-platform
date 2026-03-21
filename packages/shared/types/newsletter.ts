export interface SubscribeRequest {
  email: string
}

export interface SubscribeResponse {
  message: string
}

export interface SubscriberResponse {
  id: string
  email: string
  status: 'en_attente' | 'actif' | 'desinscrit'
  confirmed_at: string | null
  unsubscribed_at: string | null
  created_at: string
}

export interface PaginatedSubscribers {
  items: SubscriberResponse[]
  total: number
  page: number
  per_page: number
}
