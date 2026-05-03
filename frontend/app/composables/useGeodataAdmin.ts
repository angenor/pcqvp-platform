import type {
  GeodataJobAccepted,
  GeodataJobStatus,
  GeodataUploadResponse,
  GeodataVersionDetail,
  GeodataVersionList,
} from '~/types/geodata'

const BASE = '/api/admin/geodata/regions'
const POLL_INTERVAL_MS = 1500
const POLL_MAX_ATTEMPTS = 240 // 6 min

export function useGeodataAdmin() {
  const { apiFetch } = useApi()

  async function uploadVersion(
    file: File,
    notes?: string
  ): Promise<GeodataUploadResponse | GeodataJobAccepted> {
    const form = new FormData()
    form.append('file', file)
    if (notes) form.append('notes', notes)
    return apiFetch<GeodataUploadResponse | GeodataJobAccepted>(
      `${BASE}/upload`,
      { method: 'POST', body: form }
    )
  }

  function isJobAccepted(
    res: GeodataUploadResponse | GeodataJobAccepted
  ): res is GeodataJobAccepted {
    return 'job_id' in res
  }

  async function getJob(jobId: string): Promise<GeodataJobStatus> {
    return apiFetch<GeodataJobStatus>(`${BASE}/jobs/${jobId}`)
  }

  async function pollJob(jobId: string): Promise<GeodataJobStatus> {
    for (let i = 0; i < POLL_MAX_ATTEMPTS; i++) {
      const job = await getJob(jobId)
      if (job.status === 'done' || job.status === 'failed') return job
      await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS))
    }
    throw new Error('Polling expiré (timeout)')
  }

  async function listVersions(
    limit = 20,
    offset = 0
  ): Promise<GeodataVersionList> {
    return apiFetch<GeodataVersionList>(
      `${BASE}/versions?limit=${limit}&offset=${offset}`
    )
  }

  async function getVersion(id: string): Promise<GeodataVersionDetail> {
    return apiFetch<GeodataVersionDetail>(`${BASE}/versions/${id}`)
  }

  async function activateVersion(id: string): Promise<GeodataVersionDetail> {
    return apiFetch<GeodataVersionDetail>(
      `${BASE}/versions/${id}/activate`,
      { method: 'POST' }
    )
  }

  async function deleteVersion(id: string): Promise<void> {
    await apiFetch<void>(`${BASE}/versions/${id}`, { method: 'DELETE' })
  }

  return {
    uploadVersion,
    isJobAccepted,
    getJob,
    pollJob,
    listVersions,
    getVersion,
    activateVersion,
    deleteVersion,
  }
}
