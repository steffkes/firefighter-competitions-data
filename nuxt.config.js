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
    prerender: {
      routes: [
        "/api/competitions/recbbcQl0KFKj7Ox4.json",
        "/api/competitions/recqjh5V3DUAzgLYQ.json",
        "/api/competitions/recNdFl6cR1xA5l4p.json",
        "/api/competitions/recxAxWccPrMWcVVv.json",
        "/fcc.ics",
        "/fsr.ics",
        "/fcc-fsr.ics",
      ],
    },
  },
});
