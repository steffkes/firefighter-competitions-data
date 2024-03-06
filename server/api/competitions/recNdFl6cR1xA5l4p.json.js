import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

export const count = async () => {
  const data = (
    await Promise.allSettled(
      "abcdefghijklmnopqrstuvwxyz".split("").map(
        async (character) =>
          new Promise(async (resolve) => {
            const data = await ofetch(
              "https://apiah.endu.net/events/91215/entries",
              {
                query: {
                  limit: 100000,
                  teamname: "a",
                },
              }
            );

            return resolve(data);
          })
      )
    )
  ).flatMap(({ value }) => value);

  const uniq = [
    ...new Map(data.map((entry) => [entry.entryid, entry])).values(),
  ];

  return uniq.length;
};

export default defineEventHandler(async (event) => await count());
