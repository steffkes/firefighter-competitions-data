const axios = require("axios");

module.exports = async () => {
  const airtable = axios.create({
    baseURL: "https://api.airtable.com/v0/",
    headers: {
      Authorization: "Bearer " + process.env.AIRTABLE_API_KEY,
    },
  });

  const mapper = (kind, record) => {
    return {
      kind,
      date: {
        start: new Date(record.fields.Datum),
        end: new Date(record.fields["Datum bis"] || record.fields.Datum),
      },
      location: {
        city: record.fields.Ort,
        country_code: record.fields.Land,
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
  competitions.sort(
    ({ date: { start: a_date } }, { date: { start: b_date } }) =>
      a_date - b_date
  );

  return competitions;
};
