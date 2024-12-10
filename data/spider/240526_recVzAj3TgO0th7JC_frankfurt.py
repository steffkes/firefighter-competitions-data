import scrapy
from datetime import datetime
import re
import itertools
import string
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem
from scrapy.utils.python import to_bytes
from collections import defaultdict


class FrankfurtJsonItemExporter(JsonItemExporter):
    def finish_exporting(self):
        groups = defaultdict(list)
        for item in self.items:
            groups[item["names"][0]].append(item["names"][1])

        teams = sorted(
            groups.values(),
            key=lambda entry: (len(entry), entry),
        )
        data = {
            "date": datetime.now().isoformat(),
            "competition_id": self.items[0]["competition_id"],
            "count": len(list(itertools.chain.from_iterable(teams))),
            "teams": teams,
        }

        self.file.write(
            to_bytes(
                self.encoder.encode(data) + "\n",
                self.encoding,
            )
        )


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "277814"
    race_key = "0fdd4b818141191b0084fc27c0714d40"

    custom_settings = {
        "FEED_EXPORTERS": {
            "starter": FrankfurtJsonItemExporter,
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
        for contest in [3, 4]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "listname": "Teilnehmerlisten|TN Startzeit",
                    "contest": str(contest),
                },
                callback=self.parse_starters,
            )

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

    def parse_starters(self, response):
        fixName = lambda name: " ".join(reversed(list(map(str.strip, name.split(",")))))

        for [
            _id,
            _empty,
            bib,
            name,
            _gender,
            _category,
            _team,
            _nationality,
            _competition,
            _empty,
        ] in response.json()["data"]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=(bib.split("-")[0], fixName(name)),
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
            bib,
        ] in (
            data[data_key]["#1_M"] + data[data_key]["#2_W"]
        ):
            duration = "0" + ("0:%s" % raw_duration.replace(",", "."))[-9:]

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                bib=bib,
                type=competition_type,
                duration=duration,
                category=category,
                names=[fixName(name)],
            )
