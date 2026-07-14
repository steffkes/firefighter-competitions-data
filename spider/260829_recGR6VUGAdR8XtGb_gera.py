from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://www.1-sv-gera.de/etl-meldeliste.html",
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        for table in response.css("table[summary*='TreppenlaufFeuerwehr']"):
            for rows in table.css("tbody tr"):
                [lastname, firstname, _team, _city, _confirmed] = rows.css(
                    "td::text"
                ).getall()
                yield ParticipantItem(
                    competition_id=self.competition_id,
                    names=["{} {}".format(firstname, lastname)],
                )
