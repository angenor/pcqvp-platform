export default defineNuxtPlugin(async () => {
  const { isAuthenticated, refreshToken, fetchUser } = useAuth()

  if (!isAuthenticated.value) {
    const refreshed = await refreshToken()
    if (refreshed) {
      await fetchUser()
    }
  }
})
