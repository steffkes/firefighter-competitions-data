import scrapy
from datetime import datetime
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem
import re


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

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
            url="https://firefit-europe.eu/ranking-siegertsbrunn-2023/",
        )

    def parse(self, response):
        categories = ["M", "W", "M", "W", "X", "M", "W", "X"]

        for index, table in enumerate(
            response.css("table.ffc-table-dark")[0 : len(categories)]
        ):
            for row in table.css("tbody tr.status-ok"):
                names = [row.css(".name-line1::text").get().strip()]
                duration = "00:0" + "".join(
                    row.css(".result-line1 span::text").getall()
                ).replace(",", ".")

                team = sorted(row.css(".member-name span::text").getall())
                if len(team):
                    names = team

                yield ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type={0: "MPA", 1: "MPA"}.get(index, "OPA"),
                    category=categories[index],
                    duration=duration,
                    names=names,
                )
