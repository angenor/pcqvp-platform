<script setup lang="ts">
import type { RegionListItem, CommuneListItem } from '~/types/geography'

const { fetchRegions } = useGeography()

const regions = ref<RegionListItem[]>([])
const isLoading = ref(true)
const hoveredRegion = ref<RegionListItem | null>(null)
const selectedRegion = ref<RegionListItem | null>(null)
const selectedCommune = ref<CommuneListItem | null>(null)

// Modal communes
const showCommunesModal = ref(false)

onMounted(async () => {
  try {
    regions.value = await fetchRegions()
  } catch (err) {
    console.error('Erreur lors du chargement des régions:', err)
  } finally {
    isLoading.value = false
  }
})

const handleRegionClick = (region: RegionListItem | null) => {
  if (region) {
    selectedRegion.value = region
    selectedCommune.value = null
    showCommunesModal.value = true
  }
}

const handleRegionHover = (region: RegionListItem | null) => {
  hoveredRegion.value = region
}

const handleCommuneSelect = (commune: CommuneListItem) => {
  showCommunesModal.value = false
  selectedCommune.value = commune
}

const navigateToCommune = () => {
  if (selectedCommune.value) {
    navigateTo(`/collectivite/commune-${selectedCommune.value.id}`)
  }
}

const clearSelection = () => {
  selectedRegion.value = null
  selectedCommune.value = null
}
</script>

<template>
  <section class="py-8">
    <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-8 text-center">
      Carte des Régions de Madagascar
    </h2>

    <div class="grid lg:grid-cols-3 gap-6 items-stretch map-stats-grid">
      <!-- Carte (2/3 de largeur sur desktop) -->
      <div class="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700 overflow-hidden map-container">
        <ClientOnly>
          <MadagascarMap
            :regions="regions"
            :is-loading="isLoading"
            class="h-full w-full"
            @region-click="handleRegionClick"
            @region-hover="handleRegionHover"
          />
          <template #fallback>
            <div class="h-full flex items-center justify-center">
              <UiLoadingSpinner />
            </div>
          </template>
        </ClientOnly>
      </div>

      <!-- Panneau Notebook Paper -->
      <div class="notebook-card">
        <div class="notebook-card-inner">
          <Transition name="notebook-fade" mode="out-in">
            <!-- Vue commune sélectionnée -->
            <div v-if="selectedCommune && selectedRegion" key="commune" class="notebook-content">
              <h3 class="notebook-title">Commune sélectionnée</h3>

              <div class="notebook-info-box">
                <span class="notebook-info-label">Commune</span>
                <span class="notebook-info-value">{{ selectedCommune.name }}</span>
              </div>

              <div class="notebook-info-box">
                <span class="notebook-info-label">Région</span>
                <span class="notebook-info-value">{{ selectedRegion.name }}</span>
              </div>

              <div class="notebook-separator"></div>

              <button
                class="notebook-btn"
                @click="navigateToCommune"
              >
                Voir le compte administratif
              </button>

              <button
                class="notebook-btn notebook-btn--secondary"
                @click="showCommunesModal = true"
              >
                Changer de commune
              </button>

              <button
                class="notebook-btn notebook-btn--secondary"
                @click="clearSelection"
              >
                Retour a la liste
              </button>
            </div>

            <!-- Vue region sélectionnée (pas encore de commune) -->
            <div v-else-if="selectedRegion" key="region" class="notebook-content">
              <h3 class="notebook-title">{{ selectedRegion.name }}</h3>

              <div class="notebook-info-box">
                <span class="notebook-info-label">Région sélectionnée</span>
                <span class="notebook-info-value">{{ selectedRegion.name }}</span>
              </div>

              <div class="notebook-separator"></div>

              <p class="notebook-text">
                Sélectionnez une commune pour consulter son compte administratif.
              </p>

              <button
                class="notebook-btn"
                @click="showCommunesModal = true"
              >
                Voir les communes
              </button>

              <button
                class="notebook-btn notebook-btn--secondary"
                @click="clearSelection"
              >
                Retour a la liste
              </button>
            </div>

            <!-- Vue par défaut : liste des régions -->
            <div v-else key="list" class="notebook-content">
              <h3 class="notebook-title">Régions de Madagascar</h3>

              <!-- Loading skeleton -->
              <template v-if="isLoading">
                <div v-for="i in 8" :key="i" class="skeleton-line"></div>
              </template>

              <!-- Liste des régions -->
              <template v-else>
                <button
                  v-for="region in regions"
                  :key="region.id"
                  class="notebook-item"
                  :class="{ 'notebook-item--active': hoveredRegion?.id === region.id }"
                  @click="handleRegionClick(region)"
                  @mouseenter="hoveredRegion = region"
                  @mouseleave="hoveredRegion = null"
                >
                  <span class="notebook-bullet">&#9679;</span>
                  <span>{{ region.name }}</span>
                </button>

                <div class="notebook-footer">
                  <span>Total : {{ regions.length }} régions</span>
                </div>
              </template>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- Modal sélection de commune -->
    <HomeCommunesModal
      v-model:show="showCommunesModal"
      :region="selectedRegion"
      @select-commune="handleCommuneSelect"
    />
  </section>
