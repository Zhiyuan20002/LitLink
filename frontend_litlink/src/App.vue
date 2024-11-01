<script setup lang="ts">
import PaperPage from './components/PaperPage.vue'

</script>

<template>
  <a-config-provider
      :theme="{
      token: {
        colorPrimary: '#5A54F9',
        // #191970
      },
    }"
  >
    <PaperPage/>
  </a-config-provider>
</template>

<style scoped>

</style>
