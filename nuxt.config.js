import { writeFileSync } from "fs";
import { join } from "path";
import calendarProvider from "./calendar-provider";

export default defineNuxtConfig({
  vite: {
    server: {
      hmr: {
        clientPort: 6601,
      },
    },
  },
  css: ["@/node_modules/bulma/css/bulma.min.css"],
  hooks: {
    "nitro:build:public-assets": async (nitro) => {
      for (const [calendarPath, calendarContent] of Object.entries(
        calendarProvider
      )) {
        writeFileSync(
          join(nitro.options.output.publicDir, calendarPath),
          await calendarContent()
        );
        console.info("calendar " + calendarPath + " exported");
      }
    },
  },
  nitro: {
    prerender: {
      routes: [
        "/api/competitions/recbbcQl0KFKj7Ox4.json",
        "/api/competitions/recqjh5V3DUAzgLYQ.json",
        "/api/competitions/recNdFl6cR1xA5l4p.json",
        "/api/competitions/recxAxWccPrMWcVVv.json",
      ],
    },
  },
});
