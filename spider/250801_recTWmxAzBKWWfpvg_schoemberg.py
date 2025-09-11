import scrapy
from datetime import datetime
from util import Spider, ParticipantItem, ResultItem


class CompetitionSpider(Spider):
    name = __name__

    race_id = "314379"
    race_key = "5dfc4e446d96c06bd1addb9630b6273d"

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "rr Timing|Teilnehmerliste_Feuerwehrlauf",
                "contest": "9",
            },
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        data = list(response.json()["data"].values())[0]
        for [
            _bib,
            _number2,
            _team,
            name1,
            name2,
            _byear1,
            _byear2,
            _gender1,
            _gender2,
        ] in data:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(fixName, [name1, name2])),
            )


def fixName(name):
    return " ".join(reversed(list(map(str.strip, name.split(",")))))


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("Wetzel, Denise", "Denise Wetzel"),
        ("Julia, Keller", "Keller Julia"),
    ],
)
def test_fixName(input, output):
    assert fixName(input) == output
