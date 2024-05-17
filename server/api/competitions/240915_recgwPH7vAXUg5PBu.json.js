import { defineEventHandler } from "h3";
import data from "@/data/teams/240915_recgwPH7vAXUg5PBu.json" assert { type: "json" };

export default defineEventHandler(async (event) => data["count"]);