</template>

<style scoped>
/* Import Google Font for handwriting style */
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@400;500;600;700&display=swap');

.map-stats-grid {
  min-height: 600px;
}

.map-container {
  min-height: 500px;
  height: 600px;
}

@media (min-width: 1024px) {
  .map-container {
    height: 650px;
  }
}

@media (max-width: 1023px) {
  .map-container {
    height: 500px;
    min-height: 400px;
  }
}

/* ============================================
   Notebook / Paper Effect
   ============================================ */

.notebook-card {
  position: relative;
  filter: drop-shadow(0 0 8px rgba(0, 0, 0, 0.25));
  transition: filter 0.3s ease;
  min-height: 500px;
}

.notebook-card:hover {
  filter: drop-shadow(0 0 12px rgba(0, 0, 0, 0.35));
}

/* Sticky tape effect */
.notebook-card::before,
.notebook-card::after {
  content: "";
  position: absolute;
  width: 20px;
  height: 45px;
  background: #e6e6e6b8;
  z-index: 10;
}

.notebook-card::before {
  left: 60%;
  top: -12px;
  transform: rotate(45deg);
}

.notebook-card::after {
  left: 40%;
  bottom: -12px;
  transform: rotate(-45deg);
}

.dark .notebook-card::before,
.dark .notebook-card::after {
  background: #475569b8;
}

