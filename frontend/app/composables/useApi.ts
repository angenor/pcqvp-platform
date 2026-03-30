export function useApi() {
  const getAuthHeaders = (): Record<string, string> => {
    const token = useCookie('access_token').value
    return token ? { Authorization: `Bearer ${token}` } : {}
  }

  async function apiFetch<T>(url: string, options: any = {}): Promise<T> {
    const headers = {
      ...getAuthHeaders(),
      ...(options.headers || {}),
    }

    try {
      return await $fetch<T>(url, {
        ...options,
        headers,
        credentials: 'include',
      })
    } catch (error: any) {
      if (error?.response?.status === 401 || error?.statusCode === 401) {
        const { refreshToken, logout } = useAuth()
        const refreshed = await refreshToken()
        if (refreshed) {
          const retryHeaders = {
            ...getAuthHeaders(),
            ...(options.headers || {}),
          }
          return await $fetch<T>(url, {
            ...options,
            headers: retryHeaders,
            credentials: 'include',
          })
        }
        logout()
      }
      throw error
    }
  }

  return { apiFetch }
}
