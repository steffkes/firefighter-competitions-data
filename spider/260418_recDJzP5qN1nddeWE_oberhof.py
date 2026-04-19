from util import Spider, ParticipantItem, ResultItem, ResultRankItem, SlotItem
from itertools import batched, chain
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__
    race_id = 362068
    race_key = "378d16dcd5e34cfc336ebeaf786aabf2"

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/participants/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "02: Online Ergebnisse und Listen|26 Teilnehmer Team - Startzeit",
            },
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRRegStart/data/config" % self.race_id,
            callback=self.parse_slots,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/results/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "02: Online Ergebnisse und Listen|23a Ergebnisse AK - Team",
            },
        )

    def parse_slots(self, response):
        yield SlotItem(
            competition_id=self.competition_id,
            amount=int(
                response.json()["RegistrationConfig"]["Registrations"][1]["SlotsLeft"]
                / 2
            ),
        )

    def parse_starters(self, response):

        for [
            _number1,
            _number2,
            _time,
            _team,
            _department,
            names,
            _category,
        ] in response.json()["data"]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=extractNames(names),
            )

    def parse(self, response):
        data = response.json()["data"]

        del data["#3_Wertung: MIXO"]
        del data["#6_Wertung: WJ U20"]

        age_group_map = {
            "YOUNG": ("M", "Youngster"),
            "ELITE-YOUNG": ("M", "Youngster"),
            "OLDIE": ("M", "Oldies"),
            "ELITE-OLDIE": ("M", "Oldies"),
            "MIX": ("X", None),
            "ELITE-MIX": ("X", None),
            "LADIES": ("W", None),
        }

        durations = {"total": [], "M": [], "W": [], "X": []}
        results = []

        for entry in chain.from_iterable(data.values()):
            [_, _, rank_age_group, _, raw_duration, names, age_group, _] = entry

            if rank_age_group in ["DSQ", "a.k."]:
                continue

            (category, age_group) = age_group_map[age_group.split(" / ")[0]]

            duration = self.fixDuration(raw_duration.split(" ")[0])
            durations["total"].append(duration)
            durations[category].append(duration)

            results.append(
                ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type="MPA",
                    duration=duration,
                    names=extractNames(names),
                    category=category,
                    age_group=age_group,
                    rank=ResultRankItem(age_group=int(rank_age_group[:-1])),
                )
            )

        durations["total"] = sorted(set(durations["total"]))
        durations["M"] = sorted(set(durations["M"]))
        durations["W"] = sorted(set(durations["W"]))
        durations["X"] = sorted(set(durations["X"]))

        for result in results:
            result["rank"]["total"] = durations["total"].index(result["duration"]) + 1
            result["rank"]["category"] = (
                durations[result["category"]].index(result["duration"]) + 1
            )

            yield result


import re


def extractNames(names):
    return sorted(
        map(
            lambda name: re.match(r"^[^\(]+", name).group().strip(),
            names.split(" / "),
        )
    )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        (
            "Damian Pyka (ML/1975) / Jasmin Bohun (WL/1989)",
            ["Damian Pyka", "Jasmin Bohun"],
        ),
        (
            "Jörg Bohun (ML/1981) / Benjamin Schrader (ML/1985)",
            ["Benjamin Schrader", "Jörg Bohun"],
        ),
        (
            "Jasmin Bohun (WL/1989) / Bianca Schrader (WL/1990)",
            ["Bianca Schrader", "Jasmin Bohun"],
        ),
    ],
)
def test_extractNames(input, output):
    assert extractNames(input) == output
