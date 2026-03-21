import type { SiteConfigResponse, GlobalLeaksPublicResponse } from '~~/types/config'

export function useSiteConfig() {
  const { apiFetch } = useApi()

  async function getConfig(key: string): Promise<SiteConfigResponse> {
    return await apiFetch<SiteConfigResponse>(`/api/admin/config/${key}`)
  }

  async function updateConfig(key: string, value: string): Promise<SiteConfigResponse> {
    return await apiFetch<SiteConfigResponse>(`/api/admin/config/${key}`, {
      method: 'PUT',
      body: { value },
    })
  }

  async function getPublicGlobalLeaksUrl(): Promise<string> {
    const data = await apiFetch<GlobalLeaksPublicResponse>('/api/public/config/globalleaks')
    return data.url
  }

  return {
    getConfig,
    updateConfig,
    getPublicGlobalLeaksUrl,
  }
}
