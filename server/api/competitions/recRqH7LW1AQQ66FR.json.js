import { ofetch } from "ofetch";

export default defineEventHandler(async (event) => {
  return (
    await Promise.allSettled(
      [9].map(
        async (contest) =>
          new Promise(async (resolve) => {
            const { data } = await ofetch(
              "https://my1.raceresult.com/267314/RRPublish/data/list",
              {
                query: {
                  key: "e9de69adb513973efb142494b4cf6628",
                  listname: "rr Timing|Teilnehmerliste_Feuerwehrlauf",
                  contest,
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
