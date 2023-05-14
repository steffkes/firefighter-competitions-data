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
  hooks: {
    "nitro:build:public-assets": async (_nitro) => {
      for (const [calendarPath, calendarContent] of Object.entries(
        calendarProvider
      )) {
        writeFileSync(
          join("./.output/public", calendarPath),
          await calendarContent()
        );
        console.info("calendar " + calendarPath + " exported");
      }
    },
  },
});
