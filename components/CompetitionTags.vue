<template>
  <div class="tags">
    <span
      :title="kind[competition.kind].title"
      :class="['tag', kind[competition.kind].type]"
      >{{ competition.kind }}</span
    >
    <span class="tag">
      {{ flag(competition.location.country_code) }}
      {{ competition.location.city }}</span
    >
    <ParticipantCounter
      v-if="competition.has_registration_open"
      :competition="competition"
    />
    <SingleboerseCounter
      v-if="singleboerse[competition.id]"
      :id="singleboerse[competition.id]"
    />

    <span
      v-if="competition.date.is_canceled"
      class="tag"
      style="cursor: help"
      title="Diese Veranstaltung wurde abgesagt"
      >❌
    </span>
    <span
      v-if="competition.date.is_draft"
      class="tag"
      style="cursor: help"
      title="Der Termin dieser Veranstaltung ist noch nicht endgültig"
      >❓</span
    >
  </div>
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

const singleboerse = {
  recyC5LmxecehTxWD: "240511-schonach",
  reckHSB1eG9Su8fxx: "240907-radebeul",
};

const flag = (countryCode) =>
  countryCode
    .toUpperCase()
    .replace(/./g, (char) => String.fromCodePoint(127397 + char.charCodeAt()));
</script>
