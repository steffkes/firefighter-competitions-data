import scrapy
from datetime import datetime
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "198135"
    race_key = "c80ef6981e49e27673a5f11965acccb7"

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
                "listname": "Feuerwehr|Rundenliste Feuerwehr",
                "contest": "0",
            },
        )

    def parse(self, response):
        data = response.json()["data"]
        for entry in (
            data["#1_Feuerwehr (1) - Zeit: 20:31:31 - Durchschnitt: 13:31"]
            + data["#2_Feuerwehr (2) - Zeit: 2:50:41 - Durchschnitt: 12:11"]
        ):
            [_, _, raw_duration, name, _, gender] = entry

            if not raw_duration:
                continue

            duration = "00:%s.0" % raw_duration.zfill(5)

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="MPA",
                category={"weiblich": "W", "männlich": "M"}[gender],
                duration=duration,
                names=[name],
            )
