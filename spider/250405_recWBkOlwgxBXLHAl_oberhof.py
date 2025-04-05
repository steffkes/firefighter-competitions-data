import scrapy
from datetime import datetime
from util import (
    JsonItemExporter,
    JsonLinesItemExporter,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
)


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = 313752
    race_key = "0d5ae0ee8152415c7321f52c9350c067"

    ranks = {"category": {}, "age_group": {}}

    custom_settings = {
        "FEED_EXPORTERS": {
            "starter": JsonItemExporter,
            "results": JsonLinesItemExporter,
        },
        "FEEDS": {
            "data/participants/%(ident)s.json": {
                "format": "starter",
                "encoding": "utf8",
                "overwrite": True,
                "item_classes": [ParticipantItem],
            },
            "data/results/%(name)s.jsonl": {
                "format": "results",
                "encoding": "utf8",
                "overwrite": True,
                "item_classes": [ResultItem],
            },
        },
        "EXTENSIONS": {
            "scrapy.extensions.telnet.TelnetConsole": None,
        },
    }

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
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Online Ergebnisse und Listen|05 Ergebnisse Team ALLE WK",
            },
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
