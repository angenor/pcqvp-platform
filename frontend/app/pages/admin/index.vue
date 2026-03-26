<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const { apiFetch } = useApi()

interface DashboardStats {
  comptes: { total: number; published: number; draft: number }
  collectivites: { provinces: number; regions: number; communes: number }
  users: number
  downloads: number
}

const stats = ref<DashboardStats | null>(null)
const loading = ref(true)
const error = ref('')

async function loadStats() {
  loading.value = true
  try {
    stats.value = await apiFetch<DashboardStats>('/api/admin/analytics/stats')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Erreur lors du chargement des statistiques'
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6 text-(--text-primary)">
      Tableau de bord
    </h1>

    <UiAlert v-if="error" variant="error" class="mb-4">
      {{ error }}
    </UiAlert>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <UiStatCard
        label="Comptes administratifs"
        :value="stats?.comptes.total ?? 0"
        :icon="['fas', 'calculator']"
        variant="primary"
        :loading="loading"
        to="/admin/accounts"
      />
      <UiStatCard
        label="Collectivites"
        :value="stats ? stats.collectivites.provinces + stats.collectivites.regions + stats.collectivites.communes : 0"
        :icon="['fas', 'map']"
        variant="info"
        :loading="loading"
        to="/admin/geography/provinces"
      />
      <UiStatCard
        label="Utilisateurs"
        :value="stats?.users ?? 0"
        :icon="['fas', 'users']"
        variant="success"
        :loading="loading"
        to="/admin/users"
      />
      <UiStatCard
        label="Telechargements"
        :value="stats?.downloads ?? 0"
        :icon="['fas', 'download']"
        variant="warning"
        :loading="loading"
        to="/admin/analytics"
      />
    </div>

    <!-- Details sous les cartes -->
    <div v-if="stats && !loading" class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
      <div
        class="p-5 rounded-lg border border-(--border-default)"
        :style="{ backgroundColor: 'var(--bg-card)' }"
      >
        <h3 class="text-sm font-semibold uppercase tracking-wider text-(--text-secondary) mb-3">
          Comptes administratifs
        </h3>
        <div class="flex gap-4 text-sm">
          <UiBadge variant="success" dot>{{ stats.comptes.published }} publies</UiBadge>
          <UiBadge variant="warning" dot>{{ stats.comptes.draft }} brouillons</UiBadge>
        </div>
      </div>

      <div
        class="p-5 rounded-lg border border-(--border-default)"
        :style="{ backgroundColor: 'var(--bg-card)' }"
      >
        <h3 class="text-sm font-semibold uppercase tracking-wider text-(--text-secondary) mb-3">
          Collectivites
        </h3>
        <div class="flex flex-col gap-1 text-sm text-(--text-secondary)">
          <span>{{ stats.collectivites.provinces }} provinces</span>
          <span>{{ stats.collectivites.regions }} regions</span>
          <span>{{ stats.collectivites.communes }} communes</span>
        </div>
      </div>
    </div>
  </div>
</template>
