import scrapy
from datetime import datetime
from itertools import groupby
from util import (
    JsonItemExporter,
    JsonLinesItemExporter,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
)
from pathlib import Path
import csv

changedParticipants = {"Nico Schimeczek": "Matthias Buttig"}


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
            url="https://www.racement.com/rennen/stairrun-oberhof-2024",
            formdata={
                "action": "site/table-data/get-race-participants",
                "raceId": "434519",
            },
            callback=self.parse_starters,
        )

        yield scrapy.Request(
            "file://%s"
            % Path("spider/data/241207_rectoqxiOwNaoaHRZ_oberhof.csv").resolve()
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
                        lambda entry: fixName(
                            (entry["firstName"], entry["name"])
                        ).strip(),
                        entries,
                    )
                ),
            )

    def parse(self, response):

        def nameMapper(name):
            fixedName = fixResultName(name)
            return changedParticipants.get(fixedName, fixedName)

        reader = csv.DictReader(
            response.body.decode("utf-8").splitlines(), delimiter=";"
        )

        results = []
        groups = []

        for row in reader:
            result = ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                duration="00:" + (("0" + row["Time"])[-9:])[:7],
                type="MPA",
                names=sorted(map(nameMapper, [row["Name 1"], row["Name 2"]])),
                category={"MIX": "X"}.get(row["Category"], row["Category"]),
                bib=row["No"],
            )

            if row["Age Group"]:
                result["age_group"] = row["Age Group"]

            results.append(result)
            groups.append((result["category"], result.get("age_group")))

        for category, age_group in sorted(set(groups)):
            results_category = list(
                filter(lambda result: result["category"] == category, results)
            )
            results_age_group = list(
                filter(
                    lambda result: result.get("age_group") == age_group,
                    results_category,
                )
            )

            for result in results_age_group:
                result["rank"] = ResultRankItem(
                    total=results.index(result) + 1,
                    category=results_category.index(result) + 1,
                )

                if age_group:
                    result["rank"]["age_group"] = results_age_group.index(result) + 1

                yield result


import re


def fixName(name):
    (firstname, lastname) = name
    return " ".join(
        [
            firstname,
            "".join(
                re.sub(
                    r"[A-ZÄÜÖß]+[\s-]?",
                    lambda match: match.group(0)[0] + match.group(0)[1:].lower(),
                    lastname,
                )
            ),
        ]
    )


def fixResultName(name):
    return re.sub(
        r"(([A-ZÄÜÖäüöß]+[-\s])?([A-ZÄÜÖäüöß]+))\s(.+)",
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
        name.replace(",", ""),
    )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        (("Máté", "FEGYVERNEKI"), "Máté Fegyverneki"),
        (("Peter", "HÄUSLER"), "Peter Häusler"),
        (("Hans-Josef", "MEISENBERG"), "Hans-Josef Meisenberg"),
        (("Alex", "VAN MECHELEN"), "Alex Van Mechelen"),
        (("Florian", "OERTELT-GRIMM"), "Florian Oertelt-Grimm"),
    ],
)
def test_fixName(input, output):
    assert fixName(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        ("ZIMMERMANN Maj-Britt", "Maj-Britt Zimmermann"),
        ("NAUSCHÜTZ Desirée", "Desirée Nauschütz"),
        ("WEIßMANN Lucas", "Lucas Weißmann"),
        ("HUIZINGA, Gjalt", "Gjalt Huizinga"),
        ("BEYER-BRENZ Paula", "Paula Beyer-Brenz"),
        ("SCHREITMüLLER Steve", "Steve Schreitmüller"),
        ("TäNZER Mirko", "Mirko Tänzer"),
    ],
)
def test_fixResultName(input, output):
    assert fixResultName(input) == output
