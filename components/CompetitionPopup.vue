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
        <p class="m-0 has-text-grey-light">
          {{ formatDate(competition.date.start) }}
          <span
            v-if="
              formatDate(competition.date.start) !=
              formatDate(competition.date.end)
            "
            style="white-space: nowrap"
            >- {{ formatDate(competition.date.end) }}</span
          >

          <span
            class="tag is-success"
            v-if="competition.has_registration_pending"
            style="cursor: help"
            :title="
              'Anmeldung startet am ' +
              formatDate(competition.date.registration_opens)
            "
          >
            ⏰ {{ formatDate(competition.date.registration_opens) }}
          </span>

          <span
            v-if="competition.date.is_canceled"
            style="cursor: help"
            title="Diese Veranstaltung wurde abgesagt"
            >❌
          </span>
          <span
            v-if="competition.date.is_draft"
            style="cursor: help"
            title="Der Termin dieser Veranstaltung ist noch nicht endgültig"
            >❓</span
          >
        </p>

        <p class="m-0 my-2">
          <a v-if="competition.url" :href="competition.url" class="is-block">{{
            competition.name
          }}</a>
          <span v-else>{{ competition.name }}</span>
        </p>
        <div class="tags">
          <CompetitionTypeTag :competition="competition" />
          <LocationTag :competition="competition" />
          <ParticipantCounter
            v-if="competition.has_registration_open"
            :competition="competition"
          />
        </div>
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
