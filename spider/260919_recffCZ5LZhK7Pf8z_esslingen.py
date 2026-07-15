from util import Spider, ParticipantItem, ResultItem, ResultRankItem, SlotItem
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__

    race_id = "390598"
    race_key = "29f7c11f25026655e72475822aa62038"

    @staticmethod
    def fixName(name):
        return " ".join(reversed(name.split(", ")))

    def start_requests(self):
        for key, group in [
            ("#3", "Startgruppe 4(Feuerwehr ohne angeschlossener PA)"),
            ("#4", "Startgruppe 5(Feuerwehr mit angeschlossener PA)"),
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/participants/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "listname": "Online|Teilnehmer",
                    "f": group + "<Ignore><Ignore>",
                },
                cb_kwargs={"key": key + "_" + group},
                callback=self.parse_starters,
            )

    def parse_starters(self, response, key):
        for [
            _,
            _,
            _,
            raw_name,
            _nationality,
            _yob,
            _category,
            _age_group,
            _department,
        ] in response.json()["data"][key]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=[self.fixName(raw_name)],
            )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("Endres, Andreas", "Andreas Endres"),
        ("Kühn, Stefan", "Stefan Kühn"),
    ],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
