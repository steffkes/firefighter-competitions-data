import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

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
      _bib,
      _empty,
      _unknown,
      name,
      _gender,
      _category,
      _team,
      _nationality,
      _competition,
    ]) => name
  )
  .map((name) => name.split(", ").reverse().join(" "));

export const participants = () => data;
export const count = () => data.length;

export default defineEventHandler(async (event) => await count());
