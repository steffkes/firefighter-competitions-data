import glob from "fast-glob";
import { basename } from "path";

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
      routes: ["/fcc.ics", "/fsr.ics", "/fcc-fsr.ics"],
    },
  },
  hooks: {
    async "nitro:config"(nitroConfig) {
      if (nitroConfig.dev) return;

      nitroConfig.prerender.routes.push(
        ...(
          await glob(["api/competitions/*.json.js"], {
            cwd: "./server",
          })
        ).map((path) => "/" + path.replace(/\.js$/, ""))
      );
    },
  },
});
