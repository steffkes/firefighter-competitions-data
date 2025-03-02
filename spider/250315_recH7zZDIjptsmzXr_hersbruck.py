import scrapy
import itertools
from datetime import datetime
from util import (
    Spider,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
)


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://www.feuerwehr-hersbruck.de/",
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        for names in itertools.repeat([None], 60):
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=names,
            )
