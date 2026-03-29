<script setup lang="ts">
defineProps<{
  name: string
  type: string
  bannerImage: string
}>()

const typeLabels: Record<string, string> = {
  province: 'Province',
  region: 'Region',
  commune: 'Commune',
}
</script>

<template>
  <div class="relative w-full h-[250px] md:h-[300px]">
    <img
      :src="bannerImage"
      :alt="`Banniere de ${name}`"
      class="absolute inset-0 w-full h-full object-cover"
    />
    <div class="absolute inset-0 bg-linear-to-t from-black/70 via-black/30 to-transparent" />
    <div class="relative h-full flex flex-col items-end justify-center text-center px-4 pb-8">
      <div class="w-full">
        <p class="text-sm text-white/80 mb-1">
          {{ typeLabels[type] || type }}
        </p>
        <h1 class="text-3xl md:text-4xl lg:text-5xl font-bold text-white!">
          {{ name }}
        </h1>
      </div>
    </div>
  </div>
</template>
