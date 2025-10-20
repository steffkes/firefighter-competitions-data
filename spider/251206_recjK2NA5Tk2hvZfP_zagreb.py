from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.http.JsonRequest(
            method="POST",
            url="https://tracey-prod-6b98eac1c8fad5e7fa6493b8d82e4fc3.traceysport.com/api/public/competitors/find",
            data={"filter": {"eventId": 2841}, "pages": {"pageSize": 51, "page": 1}},
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        entries = response.json()["result"]
        for entry in entries[0:50]:
            if entry["raceId"] in [8051, 8052, 8053]:
                yield ParticipantItem(
                    competition_id=self.competition_id,
                    names=["{} {}".format(entry["firstName"], entry["lastName"])],
                )
