import competitionProvider from "./competition-provider.js";
import ical from "ical-generator";
import { add } from "date-fns";

export default async (variant) => {
  const calendar = ical({
    name: "👨‍🚒 " + "Feuerwehr Wettkämpfe: " + variant.join(" & "),
    prodId: {
      company: "gelungen.es",
      product: "firefighter-competitions",
      language: "de",
    },
  });

  const competitions = (await competitionProvider()).filter(({ kind }) =>
    variant.includes(kind),
  );
  for (const competition of competitions) {
    let status = "CONFIRMED";
    if (competition.date.is_draft) {
      status = "TENTATIVE";
    }
    if (competition.date.is_canceled) {
      status = "CANCELLED";
    }

    const event = {
      id: competition.id,
      url: competition.url,
      status,
      start: competition.date.start,
      // competitions over multiple days need the end date adjusted by +1
      // otherwise the last days is skipped in calendars
      end: add(competition.date.end, {
        days: competition.date.start < competition.date.end ? 1 : 0,
      }),
      allDay: true,
      summary: "👨‍🚒 " + competition.kind + ": " + competition.name,
      location: {
        title: [
          competition.location.city,
          new Intl.DisplayNames(["de"], { type: "region" }).of(
            competition.location.country_code,
          ),
        ]
          .filter(Boolean)
          .join(", "),
        geo: competition.location.coordinates
          ? {
              lat: competition.location.coordinates.lat,
              lon: competition.location.coordinates.lng,
            }
          : null,
      },
    };

    // reminder that registrations opens
    if (
      competition.date.registration_opens instanceof Date &&
      !isNaN(competition.date.registration_opens)
    ) {
      calendar.createEvent({
        ...event,
        id: event.id + "~RO",
        start: competition.date.registration_opens,
        end: competition.date.registration_opens,
        summary: "⏰ " + competition.name,
        description: "Ameldung öffnet heute!",
      });
    }

    // the event itself
    calendar.createEvent(event);
  }

  return calendar.toString();
};
