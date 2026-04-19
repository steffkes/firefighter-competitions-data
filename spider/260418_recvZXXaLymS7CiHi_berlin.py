from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__

    @staticmethod
    def matchRankAndCategory(label):
        age_group_map = {
            "YOUNGSTER": ("M", "Youngster"),
            "OLDIES": ("M", "Oldies"),
            "OLDIES XL": ("M", "Oldies XL"),
            "MIX": ("X", "Mix"),
            "MIX XL": ("X", "Mix XL"),
            "LADIES": ("W", "Ladies"),
            "LADIES XL": ("W", "Ladies XL"),
        }

        (rank, age_group) = re.match(r"^(\d+)\. Pl\. (.+)$", label.strip()).groups()
        (category, age_group) = age_group_map[age_group]

        return (int(rank), category, age_group)

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://myracepartner.com/veranstaltung/ergebnisse/",
            formdata={"event-id": "498410", "result-id": "500113"},
        )

    def parse(self, response):
        rank = {"M": 1, "W": 1, "X": 1}

        for row in response.css("table.results tbody tr"):
            (rank_age_group, category, age_group) = self.matchRankAndCategory(
                " ".join(row.css("td:nth-child(5) ::text").getall())
            )

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="MPA",
                duration=self.fixDuration(
                    "".join(row.css("td:nth-child(6) strong ::text").getall())
                ),
                names=sorted(row.css("td:nth-child(3) ::text").getall()[0:2]),
                category=category,
                age_group=age_group,
                rank=ResultRankItem(
                    total=int(
                        re.match(
                            r"^\d+", row.css("td:nth-child(1) ::text").get()
                        ).group(0)
                    ),
                    category=rank[category],
                    age_group=rank_age_group,
                ),
            )

            rank[category] += 1


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        (" 1. Pl. YOUNGSTER", (1, "M", "Youngster")),
        (" 4. Pl. YOUNGSTER", (4, "M", "Youngster")),
        (" 3. Pl. OLDIES", (3, "M", "Oldies")),
        ("1. Pl. OLDIES XL", (1, "M", "Oldies XL")),
        ("1. Pl. MIX", (1, "X", "Mix")),
        ("1. Pl. MIX XL", (1, "X", "Mix XL")),
        ("1. Pl. LADIES", (1, "W", "Ladies")),
        ("1. Pl. LADIES XL", (1, "W", "Ladies XL")),
    ],
)
def test_MatchRankAndCategory(input, output):
    assert CompetitionSpider.matchRankAndCategory(input) == output
