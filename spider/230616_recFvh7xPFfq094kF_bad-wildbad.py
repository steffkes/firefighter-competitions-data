import scrapy
from datetime import datetime
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = 230471
    race_key = "db2e71ebb35ebe73a4e50d8be4d6debb"

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
                "contest": "3",
                "listname": "Ergebnislisten|Ergebnisliste gesamt",
            },
            cb_kwargs={
                "competition_type": "OPA",
                "data_key": "#1_Feuerwehr-Stäffeleslauf",
            },
        )

    def parse(self, response, data_key, competition_type):
        for entry in response.json()["data"][data_key]:
            [
                bib,
                _,
                category,
                _,
                _,
                firstname,
                lastname,
                _,
                _,
                _,
                _,
                _,
                raw_duration,
                _,
                _,
            ] = entry

            duration = "00:%s.0" % raw_duration

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                bib=bib,
                type=competition_type,
                duration=duration,
                category=category.upper(),
                names=["%s %s" % (firstname, lastname)],
            )
