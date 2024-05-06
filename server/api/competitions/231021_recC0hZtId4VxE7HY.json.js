import { defineEventHandler } from "h3";
import data from "@/data/teams/231021_recC0hZtId4VxE7HY.json" assert { type: "json" };

export default defineEventHandler(async (event) => data["count"]);
