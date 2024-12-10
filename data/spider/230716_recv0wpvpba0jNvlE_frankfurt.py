import scrapy
from datetime import datetime
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "237482"
    race_key = "0ddada2a321627f3fb95d390874b97bd"

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
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "contest": "4",
                "listname": "Ergebnislisten|EG ZIEL M/W",
            },
            cb_kwargs={
                "competition_type": "MPA",
                "data_key": "#1_messeTurm FFC ELITE",
            },
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "contest": "3",
                "listname": "Ergebnislisten|EG ZIEL M/W",
            },
            cb_kwargs={
                "competition_type": "OPA",
                "data_key": "#1_messeTurm FFC FIGHTER",
            },
        )

    def parse(self, response, data_key, competition_type):
        data = response.json()["data"]
        for entry in data[data_key]["#1_M"] + data[data_key]["#2_W"]:
            [bib, _, name, _, _, category, _, _, _, raw_duration, _] = entry

            name = " ".join(reversed(list(map(str.strip, name.split(",")))))
            duration = "0" + ("0:" + raw_duration.replace(",", "."))[-9:]

            # skyrun is a special case. it's a team competition but
            # everyone is running for him-/herself. so we're treating
            # this one as single-run!

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                bib=bib,
                type=competition_type,
                duration=duration,
                category=category,
                names=[name],
            )
