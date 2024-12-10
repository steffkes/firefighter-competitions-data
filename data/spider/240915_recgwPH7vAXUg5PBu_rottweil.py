import scrapy
from datetime import datetime
import re
import itertools
import string
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "281781"
    race_key = "1a92069df75cc5903748fe12993e7e8b"

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
        for contest in [5, 6]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "listname": "07 - Teilnehmer - PUBLIC|Teilnehmer ABC-Team",
                    "contest": str(contest),
                },
                callback=self.parse_starters,
            )

        for contest, competition_type, data_key in [
            (5, "MPA", "#1_{DE:Feuerwehr-Team mit PA|EN:Firefighters team with SCBA}"),
            (
                6,
                "OPA",
                "#1_{DE:Feuerwehr-Team ohne PA|EN:Firefighters team without SCBA}",
            ),
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "listname": "02 - Ergebnislisten|Ergebnisliste MW - Team",
                    "contest": str(contest),
                },
                cb_kwargs={
                    "competition_type": competition_type,
                    "data_key": data_key,
                },
            )

    def parse_starters(self, response):
        data = response.json()["data"]
        for [_id, _bib, _team, names, _category] in data:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(names.split(" / ")),
            )

    def parse(self, response, data_key, competition_type):
        data = response.json()["data"]
        for entry in (
            data[data_key]["#1_Männer"]
            + data[data_key]["#2_Frauen"]
            + data[data_key]["#3_Mixed"]
        ):
            [_, status, bib, names, category, _, raw_duration] = entry

            if status == "DNF" or not raw_duration:  # disqualified
                continue

            [category, _] = category.split(" ")
            names = sorted(map(str.strip, names.split("/")))
            duration = ("0" + ("0:" + raw_duration + ".0")[-9:])[-11:]

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                bib=bib,
                type=competition_type,
                category={"MIX": "X"}.get(category, category),
                duration=duration,
                names=names,
            )
