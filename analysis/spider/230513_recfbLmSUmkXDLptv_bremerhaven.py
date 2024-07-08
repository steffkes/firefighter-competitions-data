import scrapy
from datetime import datetime
import re
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


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
            "../data/teams/%(ident)s.json": {
                "format": "starter",
                "encoding": "utf8",
                "overwrite": True,
                "item_classes": [ParticipantItem],
            },
            "data/teams/%(name)s.jsonl": {
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
            url="https://www.firefighter-challenge-germany.de/ergebnisse/",
        )

    def parse(self, response):

        def handler(table, type, category):
            for row in table.css("tbody tr"):
                if not row.css(".place::text").get().isnumeric():
                    continue

                names = sorted(
                    filter(
                        bool, map(str.strip, row.css(".member::text").get().split(","))
                    )
                )
                duration = "00:" + row.css(".totaltime::text").get()

                yield ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type=type,
                    category=category,
                    duration=duration,
                    names=names,
                )

        yield from handler(
            table=response.xpath(
                "//div[@data-target='results-11' and @data-targetid='MG']"
            ),
            type="MPA",
            category="M",
        )

        yield from handler(
            table=response.xpath(
                "//div[@data-target='results-11' and @data-targetid='WG']"
            ),
            type="MPA",
            category="W",
        )

        yield from handler(
            table=response.xpath(
                "//div[@data-target='results-11' and @data-targetid='TM']"
            ),
            type="OPA",
            category="M",
        )

        yield from handler(
            table=response.xpath(
                "//div[@data-target='results-11' and @data-targetid='TF']"
            ),
            type="OPA",
            category="F",
        )

        yield from handler(
            table=response.xpath(
                "//div[@data-target='results-11' and @data-targetid='TMIX']"
            ),
            type="OPA",
            category="X",
        )
