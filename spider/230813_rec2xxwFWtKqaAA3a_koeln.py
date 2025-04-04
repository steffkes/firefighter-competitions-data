import scrapy
from datetime import datetime
import requests
from util import (
    JsonItemExporter,
    JsonLinesItemExporter,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
)

changedParticipants = {"Stefan Mathwis": "Stefan Matheis"}


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = 230957
    race_key = "d54a3e373b8e4dfe0af5091281fe9ce2"

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
                    "listname": "07 - Teilnehmer|Teilnehmerliste ABC Team",
                    "contest": str(contest),
                },
                callback=self.parse_starters,
            )

        for contest, competition_type, data_key in [
            (5, "MPA", "#1_{DE:Feuerwehr-Team mit PA|EN:Firefighters with SCBA}"),
            (
                6,
                "OPA",
                "#1_{DE:Feuerwehr-Team ohne PA|EN:Firefighters without SCBA}",
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
                    "contest": str(contest),
                    "listname": "02 - Ergebnislisten|Mannschaftswertung Ges",
                },
                cb_kwargs={
                    "competition_type": competition_type,
                    "data_key": data_key,
                    "details": dict(map(lambda row: (row[0], row), r.json()["data"])),
                },
            )

    def parse_starters(self, response):
        fixName = lambda name: " ".join(reversed(list(map(str.strip, name.split(",")))))

        data = list(response.json()["data"].values())[0]
        for [_bib, _id, _id2, _team, names, _category] in data:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(fixName, names.split(" / "))),
            )

    def parse(self, response, data_key, competition_type, details):
        fixName = lambda name: changedParticipants.get(name.strip(), name.strip())

        for entry in response.json()["data"][data_key]:
            [id, _id2, _rank, bib, _, names, age_group, raw_duration] = entry

            [category, _] = age_group.split(" ")
            names = sorted(map(fixName, names.split("/")))
            duration = "00:%s.0" % raw_duration.zfill(5)

            [
                _id,
                _id2,
                _bib,
                _person1,
                _person2,
                _team,
                _unknown,
                _unknown,
                _label1,
                _label2,
                _label3,
                _label4,
                _contest,
                _duration,
                _speed,
                rank_total,
                rank_category,
                rank_age_group,
            ] = details[id]

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                duration=duration,
                type=competition_type,
                category={"MIX": "X"}.get(category, category),
                names=names,
                age_group=age_group,
                rank=ResultRankItem(
                    total=int(rank_total[:-1]),
                    category=int(rank_category[:-1]),
                    age_group=int(rank_age_group[:-1]),
                ),
                bib=bib,
            )
