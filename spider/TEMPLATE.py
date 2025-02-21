from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__

    """
    @staticmethod
    def fixName(name):
        return name
    """

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="http://example.org",
            formdata={},
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(method="GET", url="http://example.org", formdata={})

    def parse_starters(self, response):
        yield ParticipantItem(
            competition_id=self.competition_id,
            names=[self.fixName(None)],
        )

    def parse(self, response):
        yield ResultItem(
            date=self.race_date,
            competition_id=self.competition_id,
            type="OPA",
            duration=None,
            names=[self.fixName(None)],
            category=None,
            age_group=None,
            bib=None,
            rank=ResultRankItem(
                total=None,
                category=None,
                age_group=None,
            ),
        )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
