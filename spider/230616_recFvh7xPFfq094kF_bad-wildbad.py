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

    race_id = 230471
    race_key = "db2e71ebb35ebe73a4e50d8be4d6debb"

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
            url="https://my.raceresult.com/%d/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "contest": "3",
                "listname": "Ergebnislisten|Ergebnisliste gesamt",
            },
            cb_kwargs={
                "competition_type": "OPA",
                "data_key": "#1_Feuerwehr-Stäffeleslauf",
            },
        )

    def parse(self, response, data_key, competition_type):
        for entry in response.json()["data"][data_key]:
            [
                bib,
                rank_total,
                category,
                rank_category,
                _,
                firstname,
                lastname,
                _,
                _,
                _,
                age_group,
                rank_age_group,
                raw_duration,
                _,
                _,
            ] = entry

            duration = "00:%s.0" % raw_duration

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=competition_type,
                duration=duration,
                names=["%s %s" % (firstname, lastname)],
                category=category.upper(),
                age_group=age_group,
                rank=ResultRankItem(
                    total=int(rank_total[:-1]),
                    category=int(rank_category[:-1]),
                    age_group=int(rank_age_group[:-1]),
                ),
                bib=bib,
            )
