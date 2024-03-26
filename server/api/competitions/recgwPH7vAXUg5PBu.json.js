import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

const data = (
  await Promise.allSettled(
    [5, 6].map(
      async (contest) =>
        new Promise(async (resolve) => {
          const { data } = await ofetch(
            "https://my1.raceresult.com/281781/RRPublish/data/list",
            {
              query: {
                key: "1a92069df75cc5903748fe12993e7e8b",
                contest,
                listname: "07 - Teilnehmer - PUBLIC|Teilnehmer ABC-Team",
              },
            }
          );
          return resolve(data || []);
        })
    )
  )
)
  .flatMap(({ value }) => value)
  .map(([_id, _bib, _team, names, _category]) => names.split(" / "));

export const teams = () => data;
export const participants = () => teams().flat();
export const count = () => participants().length;

export default defineEventHandler(async (event) => await count());
