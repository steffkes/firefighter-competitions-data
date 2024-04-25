import { ofetch } from "ofetch";
import { defineEventHandler } from "h3";

const data = (
  await Promise.allSettled(
    [2].map(
      async (contest) =>
        new Promise(async (resolve) => {
          const { data } = await ofetch(
            "https://my1.raceresult.com/275363/RRPublish/data/list",
            {
              query: {
                key: "2763c5212a432a43da74006d8553cbcb",
                contest,
                listname: "Teilnehmerlisten|Teilnehmerliste Feuerwehr",
              },
            }
          );
          return resolve(data);
        })
    )
  )
)
  .flatMap(({ value }) => value)
  .map(([_bib, _team, _unknown, _gender, names]) =>
    names.split(/[,\/]/).map((name) => name.trim())
  )
  .filter((team) => team.length == 2);

export const teams = () => data;
export const participants = () => teams().flat();
export const count = () => participants().length;

export default defineEventHandler(async (event) => await count());
