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
        class="flex-1 px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
      />
      <button
        type="submit"
        :disabled="loading"
        class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg disabled:opacity-50 transition-colors"
      >
        <span v-if="loading">...</span>
        <span v-else>S'inscrire</span>
      </button>
    </form>

    <p v-if="error" class="mt-2 text-sm text-red-600 dark:text-red-400">
      {{ error }}
    </p>

    <div v-if="success" class="text-sm text-green-600 dark:text-green-400">
      <p>Un email de confirmation a ete envoye.</p>
      <button
        class="mt-1 text-xs text-gray-500 dark:text-gray-400 underline"
        @click="reset"
      >
        Inscrire une autre adresse
      </button>
    </div>
  </div>
</template>
