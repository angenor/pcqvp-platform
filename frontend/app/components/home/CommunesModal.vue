<script setup lang="ts">
import type { RegionListItem, CommuneListItem } from '~/types/geography'

const props = defineProps<{
  show: boolean
  region: RegionListItem | null
  regionHasCompte?: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  'select-commune': [commune: CommuneListItem]
  'go-to-region': []
}>()

const { fetchCommunes } = useGeography()
const communes = ref<CommuneListItem[]>([])
const isLoading = ref(false)
const searchQuery = ref('')

watch(() => props.region, async (region) => {
  if (region && props.show) {
    await loadCommunes(region.id)
  }
})

watch(() => props.show, async (show) => {
  if (show && props.region) {
    await loadCommunes(props.region.id)
  } else {
    searchQuery.value = ''
  }
})

const loadCommunes = async (regionId: string) => {
  isLoading.value = true
  communes.value = []
  try {
    communes.value = await fetchCommunes(regionId, { hasComptes: true })
  } catch (err) {
    console.error('Erreur lors du chargement des communes:', err)
  } finally {
    isLoading.value = false
  }
}

const filteredCommunes = computed(() => {
  if (!searchQuery.value) return communes.value
  const q = searchQuery.value.toLowerCase()
  return communes.value.filter(c => c.name.toLowerCase().includes(q))
})

const close = () => {
  emit('update:show', false)
}

const selectCommune = (commune: CommuneListItem) => {
  emit('select-commune', commune)
  close()
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="show"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50 backdrop-blur-sm"
          @click="close"
        ></div>

        <!-- Modal content -->
        <div class="relative bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-md w-full max-h-[80vh] overflow-hidden">
          <!-- Header -->
          <div class="p-4 border-b border-gray-200 dark:border-gray-700">
            <div class="flex items-center justify-between mb-3">
              <div>
                <h3 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  {{ region?.name || 'Région' }}
                </h3>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {{ regionHasCompte && communes.length ? 'Compte régional et communes disponibles' : regionHasCompte ? 'Compte régional disponible' : 'Sélectionnez une commune' }}
                </p>
              </div>
              <button
                @click="close"
                class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition cursor-pointer"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- Recherche -->
            <div class="relative">
              <svg class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Rechercher une commune..."
                class="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              />
            </div>
          </div>

          <!-- Liste des communes -->
          <div class="p-4 overflow-y-auto max-h-[55vh]">
            <!-- Bouton compte régional -->
            <div v-if="regionHasCompte && !isLoading" class="mb-4">
              <button
                @click="emit('go-to-region'); close()"
                class="w-full flex items-center justify-between p-3 rounded-lg bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700 hover:bg-blue-100 dark:hover:bg-blue-900/50 cursor-pointer transition group"
              >
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-full flex items-center justify-center bg-blue-600 dark:bg-blue-500">
                    <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div class="text-left">
                    <p class="font-semibold text-sm text-blue-900 dark:text-blue-100">Compte de la région</p>
                    <p class="text-xs text-blue-600 dark:text-blue-400">Voir le compte administratif régional</p>
                  </div>
                </div>
                <svg class="w-4 h-4 text-blue-400 group-hover:text-blue-600 dark:group-hover:text-blue-300 transition" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>

              <div v-if="communes.length" class="mt-3 mb-1 flex items-center gap-2">
                <div class="flex-1 border-t border-gray-200 dark:border-gray-700"></div>
                <span class="text-xs text-gray-400 dark:text-gray-500 uppercase tracking-wide">Communes</span>
                <div class="flex-1 border-t border-gray-200 dark:border-gray-700"></div>
              </div>
            </div>

            <!-- Loading -->
            <div v-if="isLoading" class="flex flex-col items-center gap-3 py-8">
              <UiLoadingSpinner />
              <span class="text-sm text-gray-500 dark:text-gray-400">Chargement...</span>
            </div>

            <!-- Aucun résultat -->
            <div v-else-if="filteredCommunes.length === 0 && !regionHasCompte" class="text-center py-8">
              <svg class="w-8 h-8 text-gray-300 dark:text-gray-600 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                {{ searchQuery ? 'Aucune commune trouvée' : 'Aucune commune dans cette région' }}
              </p>
            </div>

            <!-- Liste -->
            <div v-else class="space-y-1.5">
              <button
                v-for="commune in filteredCommunes"
                :key="commune.id"
                @click="selectCommune(commune)"
                class="w-full flex items-center justify-between p-3 rounded-lg border border-transparent hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:border-blue-200 dark:hover:border-blue-700 cursor-pointer transition group"
              >
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-full flex items-center justify-center bg-blue-100 dark:bg-blue-900/50">
                    <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                  <p class="font-medium text-sm text-gray-900 dark:text-white text-left">
                    {{ commune.name }}
                  </p>
                </div>
                <svg class="w-3 h-3 text-gray-300 group-hover:text-blue-500 dark:text-gray-600 dark:group-hover:text-blue-400 transition" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Footer -->
          <div class="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
            <button
              @click="close"
              class="w-full py-2 px-4 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition text-sm font-medium cursor-pointer"
            >
              Fermer
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from > div:last-child,
.modal-leave-to > div:last-child {
  transform: scale(0.95) translateY(20px);
}

.modal-enter-active > div:last-child,
.modal-leave-active > div:last-child {
  transition: all 0.3s ease;
}
</style>
