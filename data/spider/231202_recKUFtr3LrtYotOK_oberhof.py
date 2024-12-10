import scrapy
from datetime import datetime
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
            url="https://timing.sportident.com/de/results/2023/xmas-stairrun/course-a/overall",
        )

    category_map = {
        "Männerteam": "M",
        "Männerteam 80": "M",
        "Männerteam 100": "M",
        "Frauenteam": "W",
        "Mixteam": "X",
    }

    def parse(self, response):
        for row in response.css("#refresh table tbody tr"):
            category = row.css("td:nth-child(5)::text").get()
            if category not in self.category_map:
                continue

            # disqualified or no time given
            if row.css("td:nth-child(1)::text").get().strip() in ["NPL", ""]:
                continue

            bib = row.css("td:nth-child(2)::text").get()
            duration = "00:" + row.css("td:nth-child(6) b::text").get().zfill(
                8
            ).replace(",", ".")
            names = sorted(
                map(
                    str.strip,
                    row.css("td:nth-child(3) div::text")
                    .get()
                    .replace(",", "")
                    .split(" und "),
                )
            )

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                bib=bib,
                type="MPA",
                duration=duration,
                category=self.category_map[category],
                names=names,
            )
