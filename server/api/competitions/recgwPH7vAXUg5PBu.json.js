import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

const data = (
  await Promise.allSettled(
    [5, 6].map(
      async (contest) =>
        new Promise(async (resolve) => {
          const { data } = await ofetch(
            "https://my1.raceresult.com/281781/RRPublish/data/list",
            {
              query: {
                key: "1a92069df75cc5903748fe12993e7e8b",
                contest,
                listname: "07 - Teilnehmer - PUBLIC|Teilnehmer ABC",
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
