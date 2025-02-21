import scrapy
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

    race_id = "271276"
    race_key = "353bdf54f57af48fa0d1af824aa6e860"

    ranks = {"category": {}}

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
                "listname": "Online|Teilnehmerliste ABC",
                "contest": str(3),
            },
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Online|Zieleinlaufliste",
                "contest": "3",
            },
            cb_kwargs={"data_key": "#1_Feuerwehr-Stäffeleslauf"},
        )

    def parse_starters(self, response):
        fixName = lambda name: " ".join(reversed(list(map(str.strip, name.split(",")))))

        data = list(response.json()["data"].values())[0]
        for [
            _bib,
            _bib2,
            name,
            _nationality,
            _byear,
            _gender,
            _category,
            _team,
            _empty,
        ] in data:
            yield ParticipantItem(
                competition_id=self.competition_id, names=[fixName(name)]
            )

    def parse(self, response, data_key):
        for [
            bib,
            _bib2,
            _rank,
            name,
            _nationality,
            _byear,
            category,
            _gender_full,
            team,
            raw_duration,
            _time_difference,
        ] in response.json()["data"][data_key]:
            duration = "00:%s.0" % raw_duration

            rank_total = self.ranks.get("total", 1)
            rank_category = self.ranks["category"].get(category, 1)

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="OPA",
                duration=duration,
                names=[name],
                category=category,
                rank=ResultRankItem(total=rank_total, category=rank_category),
                bib=bib,
            )

            self.ranks["total"] = rank_total + 1
            self.ranks["category"][category] = rank_category + 1
