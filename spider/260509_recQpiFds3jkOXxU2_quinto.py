from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://event.endu.net/events/event/entrants-json",
            formdata={"idevento": "100485", "rows": "200", "page": "1"},
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        for entry in response.json()["rows"]:
            [
                _empty,
                firstname,
                lastname,
                _year,
                _nation,
                _team,
                _empty2,
                _competiton,
            ] = entry["cell"]
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=["%s %s" % (firstname, lastname)],
            )
