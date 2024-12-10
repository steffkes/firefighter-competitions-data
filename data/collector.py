import scrapy
from pathlib import Path
from active_spiders import spiders
import re


class Spider(scrapy.Spider):
    name = __name__

    custom_settings = {
        "FEEDS": {
            "data/participants/counts.jsonl": {
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
        yield from map(
            lambda path: scrapy.Request("file://%s" % path.resolve()),
            filter(
                lambda path: path.stat().st_size,
                map(
                    lambda path: Path("data/participants").joinpath(
                        re.match(r"^\d+_[^_]+", path.name)[0] + ".json"
                    ),
                    spiders,
                ),
            ),
        )

    def parse(self, response):
        data = response.json()

        yield {
            "date": data["date"],
            "competition": data.get("competition_id") or data["competition"],
            "count": data["count"],
        }
