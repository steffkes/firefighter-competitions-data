const ical = require("ical-generator");
const competitionProvider = require("./competition-provider");

module.exports = Object.fromEntries(
  [["FCC", "FSR"], ["FCC"], ["FSR"]].map((variant) => {
    return [
      variant.join("-").toLowerCase() + ".ics",
      async function (variant) {
        const competitions = await competitionProvider();
        const filtered = competitions.filter(({ kind }) =>
          variant.includes(kind)
        );

        const calendar = ical({
          name: "👨‍🚒 " + "Feuerwehr Wettkämpfe: " + variant.join(" & "),
          prodId: {
            company: "gelungen.es",
            product: "firefighter-competitions",
            language: "de",
          },
        });

        for (const competition of filtered) {
          let status = "CONFIRMED";
          if (competition.date.is_draft) {
            status = "TENTATIVE";
          }
          if (competition.date.is_canceled) {
            status = "CANCELLED";
          }
          calendar.createEvent({
            id: competition.id,
            url: competition.url,
            status,
            start: competition.date.start,
            end: competition.date.end,
            allDay: true,
            summary: "👨‍🚒 " + competition.kind + ": " + competition.name,
            location:
              competition.location.city +
              ", " +
              new Intl.DisplayNames(["de"], { type: "region" }).of(
                competition.location.country_code
              ),
          });
        }

        return calendar.toString();
      }.bind(null, variant),
    ];
  })
);
