import scrapy
from datetime import datetime
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = 313752
    race_key = "0d5ae0ee8152415c7321f52c9350c067"

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
