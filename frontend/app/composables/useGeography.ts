import type {
  ProvinceListItem,
  ProvinceDetail,
  RegionListItem,
  RegionDetail,
  CommuneListItem,
  CommuneDetail,
  PaginatedResponse,
  HierarchyProvince,
  EditorJSData,
} from '~/types/geography'

export function useGeography() {
  const { apiFetch } = useApi()

  // --- Public endpoints ---

  function fetchProvinces(options?: { hasComptes?: boolean }) {
    const params = options?.hasComptes ? '?has_comptes=true' : ''
    return apiFetch<ProvinceListItem[]>(`/api/provinces${params}`)
  }

  function fetchProvinceDetail(id: string) {
    return apiFetch<ProvinceDetail>(`/api/provinces/${id}`)
  }

  function fetchRegions(provinceId?: string, options?: { hasComptes?: boolean }) {
    const query = new URLSearchParams()
    if (provinceId) query.set('province_id', provinceId)
    if (options?.hasComptes) query.set('has_comptes', 'true')
    const qs = query.toString()
    return apiFetch<RegionListItem[]>(`/api/regions${qs ? '?' + qs : ''}`)
  }

  function fetchRegionDetail(id: string) {
    return apiFetch<RegionDetail>(`/api/regions/${id}`)
  }

  function fetchCommunes(regionId?: string, options?: { hasComptes?: boolean }) {
    const query = new URLSearchParams()
    if (regionId) query.set('region_id', regionId)
    if (options?.hasComptes) query.set('has_comptes', 'true')
    const qs = query.toString()
    return apiFetch<CommuneListItem[]>(`/api/communes${qs ? '?' + qs : ''}`)
  }

  function fetchCommuneDetail(id: string) {
    return apiFetch<CommuneDetail>(`/api/communes/${id}`)
  }

  function fetchHierarchy() {
    return apiFetch<HierarchyProvince[]>('/api/geography/hierarchy')
  }

  // --- IDs with comptes ---

  function fetchIdsWithComptes() {
    return apiFetch<{ province_ids: string[]; region_ids: string[]; commune_ids: string[] }>(
      '/api/admin/geography/ids-with-comptes',
    )
  }

  // --- Admin CRUD ---

  function createProvince(data: { name: string; code: string; description_json?: EditorJSData | null }) {
    return apiFetch<ProvinceDetail>('/api/admin/provinces', {
      method: 'POST',
      body: data,
    })
  }

  function updateProvince(id: string, data: { name: string; code: string; description_json?: EditorJSData | null }) {
    return apiFetch<ProvinceDetail>(`/api/admin/provinces/${id}`, {
      method: 'PUT',
      body: data,
    })
  }

  function deleteProvince(id: string) {
    return apiFetch<void>(`/api/admin/provinces/${id}`, { method: 'DELETE' })
  }

  function createRegion(data: { name: string; code: string; province_id: string; description_json?: EditorJSData | null }) {
    return apiFetch<RegionDetail>('/api/admin/regions', {
      method: 'POST',
      body: data,
    })
  }

  function updateRegion(id: string, data: { name: string; code: string; province_id: string; description_json?: EditorJSData | null }) {
    return apiFetch<RegionDetail>(`/api/admin/regions/${id}`, {
      method: 'PUT',
      body: data,
    })
  }

  function deleteRegion(id: string) {
    return apiFetch<void>(`/api/admin/regions/${id}`, { method: 'DELETE' })
  }

  function createCommune(data: { name: string; code: string; region_id: string; description_json?: EditorJSData | null }) {
    return apiFetch<CommuneDetail>('/api/admin/communes', {
      method: 'POST',
      body: data,
    })
  }

  function updateCommune(id: string, data: { name: string; code: string; region_id: string; description_json?: EditorJSData | null }) {
    return apiFetch<CommuneDetail>(`/api/admin/communes/${id}`, {
      method: 'PUT',
      body: data,
    })
  }

  function deleteCommune(id: string) {
    return apiFetch<void>(`/api/admin/communes/${id}`, { method: 'DELETE' })
  }

  // --- Admin paginated lists ---

  function fetchAdminProvinces(params: { search?: string; skip?: number; limit?: number } = {}) {
    const query = new URLSearchParams()
    if (params.search) query.set('search', params.search)
    if (params.skip !== undefined) query.set('skip', String(params.skip))
    if (params.limit !== undefined) query.set('limit', String(params.limit))
    const qs = query.toString()
    return apiFetch<PaginatedResponse<ProvinceListItem>>(`/api/admin/provinces${qs ? '?' + qs : ''}`)
  }

  function fetchAdminRegions(params: { province_id?: string; search?: string; skip?: number; limit?: number } = {}) {
    const query = new URLSearchParams()
    if (params.province_id) query.set('province_id', params.province_id)
    if (params.search) query.set('search', params.search)
    if (params.skip !== undefined) query.set('skip', String(params.skip))
    if (params.limit !== undefined) query.set('limit', String(params.limit))
    const qs = query.toString()
    return apiFetch<PaginatedResponse<RegionListItem>>(`/api/admin/regions${qs ? '?' + qs : ''}`)
  }

  function fetchAdminCommunes(params: { region_id?: string; search?: string; skip?: number; limit?: number } = {}) {
    const query = new URLSearchParams()
    if (params.region_id) query.set('region_id', params.region_id)
    if (params.search) query.set('search', params.search)
    if (params.skip !== undefined) query.set('skip', String(params.skip))
    if (params.limit !== undefined) query.set('limit', String(params.limit))
    const qs = query.toString()
    return apiFetch<PaginatedResponse<CommuneListItem>>(`/api/admin/communes${qs ? '?' + qs : ''}`)
  }

  return {
    fetchIdsWithComptes,
    fetchProvinces,
    fetchProvinceDetail,
    fetchRegions,
    fetchRegionDetail,
    fetchCommunes,
    fetchCommuneDetail,
    fetchHierarchy,
    createProvince,
    updateProvince,
    deleteProvince,
    createRegion,
    updateRegion,
    deleteRegion,
    createCommune,
    updateCommune,
    deleteCommune,
    fetchAdminProvinces,
    fetchAdminRegions,
    fetchAdminCommunes,
  }
}
