import scrapy
from datetime import datetime
import re
import itertools
import string
from util import JsonItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "271276"
    race_key = "353bdf54f57af48fa0d1af824aa6e860"

    custom_settings = {
        "FEED_EXPORTERS": {"starter": JsonItemExporter},
        "FEEDS": {
            "../data/teams/%(ident)s.json": {
                "format": "starter",
                "encoding": "utf8",
                "overwrite": True,
                "item_classes": [ParticipantItem],
            },
            "data/teams/%(name)s.jsonl": {
                "format": "jsonlines",
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
                "listname": "Online|Teilnehmerliste ABC",
                "contest": str(3),
            },
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        fixName = lambda name: " ".join(reversed(list(map(str.strip, name.split(",")))))

        data = list(response.json()["data"].values())[0]
        for [
            _bib,
            _bib2,
            name,
            _nationality,
            _byear,
            _gender,
            _category,
            _team,
        ] in data:
            yield ParticipantItem(
                competition_id=self.competition_id, names=[fixName(name)]
            )
