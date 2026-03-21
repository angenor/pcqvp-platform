import type { SearchResponse } from '~~/types/search'

export function useSearch() {
  const { apiFetch } = useApi()

  const results = ref<SearchResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  let debounceTimer: ReturnType<typeof setTimeout> | null = null

  async function search(query: string, limit: number = 10) {
    if (query.length < 2) {
      results.value = null
      return
    }

    loading.value = true
    error.value = null

    try {
      results.value = await apiFetch<SearchResponse>(
        `/api/search?q=${encodeURIComponent(query)}&limit=${limit}`
      )
    } catch (e: any) {
      error.value = e?.data?.detail || 'Erreur lors de la recherche'
      results.value = null
    } finally {
      loading.value = false
    }
  }

  function debouncedSearch(query: string, limit: number = 10, delay: number = 300) {
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => search(query, limit), delay)
  }

  function clear() {
    results.value = null
    error.value = null
    if (debounceTimer) clearTimeout(debounceTimer)
  }

  return {
    results,
    loading,
    error,
    search,
    debouncedSearch,
    clear,
  }
}
