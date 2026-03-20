<script setup lang="ts">
interface HealthResponse {
  status: string
  db: string
  detail?: string
}

const { apiFetch } = useApi()

const health = ref<HealthResponse | null>(null)
const healthError = ref(false)

onMounted(async () => {
  try {
    health.value = await apiFetch<HealthResponse>('/health')
  } catch {
    healthError.value = true
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4">
    <div class="max-w-2xl mx-auto text-center">
      <h1 class="text-4xl font-bold text-gray-900 dark:text-white">Plateforme PCQVP</h1>
      <p class="mt-4 text-lg text-gray-600 dark:text-gray-400">
        Publiez Ce Que Vous Payez - Madagascar
      </p>

      <div class="mt-8">
        <GeographySelector />
      </div>

      <div class="mt-6">
        <div v-if="healthError" class="inline-flex items-center gap-2 rounded-full bg-red-100 dark:bg-red-900/30 px-4 py-2 text-sm text-red-700 dark:text-red-400">
          <span class="h-2 w-2 rounded-full bg-red-500" />
          Backend indisponible
        </div>
        <div v-else-if="health?.db === 'connected'" class="inline-flex items-center gap-2 rounded-full bg-green-100 dark:bg-green-900/30 px-4 py-2 text-sm text-green-700 dark:text-green-400">
          <span class="h-2 w-2 rounded-full bg-green-500" />
          Backend connecte
        </div>
        <div v-else-if="health" class="inline-flex items-center gap-2 rounded-full bg-yellow-100 dark:bg-yellow-900/30 px-4 py-2 text-sm text-yellow-700 dark:text-yellow-400">
          <span class="h-2 w-2 rounded-full bg-yellow-500" />
          Base de donnees deconnectee
        </div>
      </div>
    </div>
  </div>
</template>
