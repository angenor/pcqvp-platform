import type { UserProfile, TokenResponse } from '~/types/auth'

export function useAuth() {
  const user = useState<UserProfile | null>('auth_user', () => null)
  const accessToken = useState<string | null>('access_token', () => null)
  const isAuthenticated = computed(() => !!user.value)

  async function login(email: string, password: string): Promise<void> {
    const data = await $fetch<TokenResponse>('/api/auth/login', {
      method: 'POST',
      body: { email, password },
      credentials: 'include',
    })

    accessToken.value = data.access_token
    await fetchUser()
  }

  async function fetchUser(): Promise<void> {
    try {
      const data = await $fetch<UserProfile>('/api/auth/me', {
        headers: {
          Authorization: `Bearer ${accessToken.value}`,
        },
      })
      user.value = data
    } catch {
      user.value = null
      accessToken.value = null
    }
  }

  async function refreshToken(): Promise<boolean> {
    try {
      const data = await $fetch<TokenResponse>('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include',
      })
      accessToken.value = data.access_token
      return true
    } catch {
      return false
    }
  }

  function logout(): void {
    user.value = null
    accessToken.value = null
    navigateTo('/admin/login')
  }

  return {
    user,
    accessToken,
    isAuthenticated,
    login,
    fetchUser,
    refreshToken,
    logout,
  }
}
