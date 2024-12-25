import scrapy
from datetime import datetime
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "267314"
    race_key = "e9de69adb513973efb142494b4cf6628"

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
                "listname": "rr Timing|Teilnehmerliste_Feuerwehrlauf",
                "contest": "9",
            },
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "01_Baywa und Feuerwehr|Ergebnisliste_Feuerwehr_MW",
                "contest": "9",
            },
        )

    def parse_starters(self, response):
        fixName = lambda name: " ".join(reversed(list(map(str.strip, name.split(",")))))

        data = list(response.json()["data"].values())[0]
        for [_bib, _team, name1, name2, _byear1, _byear2, _gender1, _gender2] in data:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(fixName, [name1, name2])),
            )

    def parse(self, response):
        data = response.json()

        def handle(data, category):
            for team, entry in data.items():
                duration = "00:%s.0" % team.split("///")[-1]
                names = sorted(map(lambda record: fixName(record[2]), entry))

                yield ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type="OPA",
                    category=category,
                    duration=duration,
                    names=names,
                    bib=None,
                )

        yield from handle(data["data"]["#1_Männlich"], "M")
        yield from handle(data["data"]["#2_Weiblich"], "W")


import re


def fixName(name):
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
        ("HAUSCHILD Frederike", "Frederike Hauschild"),
        ("SCHULTHEIß Rebecca Regina", "Rebecca Regina Schultheiß"),
        ("MARTIN-WIDENHORN Andre", "Andre Martin-Widenhorn"),
        ("DE VITO Samuel", "Samuel De Vito"),
        ("HÖGER Ralph", "Ralph Höger"),
        ("ROßWAG Carsten", "Carsten Roßwag"),
    ],
)
def test_fixName(input, output):
    assert fixName(input) == output
