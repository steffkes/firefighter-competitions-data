import scrapy
from datetime import datetime
from pathlib import Path
from scrapy.utils.iterators import csviter
from util import (
    JsonItemExporter,
    JsonLinesItemExporter,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
)


class Spider(scrapy.spiders.CSVFeedSpider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    delimiter = ","

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
        yield scrapy.Request(
            "file://%s"
            % Path("spider/data/240630_rech2HGehAQ1qcF77_wilhelmsfeld.csv").resolve()
        )

    def parse_row(self, response, row):
        yield ResultItem(
            date=self.race_date,
            competition_id=self.competition_id,
            type="MPA",
            duration="00:" + row["Laufzeit"][0:7].replace(",", "."),
            category={"Herr": "M", "Frau": "W"}.get(row["m/w"]),
            names=[("%s %s" % (row["Vorname"], row["Name"])).strip()],
            rank=ResultRankItem(
                total=int(row["Platz"]), category=int(row["Platz m/w"])
            ),
            bib=row["Start.Nr."],
        )
