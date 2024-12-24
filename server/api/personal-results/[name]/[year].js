import { defineEventHandler } from "h3"; // needed for test
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import glob from "fast-glob";

export default defineEventHandler(async (event) => {
  const requestedName = decodeURIComponent(
    getRouterParam(event, "name", { decode: false }),
  );
  const requestedYear = getRouterParam(event, "year");

  const results = (await glob(["data/data/results/*.jsonl"]))
    .flatMap((path) =>
      readFileSync(resolve(path), "utf8")
        .trim()
        .split(/\r?\n/)
        .filter(Boolean)
        .map(JSON.parse),
    )
    .filter(({ date }) => date.startsWith(requestedYear))
    .filter(({ names }) => names.includes(requestedName));

  return results;
});
