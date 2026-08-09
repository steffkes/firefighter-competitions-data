from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    @staticmethod
    def fixName(name):
        return " ".join(reversed(name.split(", ")))

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://myracepartner.com/veranstaltung/teilnehmer/",
            formdata={"event-id": "465438", "track-id": "465443"},
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        for cell in response.css("#table-filter tbody tr .full strong::text"):
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=[self.fixName(cell.get())],
            )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("Arendholz, Tim", "Tim Arendholz"),
        ("Graef, Simon-Aaron", "Simon-Aaron Graef"),
        ("Hoang, Manh Dat", "Manh Dat Hoang"),
    ],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
