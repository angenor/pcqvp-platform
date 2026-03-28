<script setup lang="ts">
import type { EditorJSData } from '~/types/geography'
import type {
  EditorialAdminResponse,
  ResourceLinkAdmin,
} from '~/types/editorial'

definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const {
  fetchAdminEditorial,
  updateHero,
  updateBody,
  updateFooterAbout,
  updateContact,
  createResource,
  updateResource,
  deleteResource,
  reorderResources,
} = useEditorial()

const loading = ref(true)
const activeTab = ref<'hero' | 'body' | 'footer'>('hero')

// --- Hero state ---
const heroTitle = ref('')
const heroSubtitle = ref('')
const heroDescription = ref('')
const heroSaving = ref(false)
const heroFeedback = ref('')

// --- Body state ---
const bodyContent = ref<EditorJSData | null>(null)
const bodySaving = ref(false)
const bodyFeedback = ref('')

// --- Footer About state ---
const footerAboutContent = ref<EditorJSData | null>(null)
const footerAboutSaving = ref(false)
const footerAboutFeedback = ref('')

// --- Contact state ---
const contactEmail = ref('')
const contactPhone = ref('')
const contactAddress = ref('')
const contactSaving = ref(false)
const contactFeedback = ref('')

// --- Resources state ---
const resources = ref<ResourceLinkAdmin[]>([])
const newResourceTitle = ref('')
const newResourceUrl = ref('')
const resourceSaving = ref(false)
const resourceFeedback = ref('')
const editingResource = ref<string | null>(null)
const editResourceTitle = ref('')
const editResourceUrl = ref('')

