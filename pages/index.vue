<template>
  <div class="modal" :class="{ 'is-active': activeModal }">
    <div class="modal-background"></div>
    <div class="modal-content">
      <img src="/qr-code.svg" />
    </div>
    <button
      class="modal-close is-large"
      aria-label="close"
      @click="activeModal = false"
    ></button>
  </div>

  <div class="container">
    <nav class="navbar" role="navigation" aria-label="main navigation">
      <div class="navbar-brand">
        <a class="navbar-item" href="/"> 👨‍🚒 </a>

        <a class="navbar-item is-hidden-desktop" @click="activeModal = true"
          ><img src="/qr-code.svg" style="opacity: 0.1"
        /></a>

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

        <div v-if="filteredCompetitions.length" class="navbar-end">
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
        <ExplainerBox />

        <table
          v-if="upcomingRegistrations.length"
          class="table is-fullwidth is-striped is-hoverable mb-6"
        >
          <thead>
            <tr>
              <th></th>
              <th>
                Anmeldung bei diesen Wettkämpfen öffnet innerhalb der nächsten
                vier Wochen
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="competition in upcomingRegistrations"
              :key="competition.id"
              :id="competition.id"
              :class="{
                'has-text-grey-lighter': isPast(competition),
                'has-text-grey-light': competition.date.is_draft,
                'has-text-weight-light': competition.date.is_draft,
                'has-text-grey-lighter': competition.date.is_canceled,
                'is-selected': isCurrent(competition),
              }"
            >
              <td class="date">
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
                <component :is="competition.date.is_canceled ? 's' : 'span'">
                  {{ formatDate(competition.date.start) }}
                  <span
                    v-if="
                      formatDate(competition.date.start) !=
                      formatDate(competition.date.end)
                    "
                    style="white-space: nowrap"
                    >- {{ formatDate(competition.date.end) }}</span
                  >
                </component>
                <p>
                  <span
                    :class="{
                      tag: true,
                      'is-success':
                        formatDate(competition.date.registration_opens) !=
                        formatDate(new Date()),
                      'is-dark':
                        formatDate(competition.date.registration_opens) ==
                        formatDate(new Date()),
                    }"
                    v-if="competition.has_registration_pending"
                    style="cursor: help"
                    :title="
                      'Anmeldung startet am ' +
                      formatDate(competition.date.registration_opens)
                    "
                  >
                    ⏰ {{ formatDate(competition.date.registration_opens) }}
                  </span>
                </p>
              </td>
              <td>
                <component :is="competition.date.is_canceled ? 's' : 'div'">
                  <a
                    v-if="competition.url"
                    class="is-block"
                    :href="competition.url"
                    >{{ competition.name }}</a
                  >
                  <div v-else>{{ competition.name }}</div>
                </component>
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
                  <ParticipantCounter :competition="competition" />
                  <SingleboerseCounter
                    v-if="singleboerse[competition.id]"
                    :id="singleboerse[competition.id]"
                  />
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <table class="table is-fullwidth is-striped is-hoverable">
          <thead>
            <tr>
              <th class="date">Datum</th>
              <th>Wettkampf / Art / Ort</th>
            </tr>
          </thead>
          <tfoot>
            <tr>
              <th class="date">Datum</th>
              <th>Wettkampf / Art / Ort</th>
            </tr>
          </tfoot>
          <tbody>
            <tr v-if="!filteredCompetitions.length" class="has-text-grey-light">
              <td colspan="2">
                Mit der getroffenen Auswahl gibt es keine Wettkämpfe.
              </td>
            </tr>
            <tr
              v-for="competition in filteredCompetitions"
              :key="competition.id"
              :id="competition.id"
              :class="{
                'has-text-grey-lighter': isPast(competition),
                'has-text-grey-light': competition.date.is_draft,
                'has-text-weight-light': competition.date.is_draft,
                'has-text-grey-lighter': competition.date.is_canceled,
                'is-selected': isCurrent(competition),
              }"
            >
              <td class="date">
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
                <component :is="competition.date.is_canceled ? 's' : 'span'">
                  {{ formatDate(competition.date.start) }}
                  <span
                    v-if="
                      formatDate(competition.date.start) !=
                      formatDate(competition.date.end)
                    "
                    style="white-space: nowrap"
                    >- {{ formatDate(competition.date.end) }}</span
                  >
                </component>
                <p>
                  <span
                    :class="{
                      tag: true,
                      'is-success':
                        formatDate(competition.date.registration_opens) !=
                        formatDate(new Date()),
                      'is-dark':
                        formatDate(competition.date.registration_opens) ==
                        formatDate(new Date()),
                    }"
                    v-if="competition.has_registration_pending"
                    style="cursor: help"
                    :title="
                      'Anmeldung startet am ' +
                      formatDate(competition.date.registration_opens)
                    "
                  >
                    ⏰ {{ formatDate(competition.date.registration_opens) }}
                  </span>
                </p>
              </td>
              <td>
                <component :is="competition.date.is_canceled ? 's' : 'div'">
                  <a
                    v-if="competition.url"
                    class="is-block"
                    :href="competition.url"
                    >{{ competition.name }}</a
                  >
                  <div v-else>{{ competition.name }}</div>
                </component>
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
                  <ParticipantCounter :competition="competition" />
                  <SingleboerseCounter
                    v-if="singleboerse[competition.id]"
                    :id="singleboerse[competition.id]"
                  />
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
                      <a
                        v-if="competition.url"
                        :href="competition.url"
                        class="is-block"
                        >{{ competition.name }}</a
                      >
                      <span v-else>{{ competition.name }}</span>
                    </p>
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
                    </div>
                  </component>
                </l-popup>
              </l-marker>
            </l-map>
          </div>
        </ClientOnly>
      </div>
    </div>
  </div>

  <footer class="footer mt-6">
    <div class="content has-text-centered">
      <p>
        Hast du Fragen zum Kalender? Oder weißt von Wettkämpfen die hier noch
        fehlen?<br />
        Melde dich bitte bei <strong>Stefan</strong>:
        <a href="tel:004916097048114">📞 0160 970 48 114</a>&nbsp;
        <a href="mailto:stefan@mathe.is">✉️ stefan@mathe.is</a>
      </p>
    </div>
  </footer>
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

