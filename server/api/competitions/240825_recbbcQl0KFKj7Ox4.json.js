import { defineEventHandler } from "h3";
import data from "@/data/teams/240825_recbbcQl0KFKj7Ox4.json" assert { type: "json" };

export default defineEventHandler(async (event) => data["count"]);
