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
};
