import { defineEventHandler } from "h3";
import data from "@/data/teams/240607_recqjh5V3DUAzgLYQ.json" assert { type: "json" };

export default defineEventHandler(async (event) => data["count"]);
