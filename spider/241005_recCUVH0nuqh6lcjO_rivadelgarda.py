import scrapy
from datetime import datetime
from util import (
    JsonItemExporter,
    JsonLinesItemExporter,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
)

nameMappings = {"Hindelang Günther": "Günther Hindelang"}


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    ranks = {"total": 1, "category": {"M": 1, "W": 1}}

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
            url="https://www.dtiming.it/wp-content/glive-results/glof-2024/GARDA%20LIFT%20ON%20FIRE.clax",
        )

    def parse(self, response):
        entries = dict(
            map(
                lambda entry: (entry.attrib["d"], entry),
                response.css("Engages E"),
            )
        )

        for result in response.css("Resultats R"):
            entry = entries[result.attrib["d"]]

            duration = fixDuration(result.attrib["t"])
            bib = result.attrib["d"]
            category = {"M": "M", "F": "W"}.get(entry.attrib["x"])

            if not duration:
                continue

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                duration=duration,
                type="MPA",
                category=category,
                names=[fixName(entry.attrib["n"])],
                rank=ResultRankItem(
                    total=self.ranks["total"], category=self.ranks["category"][category]
                ),
                bib=bib,
            )

            self.ranks["total"] += 1
            self.ranks["category"][category] += 1


import re


def fixDuration(raw_duration):
    if raw_duration == "Squalificato":
        return None

    return re.sub(r"^(00)h(\d{2})'(\d{2}),(\d)\d*$", r"\1:\2:\3.\4", raw_duration)


def fixName(name):
    [firstname, lastname] = reversed(
        list(map(lambda str: str.strip(), name.split("\xa0")))
    )

    fixed = " ".join(
        [
            firstname,
            re.sub(
                r"^(.)(.+)$",
                lambda match: "%s%s" % (match.group(1), match.group(2).lower()),
                lastname,
            ),
        ]
    )

    return nameMappings.get(fixed, fixed)


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("00h07'23,4", "00:07:23.4"),
        ("00h08'52,3", "00:08:52.3"),
        ("00h12'49,6", "00:12:49.6"),
        ("Squalificato", None),
    ],
)
def test_fixDuration(input, output):
    assert fixDuration(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        ("KOCH Petra", "Petra Koch"),
        ("FICILI Orso Mario Bartolomeo", "Orso Mario Bartolomeo Ficili"),
        ("WEISS Anne-Kathrin", "Anne-Kathrin Weiss"),
        ("GÜNTHER Hindelang", "Günther Hindelang"),
    ],
)
def test_fixName(input, output):
    assert fixName(input) == output
