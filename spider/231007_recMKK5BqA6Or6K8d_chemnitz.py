import scrapy
from datetime import datetime, timedelta
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
            url="https://events.lauf-kultour.de/zeitmessung/results.php",
            formdata={
                "eventID": "88",
                "cat": "ff",
            },
        )

    def parse(self, response):

        for entry in response.json()["results"]:
            print(entry)

            if entry["time"] in ["DNS", "DNF"]:
                continue

            [minutes, seconds] = entry["time"] // 60, entry["time"] % 60

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                duration="00:%02d:%02d.0" % (minutes, seconds),
                type="MPA",
                category=entry["AK"][0].upper(),
                names=["%s %s" % (entry["forename"].strip(), entry["surname"].strip())],
                bib=entry["bib"],
            )
