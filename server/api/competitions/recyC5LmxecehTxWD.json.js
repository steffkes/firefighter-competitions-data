import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

export const count = async () =>
  (
    await Promise.allSettled(
      [1].map(
        async (contest) =>
          new Promise(async (resolve) => {
            const { data } = await ofetch(
              "https://my1.raceresult.com/279564/RRPublish/data/list",
              {
                query: {
                  key: "0b390ff34ee4d88a57b036f1dc1fbf9e",
                  contest,
                  listname: "02_Teilnehmerlisten|Teilnehmer_Schanzenlauf",
                },
              }
            );
            return resolve(data.length);
          })
      )
    )
  )
    .map(({ value }) => value)
    .reduce((state, curr) => state + curr, 0);

export default defineEventHandler(async (event) => await count());
