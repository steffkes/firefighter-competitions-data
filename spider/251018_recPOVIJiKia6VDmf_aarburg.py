from util import Spider, ParticipantItem, ResultItem, ResultRankItem
from itertools import chain
import scrapy


class CompetitionSpider(Spider):
    name = __name__
    race_id = "323278"
    race_key = "430785aeb0c568f890e4c77f571f6728"

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
                "f": "<Ignore><Ignore>",
            },
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        for [_bib1, _bib2, name, _country, _yob, _gender, _category, _city] in list(
            chain.from_iterable(response.json()["data"].values())
        ):
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=[self.fixName(name)],
            )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [("Müller, Trix", "Trix Müller"), ("Kläy, Raphael", "Raphael Kläy")],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
