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
      <b-icon icon="calendar"> </b-icon>
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
          <th><abbr title="Art des Wettkampfes">Art</abbr></th>
          <th>Ort</th>
          <th>Wettkampf</th>
        </tr>
      </thead>
      <tfoot>
        <tr>
          <th class="date">Datum</th>
          <th><abbr title="Art des Wettkampfes">Art</abbr></th>
          <th>Ort</th>
          <th>Wettkampf</th>
        </tr>
      </tfoot>
      <tbody>
        <tr
          v-for="competition in filteredCompetitions"
          @click="highlight(competition)"
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
          </td>
          <td>
            {{ flag(competition.location.country_code) }}
            {{ competition.location.city }}
          </td>
          <td>
            {{ competition.name }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
const competitionProvider = require("../competition-provider");

export default {
  data: () => ({
    selectedCompetition: null,
    displayPastCompetitions: false,
    competitionFilter: {
      FCC: true,
      FSR: true,
    },
    kind: {
      FCC: {
        title: "Firefighter Combat Challenge",
        type: "is-warning",
      },
      FSR: {
        title: "Firefighter Stair Run",
        type: "is-info",
      },
    },
  }),
  methods: {
    isPast: (competition) => new Date() - competition.date.end > 0,
    flag: (countryCode) =>
      countryCode
        .toUpperCase()
        .replace(/./g, (char) =>
          String.fromCodePoint(127397 + char.charCodeAt())
        ),
    formatDate: (date) =>
      date.toLocaleDateString("de-DE", {
        weekday: "short",
        year: "2-digit",
        month: "2-digit",
        day: "2-digit",
      }),
    highlight: (competition) => {
      window.location.hash = "#" + competition.id;
    },
    competitionFromHash: () => window.location.hash.slice(1),
  },
  computed: {
    calendarPath() {
      return (
        Object.keys(this.kind)
          .filter((kind) => this.competitionFilter[kind])
          .join("-")
          .toLowerCase() + ".ics"
      );
    },
    filteredCompetitions() {
      let competitions = this.competitions;

      if (!this.displayPastCompetitions) {
        competitions = competitions.filter(
          (competition) => !this.isPast(competition)
        );
      }

      if (!this.competitionFilter.FSR) {
        competitions = competitions.filter(({ kind }) => kind != "FSR");
      }

      if (!this.competitionFilter.FCC) {
        competitions = competitions.filter(({ kind }) => kind != "FCC");
      }

      return competitions;
    },
  },
  async asyncData() {
    return {
      competitions: await competitionProvider(),
    };
  },
  mounted() {
    const readCompetition = () => {
      this.selectedCompetition = this.competitionFromHash();
    };
    window.addEventListener("hashchange", readCompetition);
    readCompetition();
  },
};
</script>

<style>
table th.date,
table td.date {
  text-align: right !important;
  font-variant-numeric: tabular-nums;
}
</style>
