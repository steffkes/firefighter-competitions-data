import { ofetch } from "ofetch";

export const count = async () =>
  (
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
            return resolve(data.length);
          })
      )
    )
  )
    .map(({ value }) => value)
    .reduce((state, curr) => state + curr, 0);

export default defineEventHandler(async (event) => await count());
