import fs from "fs";
import path from "path";

const ical = require("ical-generator");
const competitionProvider = require("./competition-provider");

const variants = [["FCC", "FSR"], ["FCC"], ["FSR"]];

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

  hooks: {
    generate: {
      async done(generator, errors) {
        console.info("generate done");
        const competitions = await competitionProvider();

        for (const variant of variants) {
          const slug = variant.join("-");
          const filtered = competitions.filter(({ kind }) =>
            variant.includes(kind)
          );
          const calendar = ical({
            name: "Feuerwehr Wettkämpfe: " + variant.join(" & "),
            prodId: {
              company: "gelungen.es",
              product: "firefighter-competitions",
              language: "de",
            },
          });

          for (const competition of filtered) {
            calendar.createEvent({
              start: competition.date,
              end: competition.date,
              allDay: true,
              summary: competition.kind + ": " + competition.location.city,
              location:
                competition.location.city +
                ", " +
                new Intl.DisplayNames(["de"], { type: "region" }).of(
                  competition.location.country_code
                ),
            });
          }

          fs.writeFileSync(
            path.join(generator.distPath, slug.toLowerCase() + ".ics"),
            calendar.toString()
          );
        }
      },
    },
  },
};
