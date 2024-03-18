import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

const data = (
  await Promise.allSettled(
    [3].map(
      async (contest) =>
        new Promise(async (resolve) => {
          const { data } = await ofetch(
            "https://my1.raceresult.com/271276/RRPublish/data/list",
            {
              query: {
                key: "353bdf54f57af48fa0d1af824aa6e860",
                contest,
                listname: "Online|Teilnehmerliste ABC",
              },
            }
          );
          return resolve(Object.values(data)[0]);
        })
    )
  )
)
  .flatMap(({ value }) => value)
  .map(
    ([_bib, _bib2, name, _nationality, _byear, _gender, _category, _team]) =>
      name
  )
  .map((name) => name.split(", ").reverse().join(" "));

export const participants = () => data;
export const count = () => data.length;

export default defineEventHandler(async (event) => await count());
