<template>
  <l-marker
    :id="competition.id"
    :lat-lng="[
      competition.location.coordinates.lat,
      competition.location.coordinates.lng,
    ]"
  >
    <l-popup>
      <component :is="competition.date.is_canceled ? 's' : 'div'">
        <div class="m-0 has-text-grey-light" style="white-space: nowrap">
          <CompetitionDate :competition="competition" />

          <span
            class="tag is-success ml-2"
            v-if="competition.has_registration_pending"
            style="cursor: help"
            :title="
              'Anmeldung startet am ' +
              formatDate(competition.date.registration_opens)
            "
          >
            ⏰
            <FormattedDate
              :date="competition.date.registration_opens"
              class="ml-1"
            />
          </span>
        </div>

        <p class="m-0 my-2">
          <a v-if="competition.url" :href="competition.url" class="is-block">{{
            competition.name
          }}</a>
          <span v-else>{{ competition.name }}</span>
        </p>
        <CompetitionTags :competition="competition" />
      </component>
    </l-popup>
  </l-marker>
</template>

<script setup>
defineProps(["competition"]);

import { LMarker, LPopup } from "@vue-leaflet/vue-leaflet";

const formatDate = (date) =>
  new Date(date).toLocaleDateString("de-DE", {
    weekday: "short",
    month: "2-digit",
    day: "2-digit",
    year: "2-digit",
  });
</script>
