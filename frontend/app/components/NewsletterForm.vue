<script setup lang="ts">
const { loading, error, success, subscribe, reset } = useNewsletter()
const email = ref('')

async function handleSubmit() {
  if (!email.value) return
  await subscribe(email.value)
  if (success.value) {
    email.value = ''
  }
}
</script>

<template>
  <div>
    <form v-if="!success" class="flex gap-2" @submit.prevent="handleSubmit">
      <input
        v-model="email"
        type="email"
        placeholder="Votre email"
        required
        class="flex-1 px-3 py-2 text-sm rounded-lg border border-(--border-default) outline-none transition-colors focus:ring-2 focus:ring-(--color-primary)/20 focus:border-(--border-focus)"
        :style="{ backgroundColor: 'var(--bg-input)', color: 'var(--text-primary)' }"
      />
      <UiButton type="submit" :loading="loading">
        S'inscrire
      </UiButton>
    </form>

    <UiAlert v-if="error" variant="error" class="mt-2">
      {{ error }}
    </UiAlert>

    <div v-if="success" class="text-sm text-(--color-success)">
      <p>Un email de confirmation a ete envoye.</p>
      <button
        class="mt-1 text-xs text-(--text-muted) underline cursor-pointer"
        @click="reset"
      >
        Inscrire une autre adresse
      </button>
    </div>
  </div>
</template>
