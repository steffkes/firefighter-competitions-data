import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

export const count = async () =>
  (
    await Promise.allSettled(
      [2].map(
        async (contest) =>
          new Promise(async (resolve) => {
            const { data } = await ofetch(
              "https://my1.raceresult.com/275363/RRPublish/data/list",
              {
                query: {
                  key: "2763c5212a432a43da74006d8553cbcb",
                  contest,
                  listname: "Teilnehmerlisten|Teilnehmerliste Feuerwehr",
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
