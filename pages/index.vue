<template>
  <div>
    <span
      :class="['tag', kind.FCC.type, { 'is-light': !competitionFilter.FCC }]"
    >
      <label class="checkbox" :title="kind.FCC.title">
        <input type="checkbox" v-model="competitionFilter.FCC" />
        FCC
      </label>
    </span>
    <span
      :class="['tag', kind.FSR.type, { 'is-light': !competitionFilter.FSR }]"
    >
      <label class="checkbox" :title="kind.FSR.title">
        <input type="checkbox" v-model="competitionFilter.FSR" />
        FSR
      </label>
    </span>
    <a :href="calendarPath" class="button is-primary is-small">
      <span>Wettkämpfe für deinen Kalendar</span>
    </a>
    <label class="checkbox">
      <input type="checkbox" v-model="displayPastCompetitions" />
      Zeige vergangene Wettkämpfe an
    </label>

    <table class="table is-striped">
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
            'is-selected': competition.id == selectedCompetition,
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
            <span
              :title="kind[competition.kind].title"
              :class="['tag', kind[competition.kind].type]"
              >{{ competition.kind }}</span
            >
            {{ flag(competition.location.country_code) }}
            {{ competition.location.city }}<br />
            {{ competition.name }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
table th.date,
table td.date {
  text-align: right !important;
  font-variant-numeric: tabular-nums;
}
</style>

<script setup>
const selectedCompetition = ref(null);
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
const competitionFromHash = () => window.location.hash.slice(1);

if (process.client) {
  const readCompetition = () => {
    selectedCompetition.value = competitionFromHash();
  };
  window.addEventListener("hashchange", readCompetition);
  readCompetition();
}

useHead({
  title: "Feuerwehr Wettkämpfe",
  viewport: "width=device-width, initial-scale=1, maximum-scale=1",
  charset: "utf-8",
});
</script>
