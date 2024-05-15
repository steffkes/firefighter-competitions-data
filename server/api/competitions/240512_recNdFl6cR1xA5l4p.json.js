import { defineEventHandler } from "h3";
import data from "@/data/teams/240512_recNdFl6cR1xA5l4p.json" assert { type: "json" };

export default defineEventHandler(async (event) => data["count"]);
