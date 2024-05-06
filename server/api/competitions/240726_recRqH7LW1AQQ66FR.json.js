import { defineEventHandler } from "h3";
import data from "@/data/teams/240726_recRqH7LW1AQQ66FR.json" assert { type: "json" };

export default defineEventHandler(async (event) => data["count"]);
