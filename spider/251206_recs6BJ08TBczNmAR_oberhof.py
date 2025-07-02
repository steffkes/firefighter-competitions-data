from util import Spider, ParticipantItem, ResultItem, ResultRankItem
from itertools import batched
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__
    race_id = "340048"
    race_key = "159bc32560a3f6d9c498b3a4435fee48"

    @staticmethod
    def fixName(name):
        return " ".join(reversed(name.split(", ")))

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Online|Teilnehmer",
                "contest": "0",
            },
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        for entries in response.json()["data"]["#1_StairRun - Feuerwehr"].values():
            for [
                [
                    _id1_1,
                    _bib_1,
                    raw_name_1,
                    _team_1,
                    _country_1,
                    _year_1,
                    _age_group_1,
                ],
                [
                    _id1_2,
                    _bib_2,
                    raw_name_2,
                    _team_2,
                    _country_2,
                    _year_2,
                    _age_group_2,
                ],
            ] in batched(entries, 2):
                yield ParticipantItem(
                    competition_id=self.competition_id,
                    names=sorted(map(self.fixName, [raw_name_1, raw_name_2])),
                )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("Tänzer, Mirko", "Mirko Tänzer"),
        ("Rische, Jan-Nick", "Jan-Nick Rische"),
        ("Kulhánek, Jakub", "Jakub Kulhánek"),
    ],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
