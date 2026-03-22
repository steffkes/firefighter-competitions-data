from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        # source: https://www.berlin-timing.de/Hochhauslauf/Startliste
        yield scrapy.FormRequest(
            method="GET",
            url="https://www.berlin-timing.de/Liste/54cf88cceb98b07469fe3fb9d505ec44.csv",
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        for row in scrapy.utils.iterators.csviter(
            "\n".join(response.text.split("\n")[3:]), delimiter=";"
        ):
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=["{} {}".format(row["Vorname"], row["Nachname"])],
            )
