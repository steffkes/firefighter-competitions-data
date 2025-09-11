from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__
    race_id = "328155"
    race_key = "f2b45a388c1b9035c1425887fbf67bda"

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
                "contest": "2",
            },
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        for [
            _id1,
            _id2,
            name,
            _origin,
            _yob,
            _gender,
            _category,
            _department,
            _starttime,
        ] in response.json()["data"]["#1_Burgstäffeleslauf Esslingen (Feuerwehr)"]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=[self.fixName(name)],
            )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [("Bopp, Marc", "Marc Bopp"), ("Mötzung, Erik", "Erik Mötzung")],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
