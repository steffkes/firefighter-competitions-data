import { defineEventHandler } from "h3";
import data from "@/data/teams/240914_reckVPmrGF6ElGwDr.json" assert { type: "json" };

export default defineEventHandler(async (event) => data["count"]);
