import scrapy
from datetime import datetime
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "210595"
    race_key = "c1080e06f270bfa9c6172101d8fb33bb"

    custom_settings = {
        "FEED_EXPORTERS": {
            "results": JsonLinesItemExporter,
        },
        "FEEDS": {
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
        for contest, competition_type, data_key in [
            (3, "OPA", "#1_messeTurm FFC FIGHTER"),
            (4, "MPA", "#1_messeTurm FFC ELITE"),
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "listname": "Ergebnislisten|EG ZIEL M/W",
                    "contest": str(contest),
                },
                cb_kwargs={
                    "competition_type": competition_type,
                    "data_key": data_key,
                },
            )

    def parse(self, response, data_key, competition_type):
        fixName = lambda name: " ".join(reversed(list(map(str.strip, name.split(",")))))

        data = response.json()["data"]
        for [
            _id,
            _rank,
            name,
            _team,
            _nationality,
            category,
            _category_detail,
            _rank_age,
            _rank_total,
            raw_duration,
            _gap,
            bib,
        ] in (
            data[data_key]["#1_M"] + data[data_key]["#2_W"]
        ):
            duration = "0" + ("0:%s" % raw_duration.replace(",", "."))[-9:]

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                duration=duration,
                type=competition_type,
                category=category,
                names=[fixName(name)],
                bib=bib,
            )
