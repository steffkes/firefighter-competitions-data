<template>
  <span
    ><time :datetime="competition.date.start">
      {{ formatDate(competition.date.start) }}
    </time>
  </span>

  <span
    v-if="
      formatDate(competition.date.start) != formatDate(competition.date.end)
    "
    style="white-space: nowrap"
  >
    -
    <time :datetime="competition.date.end">{{
      formatDate(competition.date.end)
    }}</time>
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
