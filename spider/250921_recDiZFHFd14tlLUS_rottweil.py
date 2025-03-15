import scrapy
from datetime import datetime
import re
import itertools
import string
import requests
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

    race_id = "326961"
    race_key = "cea1bfecebe76305675f5af5f93c2fb0"

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
            r = requests.get(
                "https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                params={
                    "key": self.race_key,
                    "listname": "01 - Detail|Details Team",
                    "contest": str(contest),
                },
            )

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
                    "details": dict(map(lambda row: (row[0], row), r.json()["data"])),
                },
            )

    def parse_starters(self, response):
        data = response.json()["data"]
        for [_id, _id2, _bib, _team, names, _category] in data:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(names.split(" / ")),
            )

    def parse(self, response, data_key, competition_type, details):
        data = (response.json()["data"] or {}).get(data_key, {})
        for entry in (
            data.get("#1_Männer", [])
            + data.get("#2_Frauen", [])
            + data.get("#3_Mixed", [])
        ):
            [id, _id2, status, bib, names, age_group, _, raw_duration] = entry

            if status in ["DNF", "a.k."] or not raw_duration:  # disqualified
                continue

            [category, _] = age_group.split(" ")
            names = sorted(map(str.strip, names.split("/")))
            duration = ("0" + ("0:" + raw_duration + ".0")[-9:])[-11:]

            [
                _id,
                _id2,
                _bib,
                _person1,
                _person2,
                _team,
                _org,
                _unknown,
                _label1,
                _label2,
                _label3,
                _label4,
                _contest,
                _time,
                _speed,
                rank_total,
                rank_category,
                rank_age_group,
            ] = details[id]

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=competition_type,
                duration=duration,
                names=names,
                category={"MIX": "X"}.get(category, category),
                age_group=age_group,
                rank=ResultRankItem(
                    total=int(rank_total[:-1]),
                    category=int(rank_category[:-1]),
                    age_group=int(rank_age_group[:-1]),
                ),
                bib=bib,
            )
