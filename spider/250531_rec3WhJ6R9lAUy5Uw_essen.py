from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__
    race_id = "335507"
    race_key = "71e2b253b08c4c1165959c436b26c937"

    @staticmethod
    def fixName(name):
        return " ".join(reversed(name.split(","))).strip()

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Teilnehmerlisten|TN ABC",
                "contest": "3",
            },
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "Ergebnislisten|EG TN keine Staffel RANG",
                "contest": "3",
            },
        )

    def parse_starters(self, response):
        for [
            bib,
            _id1,
            name,
            _gender,
            _age_group,
            _yob,
            _team,
            _competition,
        ] in response.json()["data"]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=[self.fixName(name)],
            )

    def parse(self, response):
        for [
            bib,
            _id1,
            rank_total,
            name,
            _team,
            rank_category,
            category,
            _rank_age_group,
            raw_duration,
        ] in response.json()["data"]:

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="MPA",
                duration=self.fixDuration(raw_duration),
                names=[name],
                category=category,
                rank=ResultRankItem(total=int(rank_total), category=int(rank_category)),
                bib=bib,
            )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("Diedrigkeit, Tobias", "Tobias Diedrigkeit"),
        ("Gühmann, Ruben", "Ruben Gühmann"),
        ("van Emmenes, Jason", "Jason van Emmenes"),
    ],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
