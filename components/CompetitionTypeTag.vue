<template>
  <span
    :title="kind[competition.kind].title"
    :class="['tag', kind[competition.kind].type]"
    >{{ competition.kind }}</span
  >
</template>

<script setup>
defineProps(["competition"]);

const kind = {
  FCC: {
    title: "Firefighter Combat Challenge",
    type: "is-warning is-light",
  },
  FSR: {
    title: "Firefighter Stair Run",
    type: "is-info is-light",
  },
};
</script>
