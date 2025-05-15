import scrapy
from datetime import datetime
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "315581"
    race_key = "f30e6a1c244e9e63717a97aead9fdb3a"

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
                "listname": "02_Teilnehmerlisten|Teilnehmer_Schanzenlauf",
                "contest": "1",
                "f": "<Ignore><Ignore>",
            },
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        for _team, record in response.json()["data"].items():
            [_bib1, _number21, name1, _sex1, _category1, _year1, _competition1] = (
                record[0]
            )

            name2 = None
            if len(record) == 2:
                [_bib2, _number22, name2, _sex2, _category2, _year2, _competition2] = (
                    record[1]
                )

            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(fixName, [name1, name2])),
            )


import re


def fixName(name):
    if not name:
        return ""

    return re.sub(
        r"(([A-ZÄÜÖß]+[-\s])?([A-ZÄÜÖß]+))\s(.+)",
        lambda match: " ".join(
            [
                match.group(4),
                "".join(
                    map(
                        lambda str: str[0] + str[1:].lower(),
                        filter(None, match.group(2, 3)),
                    )
                ),
            ]
        ),
        name,
    )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("HARTMANN Jörg", "Jörg Hartmann"),
        ("MÜLLER Naomi", "Naomi Müller"),
        ("KNIE Nicola Simon", "Nicola Simon Knie"),
        ("WEIßHAAR Philipp", "Philipp Weißhaar"),
        (None, ""),
    ],
)
def test_fixName(input, output):
    assert fixName(input) == output
