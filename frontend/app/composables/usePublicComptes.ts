import type {
  PublicAnneesResponse,
  PublicDescriptionResponse,
  PublicCompteResponse,
  PublicDocumentsLiesResponse,
} from '../../../../packages/shared/types/public'

export function usePublicComptes() {
  const { apiFetch } = useApi()

  async function fetchAnnees(type: string, id: string): Promise<number[]> {
    const data = await apiFetch<PublicAnneesResponse>(
      `/api/public/collectivites/${type}/${id}/annees`
    )
    return data.annees
  }

  async function fetchDescription(type: string, id: string): Promise<PublicDescriptionResponse> {
    return await apiFetch<PublicDescriptionResponse>(
      `/api/public/collectivites/${type}/${id}/description`
    )
  }

  async function fetchCompte(type: string, id: string, annee: number): Promise<PublicCompteResponse> {
    return await apiFetch<PublicCompteResponse>(
      `/api/public/collectivites/${type}/${id}/comptes?annee=${annee}`
    )
  }

  async function fetchDocumentsLies(type: string, id: string): Promise<PublicDocumentsLiesResponse> {
    return await apiFetch<PublicDocumentsLiesResponse>(
      `/api/public/collectivites/${type}/${id}/documents-lies`
    )
  }

  async function downloadExport(type: string, id: string, annee: number, format: 'xlsx' | 'docx'): Promise<{ success: boolean }> {
    try {
      const response = await $fetch.raw(
        `/api/public/collectivites/${type}/${id}/comptes/${annee}/export?format=${format}`,
        { responseType: 'blob' }
      )

      const blob = response._data as Blob
      let filename = `compte_${type}_${annee}.${format}`

      const contentDisposition = response.headers.get('content-disposition')
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="(.+?)"/)
        if (match?.[1]) {
          filename = match[1]
        }
      }

      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.click()
      URL.revokeObjectURL(url)

      return { success: true }
    } catch {
      return { success: false }
    }
  }

  return { fetchAnnees, fetchDescription, fetchCompte, fetchDocumentsLies, downloadExport }
}
