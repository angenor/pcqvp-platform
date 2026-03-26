export default defineNuxtRouteMiddleware(async (to) => {
  if (!to.path.startsWith('/admin') || to.path === '/admin/login') {
    return
  }

  const { isAuthenticated, fetchUser, accessToken, refreshToken } = useAuth()

  if (!isAuthenticated.value && accessToken.value) {
    await fetchUser()
  }

  if (!isAuthenticated.value) {
    const refreshed = await refreshToken()
    if (refreshed) {
      await fetchUser()
    }
  }

  if (!isAuthenticated.value) {
    return navigateTo('/admin/login')
  }
})
