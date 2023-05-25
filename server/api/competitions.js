import { defineEventHandler } from "h3"; // needed for test
import competitionProvider from "../../../competition-provider";

export default defineEventHandler(async (event) => await competitionProvider());
