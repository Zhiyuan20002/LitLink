<script setup lang="ts">
import PaperPage from './components/PaperPage.vue'

</script>

<template>
  <a-config-provider
      :theme="{
      token: {
        colorPrimary: '#556B2F',
      },
    }"
  >
    <PaperPage/>
  </a-config-provider>
</template>

<style scoped>

</style>
