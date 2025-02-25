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
        for contest, type, gender in [
            ("G1M", "MPA", "M"),  # single male
            ("G1Z", "MPA", "W"),  # single female
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://remote.timingljubljana.si/stepup/Rezultati.aspx",
                formdata={"cat": contest},
                callback=self.parse_single,
                cb_kwargs={"type": type, "gender": gender},
            )

        for contest, type in [
            ("G3", "OPA"),  # relay mixed
            ("GE", "MPA"),  # relay mixed
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://remote.timingljubljana.si/stepup/Rezultati.aspx",
                formdata={"cat": contest},
                callback=self.parse_relay,
                cb_kwargs={"type": type},
            )

    def parse_single(self, response, type, gender):
        for row in response.css("table tr")[1:]:
            [rank, name, _country, _team, duration] = row.css("td ::text").getall()

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=type,
                duration="0" + duration,
                names=[fixName(name)],
                category=gender,
                rank=ResultRankItem(category=rank),
            )

    def parse_relay(self, response, type):
        for row in response.css("table tr")[1:]:
            [
                rank,
                names,
                _country,
                _team,
                duration1,
                duration2,
                duration3,
                _sum1_2,
                relay_duration,
            ] = row.css("td ::text").getall()

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=type,
                duration="0" + relay_duration,
                names=sorted(map(fixName, names.split(","))),
                category="Relay",
                rank=ResultRankItem(category=rank),
            )

            for name, duration in zip(
                names.split(","), [duration1, duration2, duration3]
            ):
                yield ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type=type,
                    duration="0" + duration,
                    names=[fixName(name.strip())],
                )


def fixName(name):
    parts = name.strip().split(" ")

    # last part goes first, assuming just one firstname
    parts.insert(0, parts.pop())

    return " ".join(map(lambda part: part[0].upper() + part[1:].lower(), parts))


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("BANOVEC JOŽEF", "Jožef Banovec"),
        ("ROGELJ OŽBEJ ROK", "Rok Rogelj Ožbej"),
        ("NOVAK TOBIJA ALJAŽ", "Aljaž Novak Tobija"),
        ("Hafner Urban", "Urban Hafner"),
        ("Hodža Frelih Matic", "Matic Hodža Frelih"),
        (" Bukovec Kren Ana", "Ana Bukovec Kren"),
    ],
)
def test_fixName(input, output):
    assert fixName(input) == output
