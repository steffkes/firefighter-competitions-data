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
  "/api/competitions/" +
    competition.date.start.substr(2, 8).replaceAll("-", "") +
    "_" +
    competition.id +
    ".json"
);
</script>
