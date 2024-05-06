import { defineEventHandler } from "h3";
import data from "@/data/teams/240511_recyC5LmxecehTxWD.json" assert { type: "json" };

export default defineEventHandler(async (event) => data["count"]);
