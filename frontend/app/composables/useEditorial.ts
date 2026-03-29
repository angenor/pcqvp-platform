import type {
  EditorialAdminResponse,
  EditorialPublicResponse,
  HeroUpdate,
  BodyUpdate,
  FooterAboutUpdate,
  ContactInfoUpdate,
  ResourceLinkCreate,
  ResourceLinkUpdate,
  ResourceLinkAdmin,
  ResourceReorder,
} from '~/types/editorial'

export function useEditorial() {
  const { apiFetch } = useApi()

  // --- Fetch ---

  function fetchEditorial() {
    return apiFetch<EditorialPublicResponse>('/api/editorial')
  }

  function fetchAdminEditorial() {
    return apiFetch<EditorialAdminResponse>('/api/admin/editorial')
  }

  // --- Hero ---

  function updateHero(data: HeroUpdate) {
    return apiFetch<{ message: string }>('/api/admin/editorial/hero', {
      method: 'PUT',
      body: data,
    })
  }

  // --- Body ---

  function updateBody(data: BodyUpdate) {
    return apiFetch<{ message: string }>('/api/admin/editorial/body', {
      method: 'PUT',
      body: data,
    })
  }

  // --- Footer About ---

  function updateFooterAbout(data: FooterAboutUpdate) {
    return apiFetch<{ message: string }>('/api/admin/editorial/footer/about', {
      method: 'PUT',
      body: data,
    })
  }

  // --- Contact ---

  function updateContact(data: ContactInfoUpdate) {
    return apiFetch<{ message: string }>('/api/admin/editorial/footer/contact', {
      method: 'PUT',
      body: data,
    })
  }

  // --- Resources ---

  function fetchResources() {
    return apiFetch<ResourceLinkAdmin[]>('/api/admin/editorial/footer/resources')
  }

  function createResource(data: ResourceLinkCreate) {
    return apiFetch<ResourceLinkAdmin>('/api/admin/editorial/footer/resources', {
      method: 'POST',
      body: data,
    })
  }

  function updateResource(id: string, data: ResourceLinkUpdate) {
    return apiFetch<ResourceLinkAdmin>(`/api/admin/editorial/footer/resources/${id}`, {
      method: 'PUT',
      body: data,
    })
  }

  function deleteResource(id: string) {
    return apiFetch<void>(`/api/admin/editorial/footer/resources/${id}`, {
      method: 'DELETE',
    })
  }

  function reorderResources(data: ResourceReorder) {
    return apiFetch<{ message: string }>('/api/admin/editorial/footer/resources/reorder', {
      method: 'PUT',
      body: data,
    })
  }

  return {
    fetchEditorial,
    fetchAdminEditorial,
    updateHero,
    updateBody,
    updateFooterAbout,
    updateContact,
    fetchResources,
    createResource,
    updateResource,
    deleteResource,
    reorderResources,
  }
}
