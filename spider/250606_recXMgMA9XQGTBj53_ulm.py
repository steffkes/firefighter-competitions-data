from util import Spider, ParticipantItem, ResultItem, ResultRankItem
from itertools import chain
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__

    race_id = "343683"
    race_key = "44992c339ea83d3d0a4c770030e698a5"

    @staticmethod
    def fixName(name):
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
            (name or "").strip(),
        )

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/results/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "10 Ergebnislisten|00 Ergebnisliste MW",
                "contest": "0",
            },
        )

    def parse(self, response):
        ranks = {"total": 1, "category": {"M": 1, "W": 1}}

        for [
            bib,
            _id,
            _rank_total,
            name,
            _nationality,
            _team,
            rank_category,
            raw_duration,
            _diff,
        ] in list(chain.from_iterable(response.json()["data"].values())):

            if int(bib) not in [166, 167, 158, 161, 156, 157, 153, 160, 154, 163, 162]:
                continue

            category = rank_category[0]

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="MPA",
                duration=self.fixDuration(raw_duration),
                names=[self.fixName(name)],
                category=category,
                rank=ResultRankItem(
                    total=ranks["total"], category=ranks["category"][category]
                ),
            )

            ranks["total"] += 1
            ranks["category"][category] += 1


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
    assert CompetitionSpider.fixName(input) == output
