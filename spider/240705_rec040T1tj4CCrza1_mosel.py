from util import FccSpider, ParticipantItem
import scrapy


class CompetitionSpider(FccSpider):
    name = __name__
    event_id = 17

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://www.firefighter-challenge-germany.de/combat-challenge/registrierungsliste/",
            callback=self.parse_starters,
        )

        yield from super().start_requests()

    def parse_starters(self, response):
        for row in response.css("table[data-eventdayid='34'] tr"):
            entry = row.css("td:nth-child(3)::text").get()

            if not entry:
                continue

            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(self.fixName, entry.split(","))),
            )

        for row in response.css("table[data-eventdayid='35'] tr"):
            entry = row.css("td:nth-child(3)::text").get()

            if not entry:
                continue

            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(self.fixName, entry.split(","))),
            )

        for row in response.css("table[data-eventdayid='36'] tr"):
            entry = row.css("td:nth-child(3)::text").get()

            if not entry:
                continue

            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(self.fixName, entry.split(","))),
            )
