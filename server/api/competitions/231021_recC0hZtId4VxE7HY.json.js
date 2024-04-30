import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

const data = (
  await Promise.allSettled(
    [8152, 8153].map(
      async (contest) =>
        new Promise(async (resolve) => {
          const data = await ofetch(
            "https://www.anmeldungs-service.de/module/teilnehmer/staffel_cache.php",
            {
              parseResponse: JSON.parse,
              headers: {
                "X-Requested-With": "XMLHttpRequest",
              },
              query: {
                wettid: contest,
                totalrows: 2000,
              },
            }
          );
          return resolve(data.rows || []);
        })
    )
  )
)
  .flatMap(({ value }) => value)
  .map(({ cell: { name: names } }) =>
    names
      .split("<br>")
      .map((name) =>
        name
          .match(/^(.+)\s+\w\s+\d+$/)[1]
          .split(" ")
          .reverse()
          .join(" ")
      )
      .sort()
  )
  .sort();

export const teams = () => data;
export const participants = () => teams().flat();
export const count = () => participants().length;

export default defineEventHandler(async (event) => await count());
