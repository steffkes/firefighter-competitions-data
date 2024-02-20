import { ofetch } from "ofetch";

export default async () => {
  const mapper = (kind, record) => {
    let coordinates = null;
    if (record.fields["Koordinaten"]) {
      const [lat, lng] = record.fields["Koordinaten"].split(",");
      coordinates = { lat: parseFloat(lat), lng: parseFloat(lng) };
    }
    return {
      id: record["id"],
      kind,
      name: record.fields["Name"],
      url: record.fields["Webseite"],
      showParticipantCount: record.fields["Teilnehmerzahl"],
      date: {
        start: new Date(record.fields.Datum),
        end: new Date(record.fields["Datum bis"] || record.fields.Datum),
        is_draft: record.fields["Vorläufig"],
        is_canceled: record.fields["Abgesagt"],
        registration_opens: new Date(record.fields.Anmeldestart),
      },
      location: {
        city: record.fields.Ort,
        country_code: record.fields.Land,
        coordinates,
      },
    };
  };

  const { records: stairruns } = await ofetch(
    "https://api.airtable.com/v0/appF8BPHzWCy6OKVF/tbl7nlGCJYqn3uF7C",
    {
      headers: {
        Authorization: "Bearer " + process.env.AIRTABLE_API_KEY,
      },
    }
  );
  const { records: challenges } = await ofetch(
    "https://api.airtable.com/v0/appF8BPHzWCy6OKVF/tblRWTfwwmzoImHq1",
    {
      headers: {
        Authorization: "Bearer " + process.env.AIRTABLE_API_KEY,
      },
    }
  );

  const competitions = [].concat(
    stairruns
      .filter((record) => record.fields.Datum)
      .map(mapper.bind(null, "FSR")),
    challenges
      .filter((record) => record.fields.Datum)
      .map(mapper.bind(null, "FCC"))
  );
  competitions.sort(
    ({ date: { start: a_date } }, { date: { start: b_date } }) =>
      a_date - b_date
  );

  return competitions;
};
