from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.FormRequest(
            method="POST",
            url="https://www.berlin-timing.de/Hochhauslauf/Startliste",
            formdata={"StartlisteStrecke": "Einsatzkräfte"},
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        for row in response.css("table tbody tr"):
            [_, _, _, firstname, lastname, _, _] = row.css("td::text").getall()
            if firstname.lower() != "cop":
                yield ParticipantItem(
                    competition_id=self.competition_id,
                    names=["{} {}".format(firstname.strip(), lastname.strip())],
                )
