import type { SubscribeResponse, PaginatedSubscribers } from '~~/types/newsletter'

export function useNewsletter() {
  const { apiFetch } = useApi()

  const loading = ref(false)
  const error = ref<string | null>(null)
  const success = ref(false)

  async function subscribe(email: string) {
    loading.value = true
    error.value = null
    success.value = false

    try {
      await apiFetch<SubscribeResponse>('/api/newsletter/subscribe', {
        method: 'POST',
        body: { email },
      })
      success.value = true
    } catch (e: any) {
      error.value = e?.data?.detail || "Erreur lors de l'inscription"
    } finally {
      loading.value = false
    }
  }

  function reset() {
    error.value = null
    success.value = false
  }

  return {
    loading,
    error,
    success,
    subscribe,
    reset,
  }
}

export function useAdminNewsletter() {
  const { apiFetch } = useApi()

  const subscribers = ref<PaginatedSubscribers | null>(null)
  const loading = ref(false)

  async function listSubscribers(params: {
    page?: number
    per_page?: number
    status?: string
    search?: string
  } = {}) {
    loading.value = true
    try {
      const query = new URLSearchParams()
      if (params.page) query.set('page', String(params.page))
      if (params.per_page) query.set('per_page', String(params.per_page))
      if (params.status) query.set('status', params.status)
      if (params.search) query.set('search', params.search)

      subscribers.value = await apiFetch<PaginatedSubscribers>(
        `/api/admin/newsletter/subscribers?${query.toString()}`
      )
    } finally {
      loading.value = false
    }
  }

  async function exportCsv() {
    const blob = await apiFetch<Blob>('/api/admin/newsletter/export', {
      responseType: 'blob',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `abonnes_newsletter_${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  async function deleteSubscriber(id: string) {
    await apiFetch(`/api/admin/newsletter/subscribers/${id}`, {
      method: 'DELETE',
    })
  }

  return {
    subscribers,
    loading,
    listSubscribers,
    exportCsv,
    deleteSubscriber,
  }
}
