<template>
  <div>
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
          <td>
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
          <td>{{ competition.location.city }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  data: () => ({
    displayPastCompetitions: false,
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
  },
  computed: {
    filteredCompetitions() {
      let competitions = this.competitions;

      if (!this.displayPastCompetitions) {
        competitions = this.competitions.filter(
          (competition) => !this.isPast(competition)
        );
      }

      return competitions;
    },
  },
  async asyncData({ params, $axios }) {
    const airtable = $axios.create({
      baseURL: "https://api.airtable.com/v0/",
      headers: {
        Authorization: "Bearer " + process.env.AIRTABLE_API_KEY,
      },
    });

    const mapper = (kind, record) => {
      return {
        kind,
        date: new Date(record.fields.Datum),
        location: {
          city: record.fields.Ort,
        },
      };
    };

    const [stairruns, challenges] = await Promise.all([
      airtable
        .get("appF8BPHzWCy6OKVF/tbl7nlGCJYqn3uF7C")
        .then((response) => response.data.records)
        .then((records) => records.filter((record) => record.fields.Datum))
        .then((records) => records.map(mapper.bind(null, "FSR"))),
      airtable
        .get("appF8BPHzWCy6OKVF/tblRWTfwwmzoImHq1")
        .then((response) => response.data.records)
        .then((records) => records.filter((record) => record.fields.Datum))
        .then((records) => records.map(mapper.bind(null, "FCC"))),
    ]);

    const competitions = [].concat(stairruns, challenges);
    competitions.sort(({ date: a_date }, { date: b_date }) => a_date - b_date);

    return {
      competitions,
    };
  },
};
</script>
