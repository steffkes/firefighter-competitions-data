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

import { formatDate } from "../util";
</script>
