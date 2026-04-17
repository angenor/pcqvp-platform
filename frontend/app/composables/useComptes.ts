import type {
  CompteDetail,
  CompteListResponse,
  RecetteLineResponse,
  RecetteLineUpsert,
  DepenseLineResponse,
  DepenseLineUpsert,
  DepenseProgramResponse,
  StatusUpdate,
  RecapRecettesResponse,
  RecapDepensesResponse,
  EquilibreResponse,
  ChangeLogResponse,
} from '~/types/comptes'

export function useComptes() {
  const { apiFetch } = useApi()

  function createCompte(data: { collectivite_type: string; collectivite_id: string; annee_exercice: number }) {
    return apiFetch<CompteDetail>('/api/admin/comptes', {
      method: 'POST',
      body: data,
    })
  }

  function fetchComptes(filters?: { collectivite_type?: string; collectivite_id?: string; annee?: number }) {
    const params = new URLSearchParams()
    if (filters?.collectivite_type) params.set('collectivite_type', filters.collectivite_type)
    if (filters?.collectivite_id) params.set('collectivite_id', filters.collectivite_id)
    if (filters?.annee) params.set('annee', String(filters.annee))
    const qs = params.toString()
    return apiFetch<CompteListResponse>(`/api/admin/comptes${qs ? '?' + qs : ''}`)
  }

  function fetchCompte(id: string) {
    return apiFetch<CompteDetail>(`/api/admin/comptes/${id}`)
  }

  function updateCompte(id: string, data: { collectivite_type?: string; collectivite_id?: string; annee_exercice?: number }) {
    return apiFetch<CompteDetail>(`/api/admin/comptes/${id}`, {
      method: 'PUT',
      body: data,
    })
  }

  function upsertRecetteLine(compteId: string, data: RecetteLineUpsert) {
    return apiFetch<RecetteLineResponse>(`/api/admin/comptes/${compteId}/recettes`, {
      method: 'PUT',
      body: data,
    })
  }

  function createProgramme(compteId: string, data: { intitule: string }) {
    return apiFetch<DepenseProgramResponse>(`/api/admin/comptes/${compteId}/programmes`, {
      method: 'POST',
      body: data,
    })
  }

  function updateProgramme(compteId: string, progId: string, data: { intitule: string }) {
    return apiFetch<DepenseProgramResponse>(`/api/admin/comptes/${compteId}/programmes/${progId}`, {
      method: 'PUT',
      body: data,
    })
  }

  function deleteProgramme(compteId: string, progId: string) {
    return apiFetch<void>(`/api/admin/comptes/${compteId}/programmes/${progId}`, {
      method: 'DELETE',
    })
  }

  function upsertDepenseLine(compteId: string, progId: string, data: DepenseLineUpsert) {
    return apiFetch<DepenseLineResponse>(`/api/admin/comptes/${compteId}/programmes/${progId}/depenses`, {
      method: 'PUT',
      body: data,
    })
  }

  function updateStatus(compteId: string, data: StatusUpdate) {
    return apiFetch<{ id: string; status: string; updated_at: string | null }>(`/api/admin/comptes/${compteId}/status`, {
      method: 'PUT',
      body: data,
    })
  }

  function deleteCompte(compteId: string) {
    return apiFetch<void>(`/api/admin/comptes/${compteId}`, {
      method: 'DELETE',
    })
  }

  function fetchRecapRecettes(id: string) {
    return apiFetch<RecapRecettesResponse>(`/api/admin/comptes/${id}/recapitulatifs/recettes`)
  }

  function fetchRecapDepenses(id: string) {
    return apiFetch<RecapDepensesResponse>(`/api/admin/comptes/${id}/recapitulatifs/depenses`)
  }

  function fetchEquilibre(id: string) {
    return apiFetch<EquilibreResponse>(`/api/admin/comptes/${id}/recapitulatifs/equilibre`)
  }

  function fetchChangelog(id: string) {
    return apiFetch<ChangeLogResponse>(`/api/admin/comptes/${id}/changelog`)
  }

  return {
    createCompte,
    fetchComptes,
    fetchCompte,
    updateCompte,
    upsertRecetteLine,
    createProgramme,
    updateProgramme,
    deleteProgramme,
    upsertDepenseLine,
    updateStatus,
    deleteCompte,
    fetchRecapRecettes,
    fetchRecapDepenses,
    fetchEquilibre,
    fetchChangelog,
  }
}
