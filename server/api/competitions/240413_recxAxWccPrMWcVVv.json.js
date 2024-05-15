import { defineEventHandler } from "h3";
import data from "@/data/teams/240413_recxAxWccPrMWcVVv.json" assert { type: "json" };

export default defineEventHandler(async (event) => data["count"]);
