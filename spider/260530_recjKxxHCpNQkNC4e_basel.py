from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    @staticmethod
    def fixName(name):
        parts = name.split(" ")
        parts.append(parts.pop(0))
        return " ".join(parts)

    def start_requests(self):
        for page in range(1, 4):
            yield scrapy.FormRequest(
                method="GET",
                url="https://results.datasport.com/api",
                formdata={
                    "task": "ranking",
                    "edition": "tower-run-basel2026",
                    "slug": "mixt-in-4er-teams",
                    "lang": "de",
                    "page": str(page),
                },
            )

    def parse(self, response):
        for team in response.json()["table"]["teams"]:
            names = []
            for person in team["rows"]:
                name = self.fixName(person["name"]["text"])
                names.append(name)

                yield ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type="MPA",
                    duration=self.fixDuration(person["time.main"]["text"]),
                    names=[name],
                )

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="MPA",
                duration=self.fixDuration(team["data"]["time.main"]["text"]),
                names=sorted(names),
                rank=ResultRankItem(
                    total=team["data"]["rank.main"],
                ),
            )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("Woischnig Anne-Kathrin", "Anne-Kathrin Woischnig"),
        ("Volger Natalie Patricia", "Natalie Patricia Volger"),
        ("Birmes Lukas", "Lukas Birmes"),
    ],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
