import { ofetch } from "ofetch";

const reverseName = (name) => name.split(", ").reverse().join(" ");

const tmp = (
  await Promise.allSettled(
    [5, 6].map(
      async (contest) =>
        new Promise(async (resolve) => {
          const { data } = await ofetch(
            "https://my1.raceresult.com/271676/RRPublish/data/list",
            {
              query: {
                key: "b43c7682c8720d9ae73fe4b5f1939e3b",
                contest,
                listname: "07 - Teilnehmer|Teilnehmerliste ABC Team",
              },
            }
          );
          return resolve(Object.values(data)[0]);
        })
    )
  )
)
  .flatMap(({ value }) => value)
  .map(([_bib, _id, _team, names, _category]) =>
    names.split(" / ").map(reverseName)
  );

export const teams = () => tmp;
export const participants = () => teams().flat();
export const count = () => participants().length;

import { defineEventHandler } from "h3";
import data from "@/data/teams/240825_recbbcQl0KFKj7Ox4.json" assert { type: "json" };

export default defineEventHandler(async (event) => data["count"]);
