<script setup lang="ts">
import type { EditorJSData } from '~/types/geography'
import type { ResourceLink } from '~/types/editorial'

const colorMode = useColorMode()

function toggleTheme() {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}

const logoSrc = computed(() => {
  return colorMode.value === 'dark'
    ? '/images/logos/logo_fond_noire_texte_blanc.jpeg'
    : '/images/logos/logo_fond_noire_texte_bleu.jpeg'
})

// Footer editorial content
const { fetchEditorial } = useEditorial()

const footerAboutContent = ref<EditorJSData | null>(null)
const footerAboutFallback = 'Projet "Minerais critiques : justice fiscale et redistribution de revenus" mené par PCQVP Madagascar et TI Madagascar.'
const footerContactEmail = ref('vramaherison@transparency.mg')
const footerContactText = ref('Transparency International - Initiative Madagascar')
const footerContactPhone = ref('')
const footerContactAddress = ref('')
const footerResources = ref<ResourceLink[]>([])
const hasAboutRichContent = ref(false)

onMounted(async () => {
  try {
    const data = await fetchEditorial()

    if (data.footer.about.content_json) {
      const json = data.footer.about.content_json as EditorJSData
      if (json.blocks?.length) {
        footerAboutContent.value = json
        hasAboutRichContent.value = true
      }
    }

    if (data.footer.contact.email) footerContactEmail.value = data.footer.contact.email
    if (data.footer.contact.phone) footerContactPhone.value = data.footer.contact.phone
    if (data.footer.contact.address) {
      footerContactAddress.value = data.footer.contact.address
      footerContactText.value = data.footer.contact.address
    }

    if (data.footer.resources.length) {
      footerResources.value = data.footer.resources
    }
  } catch {
    // use default values
  }
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900 transition-colors">
    <!-- Header -->
    <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <NuxtLink to="/" class="flex items-center">
            <img
              :src="logoSrc"
              :key="logoSrc"
              alt="PCQVP Madagascar"
              class="h-10 w-auto object-contain transition-opacity duration-300"
            />
          </NuxtLink>

          <!-- Search -->
          <SearchBar class="hidden md:block mx-4" />

          <!-- Navigation -->
          <nav class="flex items-center gap-4">
            <NuxtLink
              to="/signaler"
              class="inline-flex items-center gap-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white! px-4 py-2 rounded-lg transition-colors"
            >
              <font-awesome-icon icon="bullhorn" class="w-4 h-4" />
              Signaler
            </NuxtLink>

            <button
              class="p-2 rounded-md text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              :title="colorMode.value === 'dark' ? 'Mode clair' : 'Mode sombre'"
              @click="toggleTheme"
            >
              <svg v-if="colorMode.value === 'dark'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            </button>
          </nav>
        </div>

        <!-- Mobile search -->
        <div class="md:hidden pb-3">
          <SearchBar />
        </div>
      </div>
    </header>

    <!-- Main content -->
    <main class="flex-1">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 dark:bg-gray-950 text-white mt-16 print:hidden transition-colors duration-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- À propos -->
          <div>
            <h3 class="font-bold text-lg mb-3 text-white!">À propos</h3>
            <div v-if="hasAboutRichContent" class="text-gray-200 dark:text-gray-400 text-sm footer-rich-content max-h-40 overflow-hidden">
              <RichContentRenderer :description-json="footerAboutContent" />
            </div>
            <p v-else class="text-gray-200 dark:text-gray-400 text-sm">
              {{ footerAboutFallback }}
            </p>
          </div>

          <!-- Contact -->
          <div>
            <h3 class="font-bold text-lg mb-3 text-white!">Contact</h3>
            <div class="text-gray-200 dark:text-gray-400 text-sm space-y-1">
              <p v-if="footerContactEmail">
                Email: <a :href="`mailto:${footerContactEmail}`" class="text-blue-400 hover:text-blue-300 transition-colors">{{ footerContactEmail }}</a>
              </p>
              <p v-if="footerContactPhone">
                Tél: {{ footerContactPhone }}
              </p>
              <p v-if="footerContactText && !footerContactAddress">
                {{ footerContactText }}
              </p>
              <p v-if="footerContactAddress">
                {{ footerContactAddress }}
              </p>
            </div>
          </div>

          <!-- Ressources -->
          <div>
            <h3 class="font-bold text-lg mb-3 text-white!">Ressources</h3>
            <template v-if="footerResources.length">
              <ul class="space-y-2">
                <li v-for="resource in footerResources" :key="resource.id">
                  <a
                    :href="resource.url"
                    :target="resource.url.startsWith('http') ? '_blank' : undefined"
                    :rel="resource.url.startsWith('http') ? 'noopener noreferrer' : undefined"
                    class="text-sm text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    {{ resource.title }}
                  </a>
                </li>
              </ul>
            </template>
            <template v-else>
              <p class="text-gray-200 dark:text-gray-400 text-sm">
                Plateforme de suivi des revenus miniers<br>
                Collectivités Territoriales de Madagascar
              </p>
            </template>
            <div class="mt-3">
              <NuxtLink to="/signaler" class="inline-flex items-center gap-2 text-sm font-medium text-red-400 hover:text-red-300 transition-colors">
                <font-awesome-icon icon="bullhorn" class="w-4 h-4" />
                Signaler un problème
              </NuxtLink>
            </div>
          </div>
        </div>

        <div class="border-t border-gray-700 dark:border-gray-800 mt-8 pt-6 text-center text-gray-200 dark:text-gray-500 text-sm">
          <p>&copy; {{ new Date().getFullYear() }} PCQVP Madagascar. Tous droits réservés.</p>
          <p class="mt-3 text-gray-300 dark:text-gray-600">
            Plateforme développée par
            <a
              href="https://www.linkedin.com/company/herhero-forchange/"
              target="_blank"
              rel="noopener noreferrer"
              class="text-blue-400 hover:text-blue-300 dark:text-blue-500 dark:hover:text-blue-400 transition font-medium"
            >
              HerHero
            </a>
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>
