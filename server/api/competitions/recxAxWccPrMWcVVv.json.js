import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

const data = (
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
          return resolve(Object.values(data)[0]);
        })
    )
  )
)
  .flatMap(({ value }) => value)
  .map(([_bib, _empty, _team, _city, _origin, names, _category]) =>
    names.split(" / ").map((name) => name.match(/^[^\(]+/)[0].trim())
  );

export const teams = () => data;
export const participants = () => teams().flat();
export const count = () => participants().length;

export default defineEventHandler(async (event) => await count());
