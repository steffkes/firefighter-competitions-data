import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

const data = (
  await Promise.allSettled(
    [5, 6].map(
      async (contest) =>
        new Promise(async (resolve) => {
          const { data } = await ofetch(
            "https://my1.raceresult.com/271676/RRPublish/data/list",
            {
              query: {
                key: "b43c7682c8720d9ae73fe4b5f1939e3b",
                contest,
                listname: "07 - Teilnehmer|Teilnehmerliste ABC",
              },
            }
          );
          return resolve(Object.values(data)[0]);
        })
    )
  )
)
  .flatMap(({ value }) => value)
  .map(([_bib, _id, name, _byear, _category, _team]) =>
    name.split(", ").reverse().join(" ")
  );

export const participants = () => data;
export const count = () => data.length;

export default defineEventHandler(async (event) => await count());
