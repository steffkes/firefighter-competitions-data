import scrapy
from datetime import datetime
import re
import itertools
import string
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
            url="https://event.endu.net/events/event/entrants-json",
            formdata={"idevento": "100485", "rows": "200", "page": "1"},
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        for entry in response.json()["rows"]:
            [
                _empty,
                firstname,
                lastname,
                _year,
                _nation,
                _team,
                _empty2,
                _competiton,
            ] = entry["cell"]
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=["%s %s" % (firstname, lastname)],
            )
