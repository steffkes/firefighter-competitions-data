import { ofetch } from "ofetch";

export const count = async () =>
  (
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
            return resolve(Object.values(data)[0].length);
          })
      )
    )
  )
    .map(({ value }) => value)
    .reduce((state, curr) => state + curr, 0);

export default defineEventHandler(async (event) => await count());
