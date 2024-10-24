import scrapy
from datetime import datetime
import re
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = 313752
    race_key = "0d5ae0ee8152415c7321f52c9350c067"

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
        for contest in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "contest": str(contest),
                    "listname": "Online Ergebnisse und Listen|25 Teilnehmer nach Team",
                },
                callback=self.parse_starters,
            )

    def parse_starters(self, response):
        data = list((response.json()["data"] or {"dummy": []}).values())[0]
        for [_bib, _empty, _time, _team, _city, _origin, names, _category] in data:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(
                    map(
                        lambda name: re.match(r"^[^\(]+", name).group().strip(),
                        names.split(" / "),
                    )
                ),
            )
