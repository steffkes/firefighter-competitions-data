import scrapy
from pathlib import Path


class Spider(scrapy.Spider):
    name = __name__

    custom_settings = {
        "FEEDS": {
            "../data/counts.jsonl": {
                "format": "jsonlines",
                "encoding": "utf8",
                "overwrite": False,
            },
        },
        "EXTENSIONS": {
            "scrapy.extensions.telnet.TelnetConsole": None,
        },
    }

    def start_requests(self):
        for path in map(
            lambda path: "file://%s" % path.resolve(),
            filter(
                lambda path: path.stat().st_size, Path("../data/teams").glob("*.json")
            ),
        ):
            yield scrapy.Request(path)

    def parse(self, response):
        data = response.json()

        yield {
            "date": data["date"],
            "competition": data.get("competition_id") or data["competition"],
            "count": data["count"],
        }
