import scrapy
from datetime import datetime
import re


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]

    custom_settings = {
        "FEEDS": {
            "data/teams/%(name)s.jsonl": {
                "format": "jsonlines",
                "encoding": "utf8",
                "overwrite": True,
            }
        },
        "EXTENSIONS": {
            "scrapy.extensions.telnet.TelnetConsole": None,
        },
    }

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://firefit-europe.eu/ranking-dortmund-2023/",
        )

    def parse(self, response):
        categories = ["M", "W", "M", "W", "X", "M", "W", "X"]

        for index, table in enumerate(
            response.css("table.ffc-table-dark")[0 : len(categories)]
        ):
            for row in table.css("tbody tr.status-ok"):
                names = [row.css(".name-line1::text").get().strip()]
                duration = "00:0" + "".join(
                    row.css(".result-line1 span::text").getall()
                ).replace(",", ".")

                team = sorted(row.css(".member-name span::text").getall())
                if len(team):
                    names = team

                yield {
                    "date": self.race_date,
                    "competition_id": self.competition_id,
                    "type": {0: "MPA", 1: "MPA"}.get(index, "OPA"),
                    "category": categories[index],
                    "duration": duration,
                    "names": names,
                }
