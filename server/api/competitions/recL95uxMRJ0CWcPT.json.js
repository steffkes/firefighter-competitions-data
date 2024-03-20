import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

const data = (
  await Promise.allSettled(
    [9026, 9027].map(
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
          return resolve(data.rows);
        })
    )
  )
)
  .flatMap(({ value }) => value)
  .flatMap(({ cell: { name: names } }) => names.split("<br>"))
  .map((name) => name.match(/^(.+)\s+\w\s+\d+$/)[1]);

export const participants = () => data;
export const count = () => data.length;

export default defineEventHandler(async (event) => await count());
