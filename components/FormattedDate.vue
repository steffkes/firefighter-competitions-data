<template>
  <time :datetime="date">
    {{ formatDate(date) }}
  </time>
</template>

<script setup>
defineProps(["date"]);

const formatDate = (date) =>
  new Date(date).toLocaleDateString("de-DE", {
    weekday: "short",
    month: "2-digit",
    day: "2-digit",
    year: "2-digit",
  });
</script>
