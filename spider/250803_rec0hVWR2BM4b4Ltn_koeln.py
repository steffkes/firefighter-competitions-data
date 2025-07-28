import scrapy
from util import (
    Spider,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
    SlotItem,
)


class CompetitionSpider(Spider):
    name = __name__

    race_id = "323602"
    race_key = "77bdc85dcb9f1b7a137834310113b943"

    def start_requests(self):
        for contest in [5, 6]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "listname": "07 - Teilnehmer|Teilnehmerliste ABC Team",
                    "contest": str(contest),
                },
                callback=self.parse_starters,
            )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRRegStart/data/config" % self.race_id,
            callback=self.parse_slots,
        )

    def parse_starters(self, response):
        fixName = lambda name: " ".join(reversed(list(map(str.strip, name.split(",")))))

        data = list(response.json()["data"].values())[0]
        for [_bib, _number2, _id, _team, names, _category] in data:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(fixName, names.split(" / "))),
            )

    def parse_slots(self, response):
        data = response.json()

        isRegClosed = data["Now"] >= data["RegUntil"]
        if isRegClosed:
            yield SlotItem(competition_id=self.competition_id, amount=0)
