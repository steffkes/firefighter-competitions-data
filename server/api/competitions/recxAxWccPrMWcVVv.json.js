import { ofetch } from "ofetch";

export default defineEventHandler(async (event) => {
  return (
    await Promise.allSettled(
      [1, 2, 3, 4, 5, 6, 7, 8, 9].map(
        async (contest) =>
          new Promise(async (resolve) => {
            const { data } = await ofetch(
              "https://my1.raceresult.com/259924/RRPublish/data/list",
              {
                query: {
                  key: "9cca7a2e787022b15a2c81b253b2dde6",
                  contest,
                  listname: "Online|Teilnehmer nach Team",
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
});
