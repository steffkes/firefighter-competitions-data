import scrapy
from datetime import datetime


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
        yield scrapy.Request("file:///app/spider/data/240504_berlin.csv")

    def parse_row(self, response, row):
        names = sorted(
            map(
                lambda name: " ".join(reversed(list(map(str.strip, name.split(","))))),
                [row["Name1"], row["Name2"]],
            )
        )

        yield {
            "date": self.race_date,
            "competition_id": self.competition_id,
            "bib": self.tmp_bib,
            "type": "MPA",
            "duration": "00:" + row["Time"][0:7],
            "category": {"Ladies": "W", "Mix": "X"}.get(row["Category"].strip(), "M"),
            "names": names,
        }

        self.tmp_bib = self.tmp_bib + 1
