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

const columns = [
  { key: 'email', label: 'Email' },
  { key: 'role', label: 'Role' },
  { key: 'status', label: 'Statut' },
  { key: 'created_at', label: 'Date de creation' },
]

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
      <h1 class="text-2xl font-bold text-(--text-primary)">Utilisateurs</h1>
    </div>

    <UiAlert v-if="error" variant="error" class="mb-4">{{ error }}</UiAlert>

    <UiDataTable
      :columns="columns"
      :data="users"
      :loading="loading"
      empty-message="Aucun utilisateur trouve."
      :empty-icon="['fas', 'users']"
    >
      <template #cell-role="{ row }">
        <UiBadge :variant="row.role === 'admin' ? 'primary' : 'info'">
          {{ row.role }}
        </UiBadge>
      </template>
      <template #cell-status="{ row }">
        <UiBadge :variant="row.is_active ? 'success' : 'error'" dot>
          {{ row.is_active ? 'Actif' : 'Inactif' }}
        </UiBadge>
      </template>
      <template #cell-created_at="{ row }">
        <span class="font-mono text-sm">{{ formatDate(row.created_at) }}</span>
      </template>
      <template #actions="{ row }">
        <UiButton
          :variant="row.is_active ? 'ghost' : 'ghost'"
          size="sm"
          :class="row.is_active ? 'text-(--color-error)' : 'text-(--color-success)'"
          @click="toggleActive(row)"
        >
          {{ row.is_active ? 'Desactiver' : 'Activer' }}
        </UiButton>
      </template>
    </UiDataTable>
  </div>
</template>
