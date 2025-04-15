import scrapy
from datetime import datetime
import re
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

    race_id = "275363"
    race_key = "2763c5212a432a43da74006d8553cbcb"

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
        for [_bib, _team, _unknown, _gender, names] in response.json()["data"]:
            names = sorted(list(map(str.strip, re.split(r"[/,]", names))))
            if len(names) == 2:
                yield ParticipantItem(competition_id=self.competition_id, names=names)

    def parse(self, response, data_key):
        data = response.json()["data"]
        results = []

        for entry in data[data_key]["#1_m"]["#1_"] + data[data_key]["#2_a"]["#2_"]:
            [bib, _, rank_category, _, _, raw_category, names, raw_duration] = entry

            names = sorted(list(map(str.strip, re.split(r"[/,]", names))))
            duration = "00:" + raw_duration.replace(",", ".")

            results.append(
                ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type="MPA",
                    duration=duration,
                    names=names,
                    category={"Männer": "M", "Frauen": "W", "Mixed": "X"}[raw_category],
                    rank=ResultRankItem(category=int(rank_category[0:-1])),
                    bib=bib,
                )
            )

        durations = sorted(map(lambda result: result["duration"], results))

        for result in results:
            result["rank"]["total"] = durations.index(result["duration"]) + 1
            yield result
