import scrapy
from datetime import datetime
import re
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "259924"
    race_key = "9cca7a2e787022b15a2c81b253b2dde6"

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
                "listname": "Online Ergebnisse und Listen|05 Ergebnisse Team ALLE WK",
            },
        )

        for contest in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "contest": str(contest),
                    "listname": "Online Ergebnisse und Listen|25 Teilnehmer nach Team",
                },
                callback=self.parse_starters,
            )

    def parse_starters(self, response):
        data = list(response.json()["data"].values())[0]
        for [_bib, _empty, _time, _team, _city, _origin, names, _category] in data:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(
                    map(
                        lambda name: re.match(r"^[^\(]+", name).group().strip(),
                        names.split(" / "),
                    )
                ),
            )

    def parse(self, response):
        data = response.json()["data"]
        for entry in data:
            [bib, _, _, _, _, _, raw_duration, names, _, category] = entry

            duration = "00:" + raw_duration.split(" ")[0].replace(",", ".")
            names = sorted(
                map(
                    lambda name: " ".join(name.strip().split(" ")[:-1]),
                    names.split(" / "),
                )
            )

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                bib=bib,
                type="MPA" if category[-1:] != "O" else "OPA",
                duration=duration,
                category={"MIX": "X", "MIXO": "X", "LADIES": "W"}.get(category, "M"),
                names=names,
            )