import scrapy
from datetime import datetime
from pathlib import Path
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.spiders.CSVFeedSpider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    delimiter = ","

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
            method="POST",
            url="https://www.whatsmytimeresults.co.uk/results.aspx?CId=17047&RId=6275",
            formdata={"__EVENTTARGET": "ctl00$Content_Main$btnCSV"},
        )

    def parse_row(self, response, row):
        if row["Time"] == "DNF":
            return

        yield ResultItem(
            date=self.race_date,
            competition_id=self.competition_id,
            type="MPA",
            duration=row["Time"][0:10],
            category=row["Gender"][0],
            names=[row["Name"]],
        )
