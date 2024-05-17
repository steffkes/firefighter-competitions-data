import { defineEventHandler } from "h3";
import data from "@/data/teams/240504_reclRpQWg31zYe1uI.json" assert { type: "json" };

export default defineEventHandler(async (event) => data["count"]);
