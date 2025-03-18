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
        for contest in [10215, 10216]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://www.anmeldungs-service.de/module/teilnehmer/staffel_cache.php",
                formdata={
                    "wettid": str(contest),
                    "totalrows": "2000",
                },
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                },
                callback=self.parse_starters,
            )

    def parse_starters(self, response):
        reverseName = lambda name: " ".join(
            reversed(list(map(str.strip, name.split(" "))))
        )
        fixName = lambda name: reverseName(
            re.match(r"^(.+)\s+\w\s+\d+$", name).group(1).strip()
        )

        data = response.json().get("rows", [])
        for entry in data:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(fixName, entry["cell"]["name"].split("<br>"))),
            )
