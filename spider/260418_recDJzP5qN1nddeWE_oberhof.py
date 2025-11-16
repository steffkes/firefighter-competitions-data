from util import Spider, ParticipantItem, ResultItem, ResultRankItem, SlotItem
from itertools import batched
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__
    race_id = 362068
    race_key = "378d16dcd5e34cfc336ebeaf786aabf2"

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Online Ergebnisse und Listen|26 Teilnehmer Team",
            },
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRRegStart/data/config" % self.race_id,
            callback=self.parse_slots,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Online Ergebnisse und Listen|05 Ergebnisse Team ALLE WK",
            },
        )

    def parse_slots(self, response):
        yield SlotItem(
            competition_id=self.competition_id,
            amount=int(
                response.json()["RegistrationConfig"]["Registrations"][1]["SlotsLeft"]
                / 2
            ),
        )

    def parse_starters(self, response):
        for [
            _number1,
            _number2,
            _time,
            _team,
            _nationality,
            _department,
            _category,
            names,
            _ages,
        ] in response.json()["data"]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=extractNames(names),
            )

    def parse(self, response):
        data = response.json()["data"]
        for entry in data:
            [bib, _, _, _, _, _, raw_duration, names, _, raw_age_group] = entry

            # it's basically everything without a breathing apparatus
            # also no gear on the back .. no rules at all?
            if raw_age_group == "MIXO":
                continue

            duration = "00:" + raw_duration.split(" ")[0].replace(",", ".")
            names = sorted(
                map(
                    lambda name: " ".join(name.strip().split(" ")[:-1]),
                    names.split(" / "),
                )
            )

            category = {"MIX": "X", "MIXO": "X", "LADIES": "W"}.get(raw_age_group, "M")
            age_group = raw_age_group.split("-")[0] if category == "M" else None

            result = ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="MPA" if raw_age_group[-1:] != "O" else "OPA",
                duration=duration,
                names=names,
                category=category,
                rank=ResultRankItem(
                    total=self.ranks.get("total", 1),
                    category=self.ranks["category"].get(category, 1),
                ),
                bib=bib,
            )

            if age_group:
                result["rank"]["age_group"] = self.ranks["age_group"].get(age_group, 1)
                result["age_group"] = age_group

            yield result

            self.ranks["total"] = result["rank"]["total"] + 1
            self.ranks["category"][category] = result["rank"]["category"] + 1

            if "age_group" in result["rank"]:
                self.ranks["age_group"][age_group] = result["rank"]["age_group"] + 1


import re


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
            "Damian Pyka (ML/1975) / Jasmin Bohun (WL/1989)",
            ["Damian Pyka", "Jasmin Bohun"],
        ),
        (
            "Jörg Bohun (ML/1981) / Benjamin Schrader (ML/1985)",
            ["Benjamin Schrader", "Jörg Bohun"],
        ),
        (
            "Jasmin Bohun (WL/1989) / Bianca Schrader (WL/1990)",
            ["Bianca Schrader", "Jasmin Bohun"],
        ),
    ],
)
def test_extractNames(input, output):
    assert extractNames(input) == output
