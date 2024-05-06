import { defineEventHandler } from "h3";
import data from "@/data/teams/241019_recL95uxMRJ0CWcPT.json" assert { type: "json" };

export default defineEventHandler(async (event) => data["count"]);
