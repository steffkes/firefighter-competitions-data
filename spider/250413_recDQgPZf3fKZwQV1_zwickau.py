import scrapy
from datetime import datetime
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "322261"
    race_key = "08e70f5a3af5efda8835286bd20fc249"

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
                "listname": "Teilnehmerlisten|Teilnehmerliste Feuerwehr",
                "contest": "2",
            },
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Ergebnislisten|Feuerwehr AK",
                "contest": "2",
            },
            cb_kwargs={"data_key": "#1_Feuerwehr-Treppenlauf-Zwickau"},
        )

    def parse_starters(self, response):
        for [_bib, _number2, _team, _gender, names] in response.json()["data"]:
            yield ParticipantItem(
                competition_id=self.competition_id, names=fixNames(names)
            )

    def parse(self, response, data_key):
        data = response.json()["data"]
        for entry in (
            data[data_key]["#1_w"]["#1_"]
            + data[data_key]["#2_m"]["#2_"]
            + data[data_key]["#3_a"]["#3_"]
        ):
            [bib, _, _, _, _, _, names, raw_duration] = entry

            names = sorted(list(map(str.strip, re.split(r"[/,]", names))))
            duration = "00:" + raw_duration.replace(",", ".")

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                bib=bib,
                type="OPA",
                category=None,
                duration=duration,
                names=names,
            )


import re


def fixNames(raw_names):
    names = raw_names.split("/")

    if len(names) == 1:
        names = re.split(r"\s{2,}", raw_names)

    if len(names) == 1:
        names = raw_names.split(",")

    return sorted(list(map(str.strip, names)))


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        (
            "Strobel, Patrick     Brummer, Justin",
            ["Brummer, Justin", "Strobel, Patrick"],
        ),
        (
            "Wittig, Johannes      Brosius, Marius",
            ["Brosius, Marius", "Wittig, Johannes"],
        ),
        ("Hagen Scherer, Ronny Becker", ["Hagen Scherer", "Ronny Becker"]),
        ("Schubert Toni, Windisch Rick", ["Schubert Toni", "Windisch Rick"]),
        ("Alexander, Höhne / Rene, Richter", ["Alexander, Höhne", "Rene, Richter"]),
        ("Anja Werner / Julia Drews", ["Anja Werner", "Julia Drews"]),
    ],
)
def test_fixNames(input, output):
    assert fixNames(input) == output
