import scrapy
from datetime import datetime
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "233380"
    race_key = "60cc4a4284fd80a91ac2abbea60e10ed"

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
                "contest": "5",
                "listname": "02 - Ergebnislisten|Ergebnisliste MW - Team",
            },
            cb_kwargs={
                "competition_type": "MPA",
                "data_key": "#1_{DE:Feuerwehr-Team mit PA|EN:Firefighters team with SCBA}",
            },
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "contest": "6",
                "listname": "02 - Ergebnislisten|Ergebnisliste MW - Team",
            },
            cb_kwargs={
                "competition_type": "OPA",
                "data_key": "#1_{DE:Feuerwehr-Team ohne PA|EN:Firefighters team without SCBA}",
            },
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