/* Inner paper */
.notebook-card-inner {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  overflow-y: auto;
  border-radius: 0.5rem;
  padding: 1.25rem 15px 1.25rem 45px;

  /* Lined paper background */
  background:
    repeating-linear-gradient(
      #0000 0 calc(1.6rem - 1px),
      #c5dbe8 0 1.6rem
    ) right bottom / 100% 100%,
    linear-gradient(#ef4444 0 0) 35px 0 / 2px 100% #fffef5;
  background-repeat: no-repeat;
  line-height: 1.6rem;

  /* Notebook holes */
  -webkit-mask: radial-gradient(circle 0.5rem at 17px 50%, #0000 98%, #000) 0 0 / 100% 3.2rem;
  mask: radial-gradient(circle 0.5rem at 17px 50%, #0000 98%, #000) 0 0 / 100% 3.2rem;

  /* Handwriting font */
  font-family: 'Caveat', cursive;
  font-size: 1.25rem;
  color: #1e3a5f;
  font-weight: 500;
}

/* Dark mode paper */
.dark .notebook-card-inner {
  background:
    repeating-linear-gradient(
      #0000 0 calc(1.6rem - 1px),
      #374151 0 1.6rem
    ) right bottom / 100% 100%,
    linear-gradient(#ef4444 0 0) 35px 0 / 2px 100% #1e293b;
  background-repeat: no-repeat;
  color: #f1f5f9;
}

/* Content area */
.notebook-content {
  display: flex;
  flex-direction: column;
}

/* Title */
.notebook-title {
  font-family: 'Caveat', cursive;
  font-size: 1.7rem;
  font-weight: 700;
  color: #1e3a8a;
  text-decoration: underline;
  text-decoration-color: #2563eb;
  text-underline-offset: 4px;
  margin-bottom: 0.5rem;
  line-height: 1.6rem;
  padding-top: 0.2rem;
}

.dark .notebook-title {
  color: #bfdbfe;
  text-decoration-color: #60a5fa;
}

/* Region item */
.notebook-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  line-height: 1.6rem;
  padding: 0 0.25rem;
  cursor: pointer;
  transition: background 0.15s ease;
  font-family: 'Caveat', cursive;
  font-size: 1.3rem;
  font-weight: 500;
  color: #1e3a5f;
  border: none;
  background: transparent;
  text-align: left;
  width: 100%;
}

.notebook-item:hover {
  background: rgba(254, 243, 199, 0.5);
}

.notebook-item--active {
  background: rgba(254, 243, 199, 0.7);
  font-weight: 700;
  color: #1e3a8a;
}

.dark .notebook-item {
  color: #e2e8f0;
}

.dark .notebook-item:hover {
  background: rgba(59, 130, 246, 0.15);
}

.dark .notebook-item--active {
  background: rgba(59, 130, 246, 0.25);
  color: #93c5fd;
}

/* Bullet */
.notebook-bullet {
  font-size: 0.5rem;
  color: #2563eb;
  flex-shrink: 0;
}

.dark .notebook-bullet {
  color: #60a5fa;
}

/* Footer */
.notebook-footer {
  margin-top: 0.5rem;
  padding-top: 0.25rem;
  border-top: 2px dashed #64748b;
  font-family: 'Caveat', cursive;
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e3a8a;
  text-align: center;
  line-height: 1.6rem;
}

.dark .notebook-footer {
  border-top-color: #4b5563;
  color: #93c5fd;
}

/* Info box (selected region) */
.notebook-info-box {
  display: flex;
  flex-direction: column;
  padding: 0.5rem 0.75rem;
  background: rgba(254, 249, 195, 0.6);
  border: 2px dashed #b45309;
  border-radius: 0.25rem;
  margin-bottom: 0.25rem;
  line-height: 1.6rem;
}

.dark .notebook-info-box {
  background: rgba(30, 58, 138, 0.3);
  border-color: #60a5fa;
}

.notebook-info-label {
  font-size: 1.1rem;
  color: #374151;
  font-weight: 500;
}

.dark .notebook-info-label {
  color: #d1d5db;
}

.notebook-info-value {
  font-size: 1.6rem;
  font-weight: 700;
  color: #1e3a8a;
}

.dark .notebook-info-value {
  color: #bfdbfe;
}

/* Text */
.notebook-text {
  font-family: 'Caveat', cursive;
  font-size: 1.15rem;
  color: #374151;
  line-height: 1.6rem;
}

.dark .notebook-text {
  color: #d1d5db;
}

/* Separator */
.notebook-separator {
  border-bottom: 2px dashed #64748b;
  margin: 0.25rem 0;
  line-height: 1.6rem;
  height: 1.6rem;
}

.dark .notebook-separator {
  border-bottom-color: #4b5563;
}

/* Buttons - notebook style */
.notebook-btn {
  font-family: 'Caveat', cursive;
  font-size: 1.4rem;
  font-weight: 700;
  line-height: 1.6rem;
  padding: 0.35rem 0.75rem;
  border: 2px solid #1e3a8a;
  border-radius: 0.25rem;
  box-shadow: 2px 2px 0 rgba(0, 0, 0, 0.15);
  cursor: pointer;
  transition: all 0.15s ease;
  background: linear-gradient(135deg, #1e40af 0%, #2563eb 50%, #1e40af 100%);
  color: #ffffff;
  text-shadow: 1px 1px 0 rgba(0, 0, 0, 0.2);
  width: 100%;
  text-align: center;
  margin-top: 0.25rem;
}

.notebook-btn:hover {
  transform: translate(-1px, -1px);
  box-shadow: 3px 3px 0 rgba(0, 0, 0, 0.2);
  background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 50%, #1e3a8a 100%);
}

.notebook-btn--secondary {
  background: #fffbeb;
  border-color: #92400e;
  color: #78350f;
  text-shadow: none;
}

.notebook-btn--secondary:hover {
  background: #fef3c7;
}

.dark .notebook-btn--secondary {
  background: #374151;
  border-color: #60a5fa;
  color: #e5e7eb;
}

.dark .notebook-btn--secondary:hover {
  background: #4b5563;
}

/* Stats grid */
.notebook-stat-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.5rem;
}

.notebook-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem;
  background: rgba(254, 249, 195, 0.5);
  border: 1px solid #d97706;
  border-radius: 0.25rem;
  line-height: 1.6rem;
}

.dark .notebook-stat {
  background: rgba(30, 58, 138, 0.25);
  border-color: #3b82f6;
}

.notebook-stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1e3a8a;
}

.dark .notebook-stat-value {
  color: #93c5fd;
}

.notebook-stat-label {
  font-size: 1rem;
  color: #374151;
}

.dark .notebook-stat-label {
  color: #d1d5db;
}

/* Loading skeleton */
.skeleton-line {
  height: 1.6rem;
  width: 70%;
  background: linear-gradient(90deg, transparent 0%, #c5dbe830 50%, transparent 100%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 2px;
}

.skeleton-line:nth-child(even) {
  width: 55%;
}

.dark .skeleton-line {
  background: linear-gradient(90deg, transparent 0%, #37415130 50%, transparent 100%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Transition notebook content swap */
.notebook-fade-enter-active,
.notebook-fade-leave-active {
  transition: opacity 0.3s ease;
}

.notebook-fade-enter-from,
.notebook-fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (min-width: 1024px) {
  .notebook-card {
    height: 650px;
  }
}

@media (max-width: 1023px) {
  .notebook-card {
    min-height: 300px;
    height: auto;
  }
}
</style>
