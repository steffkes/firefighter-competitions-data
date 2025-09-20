from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__
    race_id = "328155"
    race_key = "f2b45a388c1b9035c1425887fbf67bda"

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
                "contest": "2",
            },
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Ergebnislisten|Ergebnisliste MW",
                "contest": "0",
            },
        )

    def parse_starters(self, response):
        for [
            _id1,
            _id2,
            name,
            _origin,
            _yob,
            _gender,
            _category,
            _department,
            _starttime,
        ] in response.json()["data"]["#1_Burgstäffeleslauf Esslingen (Feuerwehr)"]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=[self.fixName(name)],
            )

    def parse(self, response):
        ranks = {"category": {}, "age_group": {}}
        data = response.json()["data"]["#2_Burgstäffeleslauf Esslingen (Feuerwehr)"]

        for [
            bib,
            _something,
            rank_category,
            name,
            _country,
            _yob,
            age_group,
            _team,
            raw_duration,
        ] in (
            data["#3_Männlich"] + data["#4_Weiblich"]
        ):
            category = {"Frauen": "W"}.get(age_group, "M")

            rank_total = ranks.get("total", 0) + 1
            rank_category = ranks["category"].get(category, 0) + 1
            rank_age_group = ranks["age_group"].get(age_group, 0) + 1

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="OPA",
                duration=self.fixDuration(raw_duration),
                names=[self.fixName(name)],
                category=category,
                age_group=age_group,
                rank=ResultRankItem(
                    total=rank_total, category=rank_category, age_group=rank_age_group
                ),
                bib=None,
            )

            ranks["total"] = rank_total
            ranks["category"][category] = rank_category
            ranks["age_group"][age_group] = rank_age_group


import pytest


@pytest.mark.parametrize(
    "input,output",
    [("Bopp, Marc", "Marc Bopp"), ("Mötzung, Erik", "Erik Mötzung")],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
