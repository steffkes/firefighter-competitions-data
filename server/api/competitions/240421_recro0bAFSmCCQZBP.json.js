import { defineEventHandler } from "h3";
import data from "@/data/teams/240421_recro0bAFSmCCQZBP.json" assert { type: "json" };

export default defineEventHandler(async (event) => data["count"]);
