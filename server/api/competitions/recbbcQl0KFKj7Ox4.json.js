import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

export const count = async () =>
  (
    await Promise.allSettled(
      [5, 6].map(
        async (contest) =>
          new Promise(async (resolve) => {
            const { data } = await ofetch(
              "https://my1.raceresult.com/271676/RRPublish/data/list",
              {
                query: {
                  key: "b43c7682c8720d9ae73fe4b5f1939e3b",
                  contest: 5,
                  listname: "07 - Teilnehmer|Teilnehmerliste ABC Team",
                },
              }
            );
            return resolve(Object.values(data)[0].length);
          })
      )
    )
  )
    .map(({ value }) => value)
    .reduce((state, curr) => state + curr, 0);

export default defineEventHandler(async (event) => await count());
