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
        yield scrapy.FormRequest(
            method="GET",
            url="https://firefit-europe.eu/ranking-tauberfeld-2024/",
        )

    def parse(self, response):
        parties = [
            ("M", "MPA", False),  # ·
            ("W", "MPA", False),  # ↳ individual
            ("M", "OPA", False),  # ·
            ("W", "OPA", False),  # ·
            ("X", "OPA", False),  # ↳ tandem
            ("M", "OPA", True),  # ·
            ("X", "OPA", True),  # ↳ relay
        ]

        results = response.css("table.ffc-table-dark")
        relayTeams = {}

        computeDuration = lambda parts: "00:0" + "".join(parts).replace(",", ".")

        for index, (category, type, isRelay) in enumerate(parties):
            for row in results[index].css("tbody tr.status-ok"):
                names = [row.css(".name-line1::text").get().strip()]
                duration = computeDuration(row.css(".result-line1 span::text").getall())

                team = sorted(row.css(".member-name span::text").getall())
                if len(team):
                    names = team

                if isRelay:
                    relayTeams[row.css(".name .name-line1::text").get().strip()] = (
                        category,
                        type,
                        names,
                    )

                yield ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type=type,
                    category=category,
                    duration=duration,
                    names=names,
                )

        for ematch in response.css(".elimination-match .opponent"):
            (category, type, names) = relayTeams[
                ematch.css(".name ::text").get().strip()
            ]
            rawDuration = ematch.css(".result .ffc-color-success span::text").getall()

            # most likely disqualified
            if not len(rawDuration):
                continue

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=type,
                category=category,
                duration=computeDuration(rawDuration),
                names=names,
            )
