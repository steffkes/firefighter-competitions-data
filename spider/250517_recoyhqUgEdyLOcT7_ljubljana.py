from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://remote.timingljubljana.si/stepup/pregledprijav.aspx",
            callback=self.parse_starters,
        )

    def fixName(self, name):
        return " ".join(
            map(lambda part: part[0].upper() + part[1:].lower(), name.split(" "))
        )

    def parse_starters(self, response):
        for row in response.css("table tr"):
            cells = row.css("td ::text").getall()

            if len(cells) != 7:
                continue

            [lastname, firstname, _gender, _team, _bib, _unknown, group] = cells

            if not group in [
                "Step Up - Gasilci Smartwater",
                "Step Up - Ekstremna Štafeta  - Gasilci",
            ]:
                continue

            yield ParticipantItem(
                competition_id=self.competition_id,
                names=[self.fixName("%s %s" % (firstname, lastname))],
            )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("TOMAŽ ANŽIČ", "Tomaž Anžič"),
        ("LUKA KNEZ LAZAR", "Luka Knez Lazar"),
        ('OŽBEJ "STEROID" ŠKERBEC', 'Ožbej "steroid" Škerbec'),
    ],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
