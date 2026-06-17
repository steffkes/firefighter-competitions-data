from util import Spider, ParticipantItem, ResultItem, ResultRankItem, SlotItem
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__

    race_id = "390000"
    race_key = "0c21e59064c276fcec3b05571c805496"

    @staticmethod
    def fixName(name):
        return " ".join(reversed(name.split(", ")))

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/participants/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Teilnehmerlisten|TN ABC",
                "contest": "6",
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
            amount=response.json()["Registrations"][0]["SlotsLeft"],
        )

    def parse_starters(self, response):
        for [
            _bib,
            _id,
            raw_name,
            _category,
            _age_group,
            _department,
            _event,
        ] in response.json()["data"]:
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
