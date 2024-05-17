import scrapy
from datetime import datetime
from pathlib import Path


class Spider(scrapy.spiders.CSVFeedSpider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]

    tmp_bib = 1
    delimiter = ";"

    custom_settings = {
        "FEEDS": {
            "data/teams/%(name)s.jsonl": {
                "format": "jsonlines",
                "encoding": "utf8",
                "overwrite": True,
            }
        }
    }

    def start_requests(self):
        yield scrapy.Request(
            "file://%s" % Path("spider/data/230506_berlin.csv").resolve()
        )

    def parse_row(self, response, row):
        names = sorted(
            map(
                lambda name: " ".join(reversed(list(map(str.strip, name.split(","))))),
                row["Name"].split("/"),
            )
        )

        yield {
            "date": self.race_date,
            "competition_id": self.competition_id,
            "bib": self.tmp_bib,
            "type": "MPA",
            "duration": "00:" + row["Duration"].zfill(7),
            "category": None,
            "names": names,
        }

        self.tmp_bib = self.tmp_bib + 1
