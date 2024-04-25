import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

const raw = (
  await Promise.allSettled(
    "abcdefghijklmnopqrstuvwxyz".split("").map(
      async (character) =>
        new Promise(async (resolve) => {
          const data = await ofetch(
            "https://apiah.endu.net/events/91215/entries",
            {
              query: {
                limit: 100000,
                teamname: character,
              },
            }
          );

          return resolve(data);
        })
    )
  )
)
  .flatMap(({ value }) => value)
  .map(({ entryid, firstname, lastname }) => [
    entryid,
    firstname + " " + lastname,
  ]);

const data = Object.values(Object.fromEntries(raw)).map((name) => [name]);

export const teams = () => data;
export const participants = () => teams().flat();
export const count = () => participants().length;

export default defineEventHandler(async (event) => await count());