// --- Load data ---
async function loadData() {
  loading.value = true
  try {
    const data = await fetchAdminEditorial()

    heroTitle.value = data.hero.title.value
    heroSubtitle.value = data.hero.subtitle.value
    heroDescription.value = data.hero.description.value

    bodyContent.value = data.body.content_json as EditorJSData | null

    footerAboutContent.value = data.footer.about.content_json as EditorJSData | null

    contactEmail.value = data.footer.contact.email || ''
    contactPhone.value = data.footer.contact.phone || ''
    contactAddress.value = data.footer.contact.address || ''

    resources.value = data.footer.resources
  } catch {
    // silently fail
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

// --- Hero actions ---
async function saveHero() {
  heroSaving.value = true
  heroFeedback.value = ''
  try {
    await updateHero({
      title: heroTitle.value,
      subtitle: heroSubtitle.value || undefined,
      description: heroDescription.value || undefined,
    })
    heroFeedback.value = 'Hero section mise à jour avec succès'
  } catch {
    heroFeedback.value = 'Erreur lors de la mise à jour'
  } finally {
    heroSaving.value = false
    setTimeout(() => { heroFeedback.value = '' }, 3000)
  }
}

// --- Body actions ---
async function saveBody() {
  if (!bodyContent.value) return
  bodySaving.value = true
  bodyFeedback.value = ''
  try {
    await updateBody({ content_json: bodyContent.value })
    bodyFeedback.value = 'Corps de page mis à jour avec succès'
  } catch {
    bodyFeedback.value = 'Erreur lors de la mise à jour'
  } finally {
    bodySaving.value = false
    setTimeout(() => { bodyFeedback.value = '' }, 3000)
  }
}

// --- Footer About actions ---
async function saveFooterAbout() {
  if (!footerAboutContent.value) return
  footerAboutSaving.value = true
  footerAboutFeedback.value = ''
  try {
    await updateFooterAbout({ content_json: footerAboutContent.value })
    footerAboutFeedback.value = 'Section À propos mise à jour avec succès'
  } catch {
    footerAboutFeedback.value = 'Erreur lors de la mise à jour'
  } finally {
    footerAboutSaving.value = false
    setTimeout(() => { footerAboutFeedback.value = '' }, 3000)
  }
}

// --- Contact actions ---
async function saveContact() {
  contactSaving.value = true
  contactFeedback.value = ''
  try {
    await updateContact({
      email: contactEmail.value || null,
      phone: contactPhone.value || null,
      address: contactAddress.value || null,
    })
    contactFeedback.value = 'Contact mis à jour avec succès'
  } catch {
    contactFeedback.value = 'Erreur lors de la mise à jour'
  } finally {
    contactSaving.value = false
    setTimeout(() => { contactFeedback.value = '' }, 3000)
  }
}

// --- Resource actions ---
async function addResource() {
  if (!newResourceTitle.value || !newResourceUrl.value) return
  resourceSaving.value = true
  resourceFeedback.value = ''
  try {
    const resource = await createResource({
      title: newResourceTitle.value,
      url: newResourceUrl.value,
      sort_order: resources.value.length,
    })
    resources.value.push(resource)
    newResourceTitle.value = ''
    newResourceUrl.value = ''
    resourceFeedback.value = 'Ressource ajoutée'
  } catch {
    resourceFeedback.value = 'Erreur lors de l\'ajout'
  } finally {
    resourceSaving.value = false
    setTimeout(() => { resourceFeedback.value = '' }, 3000)
  }
}

function startEditResource(resource: ResourceLinkAdmin) {
  editingResource.value = resource.id
  editResourceTitle.value = resource.title
  editResourceUrl.value = resource.url
}

async function saveEditResource(id: string) {
  try {
    const updated = await updateResource(id, {
      title: editResourceTitle.value,
      url: editResourceUrl.value,
    })
    const idx = resources.value.findIndex(r => r.id === id)
    if (idx !== -1) resources.value[idx] = updated
    editingResource.value = null
  } catch {
    resourceFeedback.value = 'Erreur lors de la modification'
    setTimeout(() => { resourceFeedback.value = '' }, 3000)
  }
}

async function removeResource(id: string) {
  try {
    await deleteResource(id)
    resources.value = resources.value.filter(r => r.id !== id)
  } catch {
    resourceFeedback.value = 'Erreur lors de la suppression'
    setTimeout(() => { resourceFeedback.value = '' }, 3000)
  }
}

async function moveResource(index: number, direction: 'up' | 'down') {
  const newIndex = direction === 'up' ? index - 1 : index + 1
  if (newIndex < 0 || newIndex >= resources.value.length) return

  const temp = resources.value[index]
  resources.value[index] = resources.value[newIndex]
  resources.value[newIndex] = temp

  try {
    await reorderResources({
      order: resources.value.map(r => r.id),
    })
  } catch {
    // revert on error
    await loadData()
  }
}

const tabs = [
  { key: 'hero' as const, label: 'Hero Section', icon: 'image' },
  { key: 'body' as const, label: 'Corps de page', icon: 'file-lines' },
  { key: 'footer' as const, label: 'Footer', icon: 'bars' },
]
</script>

<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div>
      <h1 class="text-2xl font-bold text-[var(--text-primary)]">Éditoriaux</h1>
      <p class="text-sm text-[var(--text-secondary)] mt-1">
        Gérez le contenu de la page d'accueil et du footer
      </p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <font-awesome-icon icon="spinner" class="animate-spin text-2xl text-[var(--text-muted)]" />
    </div>

    <template v-else>
      <!-- Tabs -->
      <div class="border-b border-[var(--border-default)]">
        <nav class="flex gap-1 -mb-px">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="px-4 py-2.5 text-sm font-medium border-b-2 transition-colors cursor-pointer"
            :class="activeTab === tab.key
              ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
              : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--border-default)]'"
            @click="activeTab = tab.key"
          >
            <font-awesome-icon :icon="['fas', tab.icon]" class="mr-2" />
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- Hero Section Tab -->
      <div v-if="activeTab === 'hero'" class="bg-[var(--bg-card)] rounded-[var(--radius-lg)] border border-[var(--border-default)] p-6 space-y-5">
        <h2 class="text-lg font-semibold text-[var(--text-primary)]">Hero Section</h2>
        <p class="text-sm text-[var(--text-secondary)]">
          Modifiez le titre, sous-titre et description affichés sur la page d'accueil.
        </p>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-[var(--text-primary)] mb-1">Titre *</label>
            <input
              v-model="heroTitle"
              type="text"
              maxlength="255"
              class="w-full px-3 py-2 rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--bg-input)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
              placeholder="Titre principal"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-[var(--text-primary)] mb-1">Sous-titre</label>
            <input
              v-model="heroSubtitle"
              type="text"
              maxlength="255"
              class="w-full px-3 py-2 rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--bg-input)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
              placeholder="Sous-titre"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-[var(--text-primary)] mb-1">Description</label>
            <textarea
              v-model="heroDescription"
              maxlength="500"
              rows="3"
              class="w-full px-3 py-2 rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--bg-input)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent resize-none"
              placeholder="Description"
            />
          </div>
        </div>

        <div class="flex items-center gap-3">
          <button
            class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-[var(--radius-md)] text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50 cursor-pointer"
            :disabled="heroSaving || !heroTitle.trim()"
            @click="saveHero"
          >
            <font-awesome-icon v-if="heroSaving" icon="spinner" class="animate-spin mr-2" />
            Enregistrer
          </button>
          <span v-if="heroFeedback" class="text-sm" :class="heroFeedback.includes('succès') ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
            {{ heroFeedback }}
          </span>
        </div>
      </div>

      <!-- Body Tab -->
      <div v-if="activeTab === 'body'" class="bg-[var(--bg-card)] rounded-[var(--radius-lg)] border border-[var(--border-default)] p-6 space-y-5">
        <h2 class="text-lg font-semibold text-[var(--text-primary)]">Corps de page</h2>
        <p class="text-sm text-[var(--text-secondary)]">
          Contenu riche affiché sous la hero section de la page d'accueil.
        </p>

        <ClientOnly>
          <RichContentEditor v-model="bodyContent" />
        </ClientOnly>

        <div class="flex items-center gap-3">
          <button
            class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-[var(--radius-md)] text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50 cursor-pointer"
            :disabled="bodySaving"
            @click="saveBody"
          >
            <font-awesome-icon v-if="bodySaving" icon="spinner" class="animate-spin mr-2" />
            Enregistrer
          </button>
          <span v-if="bodyFeedback" class="text-sm" :class="bodyFeedback.includes('succès') ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
            {{ bodyFeedback }}
          </span>
        </div>
      </div>

      <!-- Footer Tab -->
      <div v-if="activeTab === 'footer'" class="space-y-6">
        <!-- About Section -->
        <div class="bg-[var(--bg-card)] rounded-[var(--radius-lg)] border border-[var(--border-default)] p-6 space-y-5">
          <h2 class="text-lg font-semibold text-[var(--text-primary)]">À propos</h2>
          <p class="text-sm text-[var(--text-secondary)]">
            Contenu riche de la section "À propos" du footer.
          </p>

          <ClientOnly>
            <RichContentEditor v-model="footerAboutContent" />
          </ClientOnly>

          <div class="flex items-center gap-3">
            <button
              class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-[var(--radius-md)] text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50 cursor-pointer"
              :disabled="footerAboutSaving"
              @click="saveFooterAbout"
            >
              <font-awesome-icon v-if="footerAboutSaving" icon="spinner" class="animate-spin mr-2" />
              Enregistrer
            </button>
            <span v-if="footerAboutFeedback" class="text-sm" :class="footerAboutFeedback.includes('succès') ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
              {{ footerAboutFeedback }}
            </span>
          </div>
        </div>

        <!-- Contact Section -->
        <div class="bg-[var(--bg-card)] rounded-[var(--radius-lg)] border border-[var(--border-default)] p-6 space-y-5">
          <h2 class="text-lg font-semibold text-[var(--text-primary)]">Contact</h2>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-[var(--text-primary)] mb-1">Email</label>
              <input
                v-model="contactEmail"
                type="email"
                class="w-full px-3 py-2 rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--bg-input)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                placeholder="contact@example.com"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-[var(--text-primary)] mb-1">Téléphone</label>
              <input
                v-model="contactPhone"
                type="text"
                maxlength="50"
                class="w-full px-3 py-2 rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--bg-input)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                placeholder="+261 20 22 123 45"
              />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-[var(--text-primary)] mb-1">Adresse</label>
            <textarea
              v-model="contactAddress"
              rows="2"
              maxlength="500"
              class="w-full px-3 py-2 rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--bg-input)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent resize-none"
              placeholder="Adresse postale"
            />
          </div>

          <div class="flex items-center gap-3">
            <button
              class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-[var(--radius-md)] text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50 cursor-pointer"
              :disabled="contactSaving"
              @click="saveContact"
            >
              <font-awesome-icon v-if="contactSaving" icon="spinner" class="animate-spin mr-2" />
              Enregistrer
            </button>
            <span v-if="contactFeedback" class="text-sm" :class="contactFeedback.includes('succès') ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
              {{ contactFeedback }}
            </span>
          </div>
        </div>

        <!-- Resources Section -->
        <div class="bg-[var(--bg-card)] rounded-[var(--radius-lg)] border border-[var(--border-default)] p-6 space-y-5">
          <h2 class="text-lg font-semibold text-[var(--text-primary)]">Ressources</h2>
          <p class="text-sm text-[var(--text-secondary)]">
            Liste de liens affichés dans la section "Ressources" du footer.
          </p>

          <!-- Resource list -->
          <div v-if="resources.length" class="space-y-2">
            <div
              v-for="(resource, index) in resources"
              :key="resource.id"
              class="flex items-center gap-3 p-3 rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--bg-surface)]"
            >
              <!-- Reorder buttons -->
              <div class="flex flex-col gap-0.5">
                <button
                  class="p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)] disabled:opacity-30 cursor-pointer"
                  :disabled="index === 0"
                  @click="moveResource(index, 'up')"
                >
                  <font-awesome-icon icon="chevron-up" class="text-xs" />
                </button>
                <button
                  class="p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)] disabled:opacity-30 cursor-pointer"
                  :disabled="index === resources.length - 1"
                  @click="moveResource(index, 'down')"
                >
                  <font-awesome-icon icon="chevron-down" class="text-xs" />
                </button>
              </div>

              <!-- Edit mode -->
              <template v-if="editingResource === resource.id">
                <div class="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <input
                    v-model="editResourceTitle"
                    type="text"
                    class="px-2 py-1 rounded border border-[var(--border-default)] bg-[var(--bg-input)] text-[var(--text-primary)] text-sm"
                    placeholder="Titre"
                  />
                  <input
                    v-model="editResourceUrl"
                    type="text"
                    class="px-2 py-1 rounded border border-[var(--border-default)] bg-[var(--bg-input)] text-[var(--text-primary)] text-sm"
                    placeholder="URL"
                  />
                </div>
                <button
                  class="p-1.5 text-green-600 dark:text-green-400 hover:opacity-80 cursor-pointer"
                  @click="saveEditResource(resource.id)"
                >
                  <font-awesome-icon icon="check" />
                </button>
                <button
                  class="p-1.5 text-[var(--text-muted)] hover:opacity-80 cursor-pointer"
                  @click="editingResource = null"
                >
                  <font-awesome-icon icon="xmark" />
                </button>
              </template>

              <!-- Display mode -->
              <template v-else>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-[var(--text-primary)] truncate">{{ resource.title }}</p>
                  <p class="text-xs text-[var(--text-muted)] truncate">{{ resource.url }}</p>
                </div>
                <button
                  class="p-1.5 text-[var(--text-secondary)] hover:text-[var(--color-primary)] cursor-pointer"
                  @click="startEditResource(resource)"
                >
                  <font-awesome-icon icon="pen" class="text-sm" />
                </button>
                <button
                  class="p-1.5 text-[var(--text-secondary)] hover:text-red-600 dark:hover:text-red-400 cursor-pointer"
                  @click="removeResource(resource.id)"
                >
                  <font-awesome-icon icon="trash" class="text-sm" />
                </button>
              </template>
            </div>
          </div>

          <p v-else class="text-sm text-[var(--text-muted)] italic">Aucune ressource pour le moment.</p>

          <!-- Add new resource -->
          <div class="border-t border-[var(--border-default)] pt-4">
            <h3 class="text-sm font-medium text-[var(--text-primary)] mb-3">Ajouter une ressource</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <input
                v-model="newResourceTitle"
                type="text"
                maxlength="255"
                class="px-3 py-2 rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--bg-input)] text-[var(--text-primary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                placeholder="Titre du lien"
              />
              <input
                v-model="newResourceUrl"
                type="text"
                maxlength="500"
                class="px-3 py-2 rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--bg-input)] text-[var(--text-primary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                placeholder="URL (https://...)"
              />
            </div>
            <div class="flex items-center gap-3 mt-3">
              <button
                class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-[var(--radius-md)] text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50 cursor-pointer"
                :disabled="resourceSaving || !newResourceTitle.trim() || !newResourceUrl.trim()"
                @click="addResource"
              >
                <font-awesome-icon v-if="resourceSaving" icon="spinner" class="animate-spin mr-2" />
                <font-awesome-icon v-else icon="plus" class="mr-2" />
                Ajouter
              </button>
              <span v-if="resourceFeedback" class="text-sm" :class="resourceFeedback.includes('ajoutée') ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
                {{ resourceFeedback }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
