import glob from "fast-glob";
import Airtable from "airtable";

const personName = process.argv[2];
if (!personName) {
  console.error("missing name of the person (as argument)");
  process.exit(1);
}

const airtable = new Airtable({ apiKey: process.env.AIRTAIBLE_API_KEY });

const records = await airtable
  .base("appF8BPHzWCy6OKVF")
  .table("tbl7nlGCJYqn3uF7C")
  .select()
  .firstPage();

const competitions = Object.fromEntries(
  records.map(({ id, fields }) => [id, fields]),
);

console.log(
  "Persönlicher Wettkampfkalender für %s",
  JSON.stringify(personName),
);

for (const path of await glob(["./data/teams/*.json"])) {
  const {
    default: { competition, teams },
  } = await import(path, {
    assert: { type: "json" },
  });
  const filteredTeams = teams
    .filter((team) => team.includes(personName))
    .map((team) => team.filter((name) => name != personName));
  //console.debug({ personName, competition, filteredTeams });
  if (filteredTeams.length) {
    console.log(
      "%s %s: %s",
      competitions[competition].Datum,
      competitions[competition].Name,
      filteredTeams.join(", "),
    );
  }
}
