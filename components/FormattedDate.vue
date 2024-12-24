<template>
  <time :datetime="date">
    {{ formatDate(date) }}
  </time>
</template>

<script setup>
import { formatDate } from "../util";

defineProps(["date"]);
</script>
