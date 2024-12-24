import scrapy
from datetime import datetime
import re
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "315581"
    race_key = "f30e6a1c244e9e63717a97aead9fdb3a"

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
                "listname": "02_Teilnehmerlisten|Teilnehmer_Schanzenlauf",
                "contest": "1",
            },
            callback=self.parse_starters,
        )

    def parse_starters_team(self, response):
        fixName = lambda name: re.sub(
            r"^(.+)\s(.+)$",
            lambda match: "%s %s"
            % (
                match.group(2),
                re.sub(
                    r"^(.)(.+)$",
                    lambda match: "%s%s" % (match.group(1), match.group(2).lower()),
                    match.group(1),
                ),
            ),
            name.strip(),
        )

        data = response.json()["data"]
        tmp1 = next(iter(data.values()))
        tmp2 = next(iter(tmp1.values()))
        tmp3 = next(iter(tmp2.values()))

        [
            [_bib1, name1, _sex1, _category1, _year1, _competition1],
            [_bib2, name2, _sex2, _category2, _year2, _competition2],
        ] = tmp3
        yield ParticipantItem(
            competition_id=self.competition_id,
            names=sorted(map(fixName, [name1, name2])),
        )

    def parse_starters(self, response):
        for team in response.json()["groupFilters"][0]["Values"]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "listname": "02_Teilnehmerlisten|Teilnehmer_Schanzenlauf",
                    "contest": "1",
                    "f": team,
                },
                callback=self.parse_starters_team,
            )
