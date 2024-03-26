import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

function* chunks(arr, n) {
  for (let i = 0; i < arr.length; i += n) {
    yield arr.slice(i, i + n);
  }
}

const data = (
  await Promise.allSettled(
    [1].map(
      async (contest) =>
        new Promise(async (resolve) => {
          const { data } = await ofetch(
            "https://my1.raceresult.com/279564/RRPublish/data/list",
            {
              query: {
                key: "0b390ff34ee4d88a57b036f1dc1fbf9e",
                contest,
                listname: "02_Teilnehmerlisten|Teilnehmer_Schanzenlauf",
              },
            }
          );
          return resolve(data);
        })
    )
  )
)
  .flatMap(({ value }) => value)
  .map(([_bib, name, _gender, _competition, _category]) =>
    name.replace(
      /^(.+)\s(.+)$/,
      (_, lastname, firstname) =>
        firstname +
        " " +
        lastname.replace(
          /^(.)(.+)$/,
          (_, first, rest) => first + rest.toLowerCase()
        )
    )
  );

export const teams = () => [...chunks(data, 2)];
export const participants = () => data;
export const count = () => participants().length;

export default defineEventHandler(async (event) => await count());
