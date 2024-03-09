import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

export const count = async () =>
  (
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
            return resolve((Object.values(data)[0] || []).length);
          })
      )
    )
  )
    .map(({ value }) => value)
    .reduce((state, curr) => state + curr, 0);

export default defineEventHandler(async (event) => await count());
