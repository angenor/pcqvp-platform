<script setup lang="ts">
interface HealthResponse {
  status: string
  db: string
  detail?: string
}

const { data: health, error } = await useApi<HealthResponse>('/health')
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-center">
      <h1 class="text-4xl font-bold text-gray-900">Plateforme PCQVP</h1>
      <p class="mt-4 text-lg text-gray-600">
        Publiez Ce Que Vous Payez - Madagascar
      </p>
      <div class="mt-6">
        <div v-if="error" class="inline-flex items-center gap-2 rounded-full bg-red-100 px-4 py-2 text-sm text-red-700">
          <span class="h-2 w-2 rounded-full bg-red-500" />
          Backend indisponible
        </div>
        <div v-else-if="health?.db === 'connected'" class="inline-flex items-center gap-2 rounded-full bg-green-100 px-4 py-2 text-sm text-green-700">
          <span class="h-2 w-2 rounded-full bg-green-500" />
          Backend connecte
        </div>
        <div v-else class="inline-flex items-center gap-2 rounded-full bg-yellow-100 px-4 py-2 text-sm text-yellow-700">
          <span class="h-2 w-2 rounded-full bg-yellow-500" />
          Base de donnees deconnectee
        </div>
      </div>
    </div>
  </div>
</template>
