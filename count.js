import glob from "fast-glob";
import { basename } from "path";

const date = new Date();
const str = (object) => JSON.stringify({ date: date.toISOString(), ...object });

const extension = ".json.js";
for (const path of await glob(["./server/api/competitions/*" + extension])) {
  const { count } = await import(path);
  console.log(
    str({ competition: basename(path, extension).split("_")[1], count: await count() })
  );
}
