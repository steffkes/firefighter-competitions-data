<template>
  <span class="tag">
    {{ flag(competition.location.country_code) }}
    {{ competition.location.city }}</span
  >
</template>

<script setup>
defineProps(["competition"]);

const flag = (countryCode) =>
  countryCode
    .toUpperCase()
    .replace(/./g, (char) => String.fromCodePoint(127397 + char.charCodeAt()));
</script>
