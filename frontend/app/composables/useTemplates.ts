import type {
  TemplateListResponse,
  TemplateDetail,
  TemplateLine,
  TemplateColumn,
} from '~/types/templates'

export function useTemplates() {
  const { apiFetch } = useApi()

  function fetchTemplates() {
    return apiFetch<TemplateListResponse>('/api/admin/templates')
  }

  function fetchTemplate(id: string) {
    return apiFetch<TemplateDetail>(`/api/admin/templates/${id}`)
  }

  function addLine(templateId: string, lineData: Omit<TemplateLine, 'id'>) {
    return apiFetch<TemplateLine>(`/api/admin/templates/${templateId}/lines`, {
      method: 'POST',
      body: lineData,
    })
  }

  function deleteLine(templateId: string, lineId: string) {
    return apiFetch<void>(`/api/admin/templates/${templateId}/lines/${lineId}`, {
      method: 'DELETE',
    })
  }

  function updateLines(templateId: string, linesData: TemplateLine[]) {
    return apiFetch<TemplateLine[]>(`/api/admin/templates/${templateId}/lines`, {
      method: 'PUT',
      body: linesData,
    })
  }

  function updateColumns(templateId: string, columnsData: TemplateColumn[]) {
    return apiFetch<TemplateColumn[]>(`/api/admin/templates/${templateId}/columns`, {
      method: 'PUT',
      body: columnsData,
    })
  }

  return {
    fetchTemplates,
    fetchTemplate,
    addLine,
    deleteLine,
    updateLines,
    updateColumns,
  }
}
