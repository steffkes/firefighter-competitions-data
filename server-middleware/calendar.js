const calendarProvider = require("../calendar-provider");

const app = require("express")().disable("x-powered-by");

for (const [path, content] of Object.entries(calendarProvider)) {
  app.get("/" + path, async (_, res) =>
    res.set("content-type", "text/calendar").send(await content())
  );
}

module.exports = app;
