<template>
  <span
    v-if="count"
    class="tag"
    :title="'bislang ' + count + ' Anmeldungen'"
    style="cursor: help"
    >👨‍🚒 {{ count }}</span
  >
</template>

<script setup>
const { competition } = defineProps(["competition"]);
const count = computed(() => competition.participants.count);
</script>
