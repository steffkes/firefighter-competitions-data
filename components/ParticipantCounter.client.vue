<template>
  <span
    v-if="count != null"
    class="tag"
    :title="'bislang ' + count + ' Anmeldungen'"
    style="cursor: help"
    >👨‍🚒 {{ count }}</span
  >
</template>

<script setup>
const { competition } = defineProps(["competition"]);
const { data: count } = await useFetch(
  "/api/competitions/" + competition.id + ".json"
);
</script>
