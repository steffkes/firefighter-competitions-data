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
            url="https://www.dtiming.it/wp-content/glive-results/glof-2024/GARDA%20LIFT%20ON%20FIRE.clax",
        )

    def parse(self, response):
        durations = dict(
            map(
                lambda entry: (entry.attrib["d"], entry.attrib["t"]),
                response.css("Resultats R"),
            )
        )

        for entry in response.css("Engages E"):
            raw_duration = durations.get(entry.attrib["d"])

            if not raw_duration:
                continue

            [firstname, lastname] = reversed(
                list(map(lambda str: str.strip(), entry.attrib["n"].split("\xa0")))
            )
            duration = re.sub(
                r"^(00)h(\d{2})'(\d{2}),(\d)\d*$", r"\1:\2:\3.\4", raw_duration
            )

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                duration=duration,
                type="MPA",
                category={"M": "M", "F": "W"}.get(entry.attrib["x"]),
                names=[
                    " ".join(
                        [
                            firstname,
                            re.sub(
                                r"^(.)(.+)$",
                                lambda match: "%s%s"
                                % (match.group(1), match.group(2).lower()),
                                lastname,
                            ),
                        ]
                    )
                ],
                bib=entry.attrib["d"],
            )
