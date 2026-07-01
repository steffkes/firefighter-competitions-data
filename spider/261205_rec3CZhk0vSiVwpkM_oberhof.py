import scrapy
from util import (
    Spider,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
    SlotItem,
)
from itertools import batched


class CompetitionSpider(Spider):
    name = __name__

    race_id = "394956"
    race_key = "5536f414f74accaa71b17159b889072f"

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/participants/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Online|Teilnehmer",
                "contest": "0",
            },
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/registration/config" % self.race_id,
            callback=self.parse_slots,
        )

    def parse_slots(self, response):
        yield SlotItem(
            competition_id=self.competition_id,
            amount=response.json()["Registrations"][0]["Contests"][0]["SlotsLeft"],
        )

    def parse_starters(self, response):
        for item in response.json()["data"]["#1_StairRun - Feuerwehr"].values():
            for [
                [_id11, _id12, name1, _team1, _nat1, _yob1],
                [_id21, _id22, name2, _team2, _nat2, _yob2],
            ] in batched(item, 2):
                yield ParticipantItem(
                    competition_id=self.competition_id,
                    names=sorted(map(self.fixName, [name1, name2])),
                )
