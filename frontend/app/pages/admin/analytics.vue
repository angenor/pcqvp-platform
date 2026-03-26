<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})

useHead({ title: 'Admin - Analytics' })

const { dashboard, loading, loadDashboard, purge } = useAnalytics()
const period = ref('30d')
const showPurgeModal = ref(false)

async function changePeriod(p: string) {
  period.value = p
  await loadDashboard(p)
}

async function handlePurge() {
  const result = await purge()
  showPurgeModal.value = false
  alert(result.message)
  await loadDashboard(period.value)
}

onMounted(() => loadDashboard(period.value))
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-(--text-primary)">Analytics</h1>
      <div class="flex gap-2">
        <UiButton
          v-for="p in ['7d', '30d', '12m']"
          :key="p"
          :variant="period === p ? 'primary' : 'secondary'"
          size="sm"
          @click="changePeriod(p)"
        >
          {{ p }}
        </UiButton>
      </div>
    </div>

    <!-- Purge alert -->
    <UiAlert
      v-if="dashboard?.data_retention.purge_eligible"
      variant="warning"
      class="mb-6"
    >
      <div class="flex items-center justify-between w-full">
        <span>{{ dashboard.data_retention.purge_eligible_count }} enregistrements de plus de 12 mois peuvent etre supprimes.</span>
        <UiButton variant="danger" size="sm" @click="showPurgeModal = true">Purger</UiButton>
      </div>
    </UiAlert>

    <UiModal v-model="showPurgeModal" title="Confirmer la purge" danger>
      <p class="text-sm text-(--text-secondary)">
        Supprimer les donnees de plus de 12 mois ? Cette action est irreversible.
      </p>
      <template #footer>
        <UiButton variant="ghost" @click="showPurgeModal = false">Annuler</UiButton>
        <UiButton variant="danger" @click="handlePurge">Confirmer la purge</UiButton>
      </template>
    </UiModal>

    <div v-if="loading" class="flex justify-center py-12">
      <UiLoadingSpinner size="lg" />
    </div>

    <template v-else-if="dashboard">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Visits -->
        <div
          class="p-6 rounded-lg border border-(--border-default)"
          :style="{ backgroundColor: 'var(--bg-card)' }"
        >
          <h2 class="text-lg font-semibold text-(--text-primary) mb-4">
            Visites
            <span class="text-2xl ml-2 font-mono">{{ dashboard.visits.total }}</span>
          </h2>
          <div class="space-y-2">
            <div
              v-for="(count, pageType) in dashboard.visits.by_page_type"
              :key="pageType"
              class="flex justify-between text-sm"
            >
              <span class="text-(--text-secondary) capitalize">{{ pageType }}</span>
              <span class="font-medium font-mono text-(--text-primary)">{{ count }}</span>
            </div>
          </div>
        </div>

        <!-- Downloads -->
        <div
          class="p-6 rounded-lg border border-(--border-default)"
          :style="{ backgroundColor: 'var(--bg-card)' }"
        >
          <h2 class="text-lg font-semibold text-(--text-primary) mb-4">
            Telechargements
            <span class="text-2xl ml-2 font-mono">{{ dashboard.downloads.total }}</span>
          </h2>
          <div class="space-y-2">
            <div
              v-for="(count, format) in dashboard.downloads.by_format"
              :key="format"
              class="flex justify-between text-sm"
            >
              <span class="text-(--text-secondary) uppercase">{{ format }}</span>
              <span class="font-medium font-mono text-(--text-primary)">{{ count }}</span>
            </div>
          </div>
          <p v-if="Object.keys(dashboard.downloads.by_format).length === 0" class="text-sm text-(--text-muted)">
            Aucun telechargement sur cette periode.
          </p>
        </div>
      </div>

      <!-- Visit trends -->
      <div
        class="mt-6 p-6 rounded-lg border border-(--border-default)"
        :style="{ backgroundColor: 'var(--bg-card)' }"
      >
        <h2 class="text-lg font-semibold text-(--text-primary) mb-4">Tendance des visites</h2>
        <div v-if="dashboard.visits.trend.length === 0" class="text-sm text-(--text-muted)">
          Pas de donnees sur cette periode.
        </div>
        <div v-else class="space-y-1">
          <div
            v-for="item in dashboard.visits.trend.slice(-14)"
            :key="item.date"
            class="flex items-center gap-3 text-sm"
          >
            <span class="w-24 text-(--text-muted) font-mono">{{ item.date }}</span>
            <div class="flex-1 bg-(--interactive-hover) rounded-full h-4 overflow-hidden">
              <div
                class="h-full rounded-full transition-all"
                :style="{
                  width: `${Math.min(100, (item.count / Math.max(...dashboard!.visits.trend.map(t => t.count))) * 100)}%`,
                  backgroundColor: 'var(--color-primary)',
                }"
              />
            </div>
            <span class="w-12 text-right font-medium font-mono text-(--text-primary)">{{ item.count }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
