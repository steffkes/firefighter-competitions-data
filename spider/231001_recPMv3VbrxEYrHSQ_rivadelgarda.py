import scrapy
from datetime import datetime
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem
import re


class Spider(scrapy.spiders.CSVFeedSpider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    delimiter = ";"

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
        yield scrapy.Request("file:///app/analysis/spider/data/" + self.name + ".csv")

    def parse_row(self, response, row):
        [firstname, *lastname] = reversed(row["Name"].split(" "))
        names = map(lambda str: str[0] + str[1:].lower(), [firstname, *lastname])

        yield ResultItem(
            date=self.race_date,
            competition_id=self.competition_id,
            duration=row["Time"] + ".0",
            type="MPA",
            category=None,
            names=[" ".join(names)],
            bib=row["BIB"],
        )
