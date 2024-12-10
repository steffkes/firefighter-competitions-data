import scrapy
from datetime import datetime
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


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
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%d/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "contest": "5",
                "listname": "02 - Ergebnislisten|Mannschaftswertung Ges",
            },
            cb_kwargs={
                "competition_type": "MPA",
                "data_key": "#1_{DE:Feuerwehr-Team mit PA|EN:Firefighters with SCBA}",
            },
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%d/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "contest": "6",
                "listname": "02 - Ergebnislisten|Mannschaftswertung Ges",
            },
            cb_kwargs={
                "competition_type": "OPA",
                "data_key": "#1_{DE:Feuerwehr-Team ohne PA|EN:Firefighters without SCBA}",
            },
        )

    def parse(self, response, data_key, competition_type):
        for entry in response.json()["data"][data_key]:
            [_, _, bib, _, names, category, raw_duration] = entry

            [category, _] = category.split(" ")
            names = sorted(map(str.strip, names.split("/")))
            duration = "00:%s.0" % raw_duration.zfill(5)

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                bib=bib,
                type=competition_type,
                duration=duration,
                category={"MIX": "X"}.get(category, category),
                names=names,
            )
