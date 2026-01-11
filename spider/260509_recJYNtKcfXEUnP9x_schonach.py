import scrapy
from datetime import datetime
from util import (
    JsonItemExporter,
    JsonLinesItemExporter,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
)
import re


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = "374362"
    race_key = "255bcf6c67f4feca2bb04696fb90ff6b"

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

    @staticmethod
    def fixName(name):
        if not name:
            return ""

        return re.sub(
            r"(([A-ZÄÜÖß]+[-\s])?([A-ZÄÜÖß]+))\s(.+)",
            lambda match: " ".join(
                [
                    match.group(4),
                    "".join(
                        map(
                            lambda str: str[0] + str[1:].lower(),
                            filter(None, match.group(2, 3)),
                        )
                    ),
                ]
            ),
            name,
        )

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "02_Teilnehmerlisten|Teilnehmer_Schanzenlauf",
                "contest": "1",
                "f": "<Ignore><Ignore>",
            },
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "01_Feuerwehr|Ergebnisliste_Feuerwehr_Wertungen",
                "contest": "1",
            },
        )

    def parse_starters(self, response):
        for _team, record in response.json()["data"].items():
            [
                _bib1,
                _number21,
                _ln1,
                _fn1,
                _gender1,
                _competition1,
                _yob1,
                _category1,
                _n31,
                name1,
            ] = record[0]

            name2 = None
            if len(record) == 2:
                [
                    _bib2,
                    _number22,
                    _ln2,
                    _fn2,
                    _gender2,
                    _competition2,
                    _yob2,
                    _category2,
                    _n32,
                    name2,
                ] = record[1]

            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(self.fixName, [name1, name2])),
            )

    def parse(self, response):
        groups = []
        entries = []
        for group, teams in (response.json()["data"] or {}).items():
            (contest, raw_age_group) = re.match(
                r"#\d+_((Ohne|Mit) PA) / (\w+)\s", group
            ).group(1, 3)
            type = "MPA" if "Mit PA" == contest else "OPA"

            for team, names in teams.items():
                [rank_age_group, raw_duration] = re.match(
                    r"\#\d+_(\d+)\.///.*?///(.+)", team
                ).group(1, 2)
                [
                    [_id11, bib, _id21, name1, gender1, _time1],
                    [_id21, _bib2, _id22, name2, gender2, _time2],
                ] = names

                duration = "00:%s.0" % raw_duration.zfill(5)
                gender = list(set([gender1, gender2]))
                category = gender[0] if len(gender) == 1 else "X"
                age_group = raw_age_group if category == "M" else None
                groups.append((type, category, age_group))

                result = ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type=type,
                    duration=duration,
                    names=sorted([self.fixName(name1), self.fixName(name2)]),
                    category=category,
                    bib=bib,
                )

                if age_group:
                    result["age_group"] = age_group

                entries.append(result)

        entries = sorted(entries, key=lambda record: record["duration"])

        for group in sorted(set(groups)):
            (type, category, age_group) = group

            entries_type = list(filter(lambda entry: entry["type"] == type, entries))
            entries_category = list(
                filter(lambda entry: entry["category"] == category, entries_type)
            )
            entries_age_group = list(
                filter(
                    lambda entry: entry.get("age_group") == age_group, entries_category
                )
            )

            for entry in entries_age_group:
                entry["rank"] = ResultRankItem(
                    total=entries_type.index(entry) + 1,
                    category=entries_category.index(entry) + 1,
                )

                if "age_group" in entry:
                    entry["rank"]["age_group"] = entries_age_group.index(entry) + 1

                yield entry


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("HARTMANN Jörg", "Jörg Hartmann"),
        ("MÜLLER Naomi", "Naomi Müller"),
        ("KNIE Nicola Simon", "Nicola Simon Knie"),
        ("WEIßHAAR Philipp", "Philipp Weißhaar"),
        (None, ""),
    ],
)
def test_fixName(input, output):
    assert Spider.fixName(input) == output
