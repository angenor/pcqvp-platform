<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: 'auth',
})

const { apiFetch } = useApi()

interface UserItem {
  id: string
  email: string
  role: string
  is_active: boolean
  created_at: string
}

const users = ref<UserItem[]>([])
const loading = ref(true)
const error = ref('')

async function loadUsers() {
  loading.value = true
  error.value = ''
  try {
    users.value = await apiFetch<UserItem[]>('/api/admin/users')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Erreur lors du chargement des utilisateurs'
  } finally {
    loading.value = false
  }
}

async function toggleActive(user: UserItem) {
  try {
    await apiFetch(`/api/admin/users/${user.id}`, {
      method: 'PUT',
      params: { is_active: !user.is_active },
    })
    await loadUsers()
  } catch (e: any) {
    error.value = e?.data?.detail || 'Erreur lors de la mise a jour'
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

onMounted(loadUsers)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        Utilisateurs
      </h1>
    </div>

    <div v-if="error" class="mb-4 p-3 rounded-md bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm">
      {{ error }}
    </div>

    <div v-if="loading" class="text-gray-500 dark:text-gray-400">
      Chargement...
    </div>

    <div v-else class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-700">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              Email
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              Role
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              Statut
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              Date de creation
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-for="u in users" :key="u.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
              {{ u.email }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="u.role === 'admin'
                  ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300'
                  : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300'"
              >
                {{ u.role }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="u.is_active
                  ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
                  : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'"
              >
                {{ u.is_active ? 'Actif' : 'Inactif' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
              {{ formatDate(u.created_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <button
                class="text-sm font-medium transition-colors"
                :class="u.is_active
                  ? 'text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300'
                  : 'text-green-600 dark:text-green-400 hover:text-green-800 dark:hover:text-green-300'"
                @click="toggleActive(u)"
              >
                {{ u.is_active ? 'Desactiver' : 'Activer' }}
              </button>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="5" class="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
              Aucun utilisateur trouve.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
