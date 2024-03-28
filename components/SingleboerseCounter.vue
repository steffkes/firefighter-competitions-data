<template>
  <span
    class="tag is-link"
    :title="'aktuell ' + count + ' Gesuche'"
    style="cursor: help"
    >🤚 {{ count }}</span
  >
</template>

<script setup>
const { id } = defineProps(["id"]);
const { data: count } = await useFetch(
  "https://match-me-if-you-can.vercel.app/api/" + id + ".json"
);
</script>
