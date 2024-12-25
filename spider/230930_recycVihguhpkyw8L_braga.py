import scrapy
from datetime import datetime
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
            url="https://www.sinctime.com/evento/146/resultados-externos?prova=452&pagina=1",
        )

    def parse(self, response):
        for entry in response.css("table.table tbody tr"):
            [_, _, bib, name, _, _category, duration] = entry.css("td::text").getall()

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                duration=duration + ".0",
                type="OPA",
                category=None,
                names=[name.strip()],
                bib=bib,
            )

        yield from response.follow_all(response.css(".pager a"))
