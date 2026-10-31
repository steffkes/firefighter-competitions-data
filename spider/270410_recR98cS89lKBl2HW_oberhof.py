from util import Spider, ParticipantItem, SlotItem
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__
    race_id = 413421
    race_key = "3d266a45b203e0915f3b6bfb008648ed"

    def start_requests(self):
        # teams only, the separate "SOLO RUN" (contest 10) is a regular stair run
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/participants/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "02: Online Ergebnisse und Listen|26b Teilnehmer Team",
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
        registration = next(
            registration
            for registration in response.json()["Registrations"]
            if registration["Name"] == "02 Anmeldung - Team"
        )

        # slots are counted per person, two persons per team
        yield SlotItem(
            competition_id=self.competition_id,
            amount=int(registration["SlotsLeft"] / 2),
        )

    def parse_starters(self, response):
        for [
            _bib,
            _id,
            _nationality,
            _team,
            _department,
            names,
            _age,
        ] in response.json()["data"]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=extractNames(names),
            )


def extractNames(names):
    return sorted(
        map(
            lambda name: re.match(r"^[^\(]+", name).group().strip(),
            names.split(" / "),
        )
    )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        (
            "Alexander Kitz (ML/2007) / Leo Siebeneichler (ML/2002)",
            ["Alexander Kitz", "Leo Siebeneichler"],
        ),
        (
            "Mathias Siebold (ML/1988) / Christian Windel (ML/1977)",
            ["Christian Windel", "Mathias Siebold"],
        ),
    ],
)
def test_extractNames(input, output):
    assert extractNames(input) == output
