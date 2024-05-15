import { defineEventHandler } from "h3";
import data from "@/data/teams/240526_recVzAj3TgO0th7JC.json" assert { type: "json" };

export default defineEventHandler(async (event) => data["count"]);
