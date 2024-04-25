import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

const reverseName = (name) => name.split(", ").reverse().join(" ");

const data = (
  await Promise.allSettled(
    [3, 4].map(
      async (contest) =>
        new Promise(async (resolve) => {
          const { data } = await ofetch(
            "https://my1.raceresult.com/277814/RRPublish/data/list",
            {
              query: {
                key: "0fdd4b818141191b0084fc27c0714d40",
                contest,
                listname: "Teilnehmerlisten|TN Startzeit",
              },
            }
          );
          return resolve(data);
        })
    )
  )
)
  .flatMap(({ value }) => value)
  .map(
    ([
      _id,
      _empty,
      bib,
      name,
      _gender,
      _category,
      _team,
      _nationality,
      _competition,
    ]) => ({
      name: reverseName(name),
      team: bib.split("-")[0],
    })
  );

const grouped = data.reduce((state, { name, team }) => {
  if (!(team in state)) {
    state[team] = [];
  }
  state[team].push(name);
  return state;
}, {});

export const teams = () => Object.values(grouped);
export const participants = () => teams().flat();
export const count = () => participants().length;

export default defineEventHandler(async (event) => await count());
