import glob from "fast-glob";
import { basename } from "path";
import { writeFile } from "node:fs/promises";

const date = new Date();
const str = (object) =>
  JSON.stringify({ date: date.toISOString(), ...object }, null, 2);

const extension = ".json.js";
for (const path of await glob(["./server/api/competitions/*" + extension])) {
  try {
    const { participants } = await import(path);
    const competition = basename(path, extension);
    const result = str({
      competition,
      participants: participants(),
    });
    console.log(result);
    await writeFile("data/participants/" + competition + ".json", result);
  } catch (error) {
    console.error({ path, error });
  }
}
