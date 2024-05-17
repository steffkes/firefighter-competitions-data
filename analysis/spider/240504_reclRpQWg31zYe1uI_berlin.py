import scrapy
from datetime import datetime
from scrapy.utils.iterators import csviter
from util import JsonItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.spiders.CSVFeedSpider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    tmp_bib = 1
    delimiter = ";"

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
        yield scrapy.Request(
            "file:///app/analysis/spider/data/240504_berlin_starter.csv",
            callback=self.parse_starters,
        )
        yield scrapy.Request("file:///app/analysis/spider/data/240504_berlin.csv")

    def parse_starters(self, response):
        fixName = lambda name: " ".join(reversed(name.split(", ")))
        for row in csviter(
            response, self.delimiter, self.headers, quotechar=self.quotechar
        ):
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(fixName, [row["name1"], row["name2"]])),
            )

    def parse_row(self, response, row):
        names = sorted(
            map(
                lambda name: " ".join(reversed(list(map(str.strip, name.split(","))))),
                [row["Name1"], row["Name2"]],
            )
        )

        yield ResultItem(
            date=self.race_date,
            competition_id=self.competition_id,
            bib=self.tmp_bib,
            type="MPA",
            duration="00:" + row["Time"][0:7],
            category={"Ladies": "W", "Mix": "X"}.get(row["Category"].strip(), "M"),
            names=names,
        )

        self.tmp_bib = self.tmp_bib + 1
