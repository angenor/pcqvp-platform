<script setup lang="ts">
useSeoMeta({
  title: 'Plateforme de suivi des revenus miniers - PCQVP Madagascar',
  description: 'Consultez les comptes administratifs publies des collectivites territoriales malgaches. Transparence des industries extractives.',
  ogTitle: 'Plateforme de suivi des revenus miniers - PCQVP Madagascar',
  ogDescription: 'Consultez les comptes administratifs publies des collectivites territoriales malgaches.',
})

function handleGeoSubmit(selection: { type: string; id: string }) {
  navigateTo(`/collectivite/${selection.type}-${selection.id}`)
}
</script>

<template>
  <div>
    <!-- Hero Section -->
    <section class="relative min-h-150 lg:min-h-175 flex items-center overflow-hidden -mt-16">
      <!-- Image de fond avec overlay -->
      <div class="absolute inset-0 z-0">
        <img
          src="/images/hero_background.jpg"
          alt="Exploitation minière à Madagascar"
          class="w-full h-full object-cover"
        />
        <!-- Overlay gradient -->
        <div class="absolute inset-0 bg-linear-to-r from-blue-900/60 via-blue-800/50 to-blue-900/50 dark:from-gray-900/70 dark:via-gray-800/60 dark:to-gray-900/60"></div>
        <!-- Pattern overlay pour texture -->
        <div class="absolute inset-0 opacity-5" style="background-image: url('data:image/svg+xml,%3Csvg width=&quot;60&quot; height=&quot;60&quot; viewBox=&quot;0 0 60 60&quot; xmlns=&quot;http://www.w3.org/2000/svg&quot;%3E%3Cg fill=&quot;none&quot; fill-rule=&quot;evenodd&quot;%3E%3Cg fill=&quot;%23ffffff&quot; fill-opacity=&quot;1&quot;%3E%3Cpath d=&quot;M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z&quot;/%3E%3C/g%3E%3C/g%3E%3C/svg%3E');"></div>
      </div>

      <!-- Contenu principal -->
      <div class="relative z-10 w-full">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-28">
          <!-- Titre principal -->
          <div class="text-center mb-8 lg:mb-12 animate-slide-up">
            <p class="uppercase text-2xl sm:text-3xl lg:text-4xl xl:text-5xl font-bold text-white mb-4 leading-tight drop-shadow-2xl">
              Plateforme de Suivi des Revenus Miniers
            </p>
            <p class="text-xl sm:text-2xl lg:text-3xl text-blue-100 font-light mb-6 drop-shadow-lg">
              Collectivités Territoriales de Madagascar
            </p>
            <div class="max-w-3xl mx-auto">
              <p class="text-base sm:text-lg text-blue-50 leading-relaxed drop-shadow-md">
                Publiez Ce Que Vous Payez - Madagascar
              </p>
              <!-- Badges valeurs -->
              <div class="flex flex-wrap justify-center gap-4 mt-6">
                <div class="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full border border-white/20">
                  <svg class="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-sm text-white font-medium">Transparence</span>
                </div>
                <div class="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full border border-white/20">
                  <svg class="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-sm text-white font-medium">Redevabilité</span>
                </div>
                <div class="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full border border-white/20">
                  <svg class="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-sm text-white font-medium">Accessibilité</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Formulaire de sélection -->
          <div class="max-w-3xl mx-auto animate-fade-in-up">
            <div class="bg-white/95 dark:bg-gray-800/95 backdrop-blur-lg rounded-2xl shadow-2xl p-6 sm:p-8 lg:p-10 transition-colors duration-200">
              <h3 class="text-xl sm:text-2xl font-bold text-gray-800 dark:text-white mb-6 text-center">
                Sélectionnez une collectivité
              </h3>
              <GeographySelector :on-submit="handleGeoSubmit" />
            </div>
          </div>
        </div>
      </div>

      <!-- Scroll indicator -->
      <div class="absolute bottom-8 left-1/2 -translate-x-1/2 z-20 animate-bounce">
        <svg class="w-6 h-6 text-white opacity-75" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </div>
    </section>

    <!-- Contenu principal sous le hero -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
      <!-- Section Statistiques -->
      <HomeStatsSection />

      <!-- Section Cartes informatives -->
      <HomeInfoCards />
    </main>
  </div>
</template>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(40px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fade-in 1s ease-out;
}

.animate-slide-up {
  animation: slide-up 0.8s ease-out 0.2s both;
}

.animate-fade-in-up {
  animation: fade-in-up 1s ease-out 0.4s both;
}
</style>