footer a {
  white-space: nowrap;
}

@media screen and (max-width: 1024px) {
  table .date {
    width: 10%;
  }
}
@media screen and (min-width: 1024px) {
  table .date {
    width: 40%;
  }
}
</style>

<style>
.leaflet-popup-content {
  min-width: 200px;
  line-height: initial;
  font-size: initial;
}
</style>

<script setup>
import { differenceInDays, parseISO as parseIsoDate } from "date-fns";

const displayPastCompetitions = ref(false);
const competitionFilter = ref({
  FCC: true,
  FSR: true,
});
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

const getDateFromDate = (date) => date.toISOString().substring(0, 10);

const isPast = (competition) =>
  getDateFromDate(new Date()) > getDateFromDate(new Date(competition.date.end));

const isCurrent = (competition) =>
  getDateFromDate(new Date()) >=
    getDateFromDate(new Date(competition.date.start)) &&
  getDateFromDate(new Date()) <=
    getDateFromDate(new Date(competition.date.end));

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

  filteredCompetitions = filteredCompetitions.map((competition) => {
    return {
      ...competition,
      has_registration_pending:
        competition.date.registration_opens &&
        new Date().toISOString().split("T")[0] <=
          new Date(competition.date.registration_opens)
            .toISOString()
            .split("T")[0],
      has_registration_open:
        new Date().toISOString().split("T")[0] >=
        new Date(competition.date.registration_opens)
          .toISOString()
          .split("T")[0],
    };
  });

  return filteredCompetitions;
});

const upcomingRegistrations = computed(() => {
  return filteredCompetitions.value.filter(
    ({ date: { registration_opens } }) => {
      const diffDays = differenceInDays(
        parseIsoDate(registration_opens),
        new Date()
      );
      return registration_opens && diffDays >= 0 && diffDays < 7 * 4;
    }
  );
});

const formatDate = (date) =>
  new Date(date).toLocaleDateString("de-DE", {
    weekday: "short",
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

useHead({
  title: "Feuerwehr Wettkämpfe",
  viewport: "width=device-width, initial-scale=1, maximum-scale=1",
  charset: "utf-8",
  meta: [
    {
      name: "description",
      content: "Alle Termine deutschlandweit & darüber hinaus.",
    },
    {
      property: "og:image",
      content:
        "https://firefighter-competitions.vercel.app/firefighter-competitions.jpg",
    },
  ],
  script: [
    {
      src: "https://plausible.io/js/script.js",
      "data-domain": "firefighter-competitions.vercel.app",
      defer: true,
    },
  ],
});

import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet";
import "leaflet/dist/leaflet.css";

const zoom = ref(5);
const center = ref([47.3749871, 10.270242]);
const activeNavbar = ref(false);
const activeModal = ref(false);
</script>
