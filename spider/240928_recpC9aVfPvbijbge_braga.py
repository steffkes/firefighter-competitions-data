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
            url="https://api.stopandgo.pro/xcrono/classificacao_individual.php/?id_evento=1371",
        )

    def parse(self, response):
        rank = {"category": {}, "age_group": {}}

        for entry in response.json():
            category = {"F": "W"}.get(entry["sexo"], entry["sexo"])
            age_group = entry["escalao"]

            rank["category"][category] = rank["category"].get(category, 0) + 1
            rank["age_group"][age_group] = rank["age_group"].get(age_group, 0) + 1

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                duration=entry["tempo"][0:10],
                type="OPA",
                category=category,
                names=[entry["nome"]],
                bib=entry["dorsal"],
                age_group=age_group,
                rank=ResultRankItem(
                    total=int(entry["pos"]),
                    category=rank["category"][category],
                    age_group=rank["age_group"][age_group],
                ),
            )
