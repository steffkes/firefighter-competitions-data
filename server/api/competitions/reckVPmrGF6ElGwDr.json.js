import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

const data = (
  await Promise.allSettled(
    [5, 6].map(
      async (contest) =>
        new Promise(async (resolve) => {
          const { data } = await ofetch(
            "https://my1.raceresult.com/277111/RRPublish/data/list",
            {
              query: {
                key: "a2821a19e7457bf1c5b85e15a84bd625",
                contest,
                listname: "07 - Teilnehmer|Teilnehmerliste ABC",
              },
            }
          );
          return resolve(Object.values(data)[0] || []);
        })
    )
  )
)
  .flatMap(({ value }) => value)
  .map(([_id, _bib, name, _byear, _gender, _team]) => name)
  .map((name) => name.split(", ").reverse().join(" "));

export const participants = () => data;
export const count = () => data.length;

export default defineEventHandler(async (event) => await count());
