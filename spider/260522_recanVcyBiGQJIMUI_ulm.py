from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    race_id = "368654"
    race_key = "196b45c8a53bf1640e5b1e4250844ea4"

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "01_Teilnehmerlisten_RaceResult|Online-Teilnehmerliste",
                "contest": "1",
            },
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        for record in response.json()["data"]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=[self.fixName(None)],
            )
