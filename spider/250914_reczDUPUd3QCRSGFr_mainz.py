import scrapy
import requests
from datetime import datetime
import re
import itertools
import string
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

    race_id = "332077"
    race_key = "2d3194e7534c122dfed9a1267726461c"

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
        contests = [
            (5, "MPA", "#1_Feuerwehr-Lauf mit PA"),
            (
                6,
                "OPA",
                "#1_Feuerwehr-Lauf ohne PA",
            ),
        ]

        for contest, _, data_key in contests:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "listname": "07 - Teilnehmer|Teilnehmerliste ABC Team",
                    "contest": str(contest),
                },
                callback=self.parse_starters,
                cb_kwargs={
                    "data_key": data_key,
                },
            )

        for contest, competition_type, data_key in [
            (5, "MPA", "#1_Feuerwehr-Lauf mit PA"),
            (
                6,
                "OPA",
                "#1_Feuerwehr-Lauf ohne PA",
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
                    "listname": "02 - Ergebnislisten|Mannschaftswertung Ges",
                    "contest": str(contest),
                },
                cb_kwargs={
                    "competition_type": competition_type,
                    "data_key": data_key,
                    "details": dict(map(lambda row: (row[1], row), r.json()["data"])),
                },
            )

    def parse_starters(self, response, data_key):
        fixName = lambda name: " ".join(reversed(list(map(str.strip, name.split(",")))))

        for [_id, _id2, _bib, _team, names, _category] in (
            response.json()["data"] or {}
        ).get(data_key, []):
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(fixName, names.split(" / "))),
            )

    def parse(self, response, data_key, competition_type, details):
        data = response.json()["data"]
        for entry in (data or {}).get(data_key, []):
            [_, status, bib, _, names, age_group, raw_duration] = entry

            if status == "DNF" or not raw_duration:  # disqualified
                continue

            [category, _] = age_group.split(" ")
            names = sorted(map(str.strip, names.split("/")))
            duration = "00:" + ("0" + raw_duration + ".0")[-7:]

            [
                _id,
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
            ] = details[bib]

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=competition_type,
                duration=duration,
                category={"MIX": "X"}.get(category, category),
                age_group=age_group,
                names=names,
                rank=ResultRankItem(
                    total=int(rank_total[:-1]),
                    category=int(rank_category[:-1]),
                    age_group=int(rank_age_group[:-1]),
                ),
                bib=bib,
            )
