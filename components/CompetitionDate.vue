<template>
  <span><FormattedDate :date="competition.date.start" /></span>

  <span
    v-if="
      formatDate(competition.date.start) != formatDate(competition.date.end)
    "
    style="white-space: nowrap"
  >
    -
    <FormattedDate :date="competition.date.end" />
  </span>
</template>

<script setup>
defineProps(["competition"]);

const formatDate = (date) =>
  new Date(date).toLocaleDateString("de-DE", {
    weekday: "short",
    month: "2-digit",
    day: "2-digit",
    year: "2-digit",
  });
</script>
