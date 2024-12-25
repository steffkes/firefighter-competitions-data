import scrapy
from datetime import datetime
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem
from itertools import batched


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
            url="https://runtix.com/sts/10050/2296/_team_1_ID2296P1/-/-",
            cb_kwargs={"competition_type": "MPA", "category": "M"},
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://runtix.com/sts/10050/2296/_team_2_ID2296P1/-/-",
            cb_kwargs={"competition_type": "MPA", "category": "M"},
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://runtix.com/sts/10050/2296/_team_3_ID2296P1/-/-",
            cb_kwargs={"competition_type": "MPA", "category": "X"},
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://runtix.com/sts/10050/2296/_team_4_ID2296P1/-/-",
            cb_kwargs={"competition_type": "MPA", "category": "W"},
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://runtix.com/sts/10050/2296/_team_5_ID2296P1/-/-",
            cb_kwargs={"competition_type": "OPA", "category": "X"},
        )

    def parse(self, response, competition_type, category):
        for meta, names in batched(response.css("table.results"), 2):
            duration = (
                meta.css(".col-team-time::text").get().split(" ")[1].replace(",", ".")
            )

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                duration=duration,
                type=competition_type,
                category=category,
                names=sorted(
                    names.css(".subsidiary .col-team-competitor::text").getall()
                ),
            )
