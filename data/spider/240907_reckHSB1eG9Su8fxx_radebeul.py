import scrapy
from datetime import datetime
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem

changedParticipants = {"Matthias Buttig": "Dominik Thiel"}


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "306993"
    race_key = "74179817c718adcf847cc589ff700c91"

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
                "listname": "Feuerwehr|Ergebnis-Online",
                "contest": "0",
            },
            cb_kwargs={"competition_type": "MPA"},
        )

    def parse(self, response, competition_type):
        data = response.json()["data"]
        for _, team in data.items():
            [[_, bib, name1, _, raw_duration, category], [_, _, name2, _, _, _]] = team

            names = sorted(
                map(
                    lambda name: changedParticipants.get(name.strip(), name.strip()),
                    [name1, name2],
                )
            )
            duration = "00:" + ("0" + raw_duration + ".0")[-7:]

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                bib=bib,
                type=competition_type,
                category={
                    "Männer-Team": "M",
                    "Mixed-Team": "X",
                    "Frauen-Team": "W",
                }.get(category),
                duration=duration,
                names=names,
            )
