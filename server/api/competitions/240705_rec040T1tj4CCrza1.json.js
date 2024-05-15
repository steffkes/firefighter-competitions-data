import { defineEventHandler } from "h3";
import data from "@/data/teams/240705_rec040T1tj4CCrza1.json" assert { type: "json" };

export default defineEventHandler(async (event) => data["count"]);
