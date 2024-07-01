import scrapy
from datetime import datetime
from itertools import groupby
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
            "../data/teams/%(ident)s.json": {
                "format": "starter",
                "encoding": "utf8",
                "overwrite": True,
                "item_classes": [ParticipantItem],
            },
            "data/teams/%(name)s.jsonl": {
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
        for contest in [9026, 9027]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://www.racement.com/rennen/stairrun-oberhof-2024",
                formdata={
                    "action": "site/table-data/get-race-participants",
                    "raceId": "434519",
                },
                callback=self.parse_starters,
            )

    def parse_starters(self, response):
        fireteam_filter = lambda row: row["classification"] == "Feuerwehr-Team"
        team_groupfn = lambda row: str(row["team"])

        data = response.json()["data"]
        for _team, entries in groupby(
            sorted(filter(fireteam_filter, data), key=team_groupfn), key=team_groupfn
        ):
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(
                    map(
                        lambda entry: "%s %s" % (entry["firstName"], entry["name"]),
                        entries,
                    )
                ),
            )
