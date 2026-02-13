from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.http.JsonRequest(
            url="https://www.davengo.com/event/starter/charity-challenge-help-stairs-run-2026/search/list",
            data={
                "term": "",
                "offset": 0,
                "type": "simple",
                "category": "help-stairs-run",
            },
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        for result in (
            result
            for result in response.json()["results"]
            if (result["club"] or "").startswith("Feuerwehr")
        ):
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=["{} {}".format(result["firstName"], result["lastName"])],
            )
