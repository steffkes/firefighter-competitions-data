from util import Spider, ParticipantItem, ResultItem, ResultRankItem, SlotItem
from itertools import batched
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__
    race_id = "340048"
    race_key = "159bc32560a3f6d9c498b3a4435fee48"

    @staticmethod
    def fixName(name):
        return " ".join(reversed(name.split(", ")))

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Online|Teilnehmer",
                "contest": "0",
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
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Online|Final",
                "contest": "1",
                "name": "%231_StairRun - Feuerwehr",
            },
        )

    def parse_slots(self, response):
        contests = response.json()["RegistrationConfig"]["Registrations"][0]["Contests"]

        filterFn = lambda contest: contest["Name"] == "StairRun - Feuerwehr"
        for contest in filter(filterFn, contests):
            yield SlotItem(
                competition_id=self.competition_id, amount=int(contest["SlotsLeft"] / 2)
            )

    def parse_starters(self, response):
        for entries in response.json()["data"]["#1_StairRun - Feuerwehr"].values():
            for [
                [
                    _id1_1,
                    _bib_1,
                    raw_name_1,
                    _team_1,
                    _country_1,
                    _year_1,
                    _age_group_1,
                ],
                [
                    _id1_2,
                    _bib_2,
                    raw_name_2,
                    _team_2,
                    _country_2,
                    _year_2,
                    _age_group_2,
                ],
            ] in batched(entries, 2):
                yield ParticipantItem(
                    competition_id=self.competition_id,
                    names=sorted(map(self.fixName, [raw_name_1, raw_name_2])),
                )

    def parse(self, response):
        results = []
        mapping = {
            "#1_M": ("M", "M"),
            "#2_M 100": ("M", "M 100"),
            "#3_M 80": ("M", "M 80"),
            "#4_Mix": ("X", None),
            "#5_W": ("W", None),
        }

        for ident, records in response.json()["data"][
            "#1_StairRun - Feuerwehr"
        ].items():
            (category, age_group) = mapping[ident.strip()]

            for record in records:
                [
                    _id1,
                    _id2,
                    _rank_age_group,
                    bib,
                    _team,
                    name1,
                    name2,
                    raw_duration,
                ] = record

                result = ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type="MPA",
                    duration=self.fixDuration(raw_duration),
                    names=sorted([name1, name2]),
                    category=category,
                    age_group=age_group,
                    bib=bib,
                    rank=ResultRankItem(),
                )
                results.append(result)

        ranks = {
            "category": {},
            "age_group": {},
        }

        for result in sorted(results, key=lambda result: result["duration"]):
            result["rank"]["total"] = ranks.get("total", 1)
            ranks["total"] = result["rank"]["total"] + 1

            result["rank"]["category"] = ranks["category"].get(result["category"], 1)
            ranks["category"][result["category"]] = result["rank"]["category"] + 1

            if result["age_group"]:
                result["rank"]["age_group"] = ranks["age_group"].get(result["age_group"], 1)
                ranks["age_group"][result["age_group"]] = result["rank"]["age_group"] + 1

        yield from results


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("Tänzer, Mirko", "Mirko Tänzer"),
        ("Rische, Jan-Nick", "Jan-Nick Rische"),
        ("Kulhánek, Jakub", "Jakub Kulhánek"),
    ],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
