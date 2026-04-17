import type {
  CollectivityDocument,
  CollectivityDocumentCreate,
  CollectivityDocumentFileReplace,
  CollectivityDocumentUpdate,
  CollectivityDocumentUploadResponse,
  CollectivityDocumentsReorder,
  CollectivityParentType,
} from '../../../packages/shared/types/collectivity'

export function useCollectivityDocuments() {
  const { apiFetch } = useApi()

  function listDocuments(
    parentType: CollectivityParentType,
    parentId: string,
  ): Promise<CollectivityDocument[]> {
    const qs = new URLSearchParams({
      parent_type: parentType,
      parent_id: parentId,
    }).toString()
    return apiFetch<CollectivityDocument[]>(
      `/api/admin/collectivity-documents?${qs}`,
    )
  }

  function createDocument(
    data: CollectivityDocumentCreate,
  ): Promise<CollectivityDocument> {
    return apiFetch<CollectivityDocument>('/api/admin/collectivity-documents', {
      method: 'POST',
      body: data,
    })
  }

  function updateDocumentTitle(
    id: string,
    data: CollectivityDocumentUpdate,
  ): Promise<CollectivityDocument> {
    return apiFetch<CollectivityDocument>(
      `/api/admin/collectivity-documents/${id}`,
      {
        method: 'PUT',
        body: data,
      },
    )
  }

  function replaceDocumentFile(
    id: string,
    data: CollectivityDocumentFileReplace,
  ): Promise<CollectivityDocument> {
    return apiFetch<CollectivityDocument>(
      `/api/admin/collectivity-documents/${id}/file`,
      {
        method: 'PUT',
        body: data,
      },
    )
  }

  function reorderDocuments(
    data: CollectivityDocumentsReorder,
  ): Promise<CollectivityDocument[]> {
    return apiFetch<CollectivityDocument[]>(
      '/api/admin/collectivity-documents/reorder',
      {
        method: 'PATCH',
        body: data,
      },
    )
  }

  function deleteDocument(id: string): Promise<void> {
    return apiFetch<void>(`/api/admin/collectivity-documents/${id}`, {
      method: 'DELETE',
    })
  }

  async function uploadDocumentFile(
    file: File,
  ): Promise<CollectivityDocumentUploadResponse> {
    const formData = new FormData()
    formData.append('document', file)
    return apiFetch<CollectivityDocumentUploadResponse>(
      '/api/admin/upload/document',
      {
        method: 'POST',
        body: formData,
      },
    )
  }

  return {
    listDocuments,
    createDocument,
    updateDocumentTitle,
    replaceDocumentFile,
    reorderDocuments,
    deleteDocument,
    uploadDocumentFile,
  }
}
