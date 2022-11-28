<template>
  <div>
    <b-table :data="competitions" :sort-multiple="false">
      <b-table-column label="Datum" width="50" v-slot="props">
        <template v-if="props.row.date">
          {{
            props.row.date.toLocaleDateString("de-DE", {
              year: "2-digit",
              month: "2-digit",
              day: "2-digit",
            })
          }}
        </template>
      </b-table-column>
      <b-table-column label="Art" width="20" v-slot="props">
        <b-tag
          :title="kind[props.row.kind].title"
          :type="kind[props.row.kind].type"
          >{{ props.row.kind }}</b-tag
        >
      </b-table-column>
      <b-table-column label="Stadt" v-slot="props">
        {{ props.row.location.city }}
      </b-table-column>
    </b-table>
  </div>
</template>

<script>
export default {
  data: () => ({
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
        date: record.fields.Datum ? new Date(record.fields.Datum) : null,
        location: {
          city: record.fields.Ort,
        },
      };
    };

    const [stairruns, challenges] = await Promise.all([
      airtable
        .get("appF8BPHzWCy6OKVF/tbl7nlGCJYqn3uF7C")
        .then((response) =>
          response.data.records.map(mapper.bind(null, "FSR"))
        ),
      airtable
        .get("appF8BPHzWCy6OKVF/tblRWTfwwmzoImHq1")
        .then((response) =>
          response.data.records.map(mapper.bind(null, "FCC"))
        ),
    ]);

    const competitions = [].concat(stairruns, challenges);
    competitions.sort(({ date: a_date }, { date: b_date }) => a_date - b_date);

    return {
      competitions,
    };
  },
};
</script>
