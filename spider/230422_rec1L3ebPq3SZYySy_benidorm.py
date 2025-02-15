import scrapy
from datetime import datetime
from util import (
    JsonItemExporter,
    JsonLinesItemExporter,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
)


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    ranks = {"category": {}, "age_group": {}}

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
            url="https://cronorunner.com/resultados.php?ref=441-1668-1670",
        )

    def parse(self, response):
        for row in response.css(
            "#clasificados .table-clasificacion.table-desktop tbody tr"
        ):
            age_group = row.css(".campo-categoria::text").get()
            category = {"F": "W"}.get(age_group[-1], age_group[-1])

            category_rank = self.ranks["category"].get(category, 1)
            age_group_rank = self.ranks["age_group"].get(age_group, 1)

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="MPA",
                duration="%s.0" % row.css(".campo-tiempo::text").get(),
                names=[row.css(".nombre-corredor::text").get()],
                category=category,
                age_group=age_group,
                bib=row.css(".campo-dorsal::text").get(),
                rank=ResultRankItem(
                    total=int(row.css(".campo-posicion::text").get()),
                    category=category_rank,
                    age_group=age_group_rank,
                ),
            )

            self.ranks["category"][category] = category_rank + 1
            self.ranks["age_group"][age_group] = age_group_rank + 1
