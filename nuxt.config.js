import { writeFileSync } from "fs";
import { join } from "path";

export default defineNuxtConfig({
  vite: {
    server: {
      hmr: {
        clientPort: 6601,
      },
    },
  },
  css: ["@/node_modules/bulma/css/bulma.min.css"],
  nitro: {
    devServer: {
      watch: ["./calendar-provider.js", "./competition-provider.js"],
    },
    prerender: {
      routes: [
        "/api/competitions/recbbcQl0KFKj7Ox4.json",
        "/api/competitions/recqjh5V3DUAzgLYQ.json",
        "/api/competitions/recNdFl6cR1xA5l4p.json",
        "/api/competitions/recxAxWccPrMWcVVv.json",
        "/api/competitions/recVzAj3TgO0th7JC.json",
        "/api/competitions/recRqH7LW1AQQ66FR.json",
        "/fcc.ics",
        "/fsr.ics",
        "/fcc-fsr.ics",
      ],
    },
  },
});
