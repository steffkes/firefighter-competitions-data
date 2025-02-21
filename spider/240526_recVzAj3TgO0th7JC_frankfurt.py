import scrapy
from datetime import datetime
import re
import itertools
import string
from util import (
    JsonItemExporter,
    JsonLinesItemExporter,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
)
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
                    "listname": "Ergebnislisten|EG ZIEL Teamwertung FF&RDC",
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

        groups = []
        results = []
        for team, names in data[data_key].items():
            [rank_team, raw_team_duration] = re.match(
                r"\#\d+_(\d+)\.///.*?///(.+)", team
            ).group(1, 2)

            [
                [_id1, bib1, name1, raw_duration1, age_group1, _nationality1],
                [_id2, bib2, name2, raw_duration2, age_group2, _nationality2],
                [_id3, bib3, name3, raw_duration3, age_group3, _nationality3],
            ] = names

            team_gender = list(
                set(map(lambda ag: ag[0].upper(), [age_group1, age_group2, age_group3]))
            )
            team_category = team_gender[0] if len(team_gender) == 1 else "X"
            team_duration = ("00:" + raw_team_duration.replace(",", "."))[-10:]

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=competition_type,
                duration=team_duration,
                category=team_category,
                names=sorted(map(fixName, [name1, name2, name3])),
                rank=ResultRankItem(total=int(rank_team)),
                bib=bib1.split("-")[0],
            )

            for bib, name, raw_duration, age_group in zip(
                [bib1, bib2, bib3],
                [name1, name2, name3],
                [raw_duration1, raw_duration2, raw_duration3],
                [age_group1, age_group2, age_group3],
            ):
                duration = "0" + ("0:%s" % raw_duration.replace(",", "."))[-9:]
                category = age_group[0].upper()

                result = ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type=competition_type,
                    duration=duration,
                    category=category,
                    age_group=age_group,
                    names=[fixName(name)],
                    bib=bib,
                )
                results.append(result)
                groups.append((category, age_group))

        results = sorted(results, key=lambda result: result["duration"])

        for category, age_group in sorted(set(groups)):
            entries_type = results
            entries_category = list(
                filter(lambda result: result["category"] == category, entries_type)
            )
            entries_age_group = list(
                filter(
                    lambda result: result["age_group"] == age_group, entries_category
                )
            )

            for entry in entries_age_group:
                entry["rank"] = ResultRankItem(
                    total=entries_type.index(entry) + 1,
                    category=entries_category.index(entry) + 1,
                    age_group=entries_age_group.index(entry) + 1,
                )

                yield entry
