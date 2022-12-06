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
    <a :href="calendarPath">
      <button class="button is-link is-small">
        <b-icon icon="calendar"> </b-icon>
        <span>Wettkämpfe für deinen Kalendar</span>
      </button>
    </a>
    <label class="checkbox">
      <input type="checkbox" v-model="displayPastCompetitions" />
      Zeige vergangene Wettkämpfe an
    </label>

    <table class="table is-striped">
      <thead>
        <tr>
          <th>Datum</th>
          <th><abbr title="Art des Wettkampfes">Art</abbr></th>
          <th>Ort</th>
        </tr>
      </thead>
      <tfoot>
        <tr>
          <th>Datum</th>
          <th><abbr title="Art des Wettkampfes">Art</abbr></th>
          <th>Ort</th>
        </tr>
      </tfoot>
      <tbody>
        <tr
          v-for="competition in filteredCompetitions"
          :class="{
            'has-text-grey-light': isPast(competition),
          }"
        >
          <td class="date">
            {{
              competition.date.toLocaleDateString("de-DE", {
                year: "2-digit",
                month: "2-digit",
                day: "2-digit",
              })
            }}
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
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
const competitionProvider = require("../competition-provider");

export default {
  data: () => ({
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
    isPast: (competition) => new Date() - competition.date > 0,
    flag: (countryCode) =>
      countryCode
        .toUpperCase()
        .replace(/./g, (char) =>
          String.fromCodePoint(127397 + char.charCodeAt())
        ),
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
};
</script>

<style>
table td.date {
  text-align: right;
  font-variant-numeric: tabular-nums;
}
</style>
