import type { DashboardResponse, PurgeResponse } from '~~/types/analytics'

export function useAnalytics() {
  const { apiFetch } = useApi()

  const dashboard = ref<DashboardResponse | null>(null)
  const loading = ref(false)

  async function loadDashboard(period: string = '30d') {
    loading.value = true
    try {
      dashboard.value = await apiFetch<DashboardResponse>(
        `/api/admin/analytics/dashboard?period=${period}`
      )
    } finally {
      loading.value = false
    }
  }

  async function purge(): Promise<PurgeResponse> {
    return await apiFetch<PurgeResponse>('/api/admin/analytics/purge', {
      method: 'DELETE',
    })
  }

  return {
    dashboard,
    loading,
    loadDashboard,
    purge,
  }
}
