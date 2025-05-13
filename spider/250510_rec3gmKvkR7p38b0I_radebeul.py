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

    race_id = "339886"
    race_key = "e94c697fe8e4c5a66536c55ba5d5e5ae"

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
            url="https://feuerwehrfitness-dresden.de/anmeldung-teilnehmer/",
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Feuerwehr|Ergebnis-Online",
                "contest": "0",
            },
            cb_kwargs={"competition_type": "MPA"},
        )

    def parse_starters(self, response):
        num_teams = 60 - int(response.css(".counter::text").get())
        for i in range(num_teams):
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=[None, None],
            )

    def parse(self, response, competition_type):
        ranks = {"category": {}}

        for _, team in response.json()["data"].items():
            [
                [_id1, _id2, bib, name1, _time, raw_duration, category],
                [_, _, _, name2, _, _, _],
            ] = team

            names = sorted(
                [name1, name2],
            )
            duration = "00:" + ("0" + raw_duration + ".0")[-7:]

            rank_total = ranks.get("total", 1)
            rank_category = ranks["category"].get(category, 1)

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=competition_type,
                category={
                    "Männer-Team": "M",
                    "Mixed-Team": "X",
                    "Frauen-Team": "W",
                }.get(category),
                duration=duration,
                names=names,
                rank=ResultRankItem(
                    total=rank_total,
                    category=rank_category,
                ),
                bib=bib.split("-")[0],
            )

            ranks["total"] = rank_total + 1
            ranks["category"][category] = rank_category + 1
