<template>
  <div class="container">
    <nav class="navbar" role="navigation" aria-label="main navigation">
      <div class="navbar-brand">
        <a class="navbar-item" href="/"> 👨‍🚒 </a>

        <a
          role="button"
          class="navbar-burger"
          :class="{ 'is-active': activeNavbar }"
          aria-label="menu"
          aria-expanded="false"
          @click="activeNavbar = !activeNavbar"
        >
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
        </a>
      </div>

      <div class="navbar-menu" :class="{ 'is-active': activeNavbar }">
        <div class="navbar-start">
          <a
            class="navbar-item"
            :class="[kind.FCC.type, { 'is-light': !competitionFilter.FCC }]"
          >
            <label class="checkbox" :title="kind.FCC.title">
              <input type="checkbox" v-model="competitionFilter.FCC" />
              FCC
            </label>
          </a>

          <a
            class="navbar-item"
            :class="[kind.FSR.type, { 'is-light': !competitionFilter.FSR }]"
          >
            <label class="checkbox" :title="kind.FSR.title">
              <input type="checkbox" v-model="competitionFilter.FSR" />
              FSR
            </label>
          </a>

          <a class="navbar-item">
            <label class="checkbox">
              <input type="checkbox" v-model="displayPastCompetitions" />
              Zeige vergangene Wettkämpfe an
            </label>
          </a>
        </div>

        <div class="navbar-end">
          <div class="navbar-item">
            <div class="buttons">
              <a :href="calendarPath" class="button is-primary">
                🗓️ Wettkämpfe für deinen Kalendar
              </a>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <div class="columns">
      <div class="column">
        <table class="table is-fullwidth is-striped is-hoverable">
          <thead>
            <tr>
              <th class="date">Datum</th>
              <th>Art / Ort / Wettkampf</th>
            </tr>
          </thead>
          <tfoot>
            <tr>
              <th class="date">Datum</th>
              <th>Art / Ort / Wettkampf</th>
            </tr>
          </tfoot>
          <tbody>
            <tr
              v-for="competition in filteredCompetitions"
              @click="highlight(competition)"
              :id="competition.id"
              :class="{
                'has-text-grey-lighter': isPast(competition),
                'has-text-grey-light': competition.date.is_draft,
                'has-text-weight-light': competition.date.is_draft,
              }"
            >
              <td class="date">
                <span
                  v-if="competition.date.is_draft"
                  style="cursor: help"
                  title="Der Termin dieser Veranstaltung ist noch nicht endgültig"
                  >❓</span
                >
                {{ formatDate(competition.date.start) }}
                <span
                  v-if="
                    formatDate(competition.date.start) !=
                    formatDate(competition.date.end)
                  "
                  style="white-space: nowrap"
                  >- {{ formatDate(competition.date.end) }}</span
                >
              </td>
              <td>
                <a
                  v-if="competition.url"
                  :href="competition.url"
                  style="display: block"
                  >{{ competition.name }}</a
                >
                <div v-else>{{ competition.name }}</div>
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
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="column">
        <ClientOnly>
          <div style="height: 100vh; width: 100%">
            <l-map
              :use-global-leaflet="false"
              v-model:zoom="zoom"
              :center="center"
            >
              <l-tile-layer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              ></l-tile-layer>

              <l-marker
                v-for="competition in filteredCompetitions.filter(
                  ({ location: { coordinates } }) => coordinates
                )"
                :id="competition.id"
                :lat-lng="[
                  competition.location.coordinates.lat,
                  competition.location.coordinates.lng,
                ]"
              >
                <l-popup>
                  {{ formatDate(competition.date.start) }}
                  <span
                    v-if="
                      formatDate(competition.date.start) !=
                      formatDate(competition.date.end)
                    "
                    style="white-space: nowrap"
                    >- {{ formatDate(competition.date.end) }}</span
                  >
                  <a
                    v-if="competition.url"
                    :href="competition.url"
                    style="display: block"
                    >{{ competition.name }}</a
                  >
                  <div v-else>{{ competition.name }}</div>
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
                  </div>
                </l-popup>
              </l-marker>
            </l-map>
          </div>
        </ClientOnly>
      </div>
    </div>
  </div>
</template>

<style scoped>
table th.date,
table td.date {
  text-align: right !important;
  font-variant-numeric: tabular-nums;
}

tr:target {
  background-color: #00d1b2 !important;
  color: #fff;
}
</style>

<script setup>
const displayPastCompetitions = ref(false);
const competitionFilter = ref({
  FCC: true,
  FSR: true,
});
const kind = {
  FCC: {
    title: "Firefighter Combat Challenge",
    type: "is-warning",
  },
  FSR: {
    title: "Firefighter Stair Run",
    type: "is-info",
  },
};

const isPast = (competition) => new Date() - new Date(competition.date.end) > 0;

const { data: competitions } = await useFetch("/api/competitions");

const filteredCompetitions = computed(() => {
  let filteredCompetitions = competitions.value;
  if (!displayPastCompetitions.value) {
    filteredCompetitions = filteredCompetitions.filter(
      (competition) => !isPast(competition)
    );
  }

  if (!competitionFilter.value.FSR) {
    filteredCompetitions = filteredCompetitions.filter(
      ({ kind }) => kind != "FSR"
    );
  }

  if (!competitionFilter.value.FCC) {
    filteredCompetitions = filteredCompetitions.filter(
      ({ kind }) => kind != "FCC"
    );
  }

  return filteredCompetitions;
});

const formatDate = (date) =>
  new Date(date).toLocaleDateString("de-DE", {
    weekday: "short",
    year: "2-digit",
    month: "2-digit",
    day: "2-digit",
  });

const flag = (countryCode) =>
  countryCode
    .toUpperCase()
    .replace(/./g, (char) => String.fromCodePoint(127397 + char.charCodeAt()));

const calendarPath = computed(
  () =>
    Object.keys(kind)
      .filter((kind) => competitionFilter.value[kind])
      .join("-")
      .toLowerCase() + ".ics"
);

const highlight = (competition) => {
  window.location.hash = "#" + competition.id;
};

useHead({
  title: "Feuerwehr Wettkämpfe",
  viewport: "width=device-width, initial-scale=1, maximum-scale=1",
  charset: "utf-8",
});

import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet";
import "leaflet/dist/leaflet.css";

const zoom = ref(5);
const center = ref([47.3749871, 10.270242]);
const activeNavbar = ref(false);
</script>
