<script setup lang="ts">
import type { RichContentBlock } from '~/types/geography'

defineProps<{
  descriptionJson: RichContentBlock[]
}>()

const brokenImages = ref(new Set<number>())

function handleImageError(index: number) {
  brokenImages.value = new Set([...brokenImages.value, index])
}
</script>

<template>
  <div class="space-y-4">
    <template v-for="(block, index) in descriptionJson" :key="index">
      <h2 v-if="block.type === 'heading'" class="text-xl font-bold text-gray-900 dark:text-white">
        {{ block.content }}
      </h2>
      <p v-else-if="block.type === 'paragraph'" class="text-gray-700 dark:text-gray-300 leading-relaxed">
        {{ block.content }}
      </p>
      <div v-else-if="block.type === 'image'" class="my-2">
        <img
          v-if="block.url && !brokenImages.has(index)"
          :src="block.url"
          :alt="block.alt || ''"
          class="max-w-full rounded-lg"
          @error="handleImageError(index)"
        />
        <div v-else class="w-full h-48 bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center text-gray-500 dark:text-gray-400">
          Image non disponible
        </div>
      </div>
    </template>
    <p v-if="!descriptionJson?.length" class="text-gray-500 dark:text-gray-400 italic">
      Aucune description disponible.
    </p>
  </div>
</template>
