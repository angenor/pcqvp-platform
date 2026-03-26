<script setup lang="ts">
definePageMeta({
  layout: false,
})

const { login } = useAuth()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await login(email.value, password.value)
    navigateTo('/admin')
  } catch (e: any) {
    const status = e?.response?.status || e?.statusCode
    if (status === 423) {
      error.value = 'Compte temporairement verrouille. Reessayez plus tard.'
    } else {
      error.value = 'Email ou mot de passe incorrect.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div
    class="min-h-screen flex items-center justify-center px-4"
    :style="{ backgroundColor: 'var(--bg-page)' }"
  >
    <div class="w-full max-w-sm">
      <h1 class="text-2xl font-bold text-center mb-8" :style="{ color: 'var(--text-primary)' }">
        PCQVP - Connexion
      </h1>

      <form
        class="p-6 space-y-4 border border-[var(--border-default)]"
        :style="{
          backgroundColor: 'var(--bg-card)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-md)',
        }"
        @submit.prevent="handleSubmit"
      >
        <UiAlert v-if="error" variant="error" dismissible @dismiss="error = ''">
          {{ error }}
        </UiAlert>

        <div>
          <label for="email" class="block text-sm font-medium mb-1" :style="{ color: 'var(--text-secondary)' }">
            Email
          </label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            autocomplete="email"
            class="w-full px-3 py-2 border rounded-[var(--radius-md)] text-sm transition-colors focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent outline-none"
            :style="{
              backgroundColor: 'var(--bg-input)',
              borderColor: 'var(--border-default)',
              color: 'var(--text-primary)',
            }"
          />
        </div>

        <div>
          <label for="password" class="block text-sm font-medium mb-1" :style="{ color: 'var(--text-secondary)' }">
            Mot de passe
          </label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
            class="w-full px-3 py-2 border rounded-[var(--radius-md)] text-sm transition-colors focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent outline-none"
            :style="{
              backgroundColor: 'var(--bg-input)',
              borderColor: 'var(--border-default)',
              color: 'var(--text-primary)',
            }"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-2.5 px-4 text-white font-semibold rounded-[var(--radius-md)] transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          :style="{ backgroundColor: 'var(--color-primary)' }"
        >
          <UiLoadingSpinner v-if="loading" size="sm" color="white" />
          {{ loading ? 'Connexion...' : 'Se connecter' }}
        </button>
      </form>
    </div>
  </div>
</template>
