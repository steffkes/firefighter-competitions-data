import fs from "fs";
import path from "path";

const calendarProvider = require("./calendar-provider");

export default {
  target: "static",

  server: {
    host: "0.0.0.0",
  },

  head: {
    title: "Feuerwehr Wettkämpfe",
    htmlAttrs: {
      lang: "de",
    },
    meta: [
      { charset: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { hid: "description", name: "description", content: "" },
      { name: "format-detection", content: "telephone=no" },
    ],
    link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
  },

  components: true,

  modules: ["nuxt-buefy", "@nuxtjs/axios"],

  axios: {
    baseURL: "/",
  },

  serverMiddleware: ["~/server-middleware/calendar"],

  hooks: {
    generate: {
      async done(generator, errors) {
        for (const [calendarPath, calendarContent] of Object.entries(
          calendarProvider
        )) {
          fs.writeFileSync(
            path.join(generator.distPath, calendarPath),
            await calendarContent()
          );
          console.info("calendar " + calendarPath + " exported");
        }
      },
    },
  },
};
