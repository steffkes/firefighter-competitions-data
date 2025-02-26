from util import Spider, ParticipantItem, ResultItem, ResultRankItem
from pathlib import Path
import scrapy
import csv


class CompetitionSpider(Spider):
    name = __name__

    @staticmethod
    def fixName(name):
        [*lastname, firstname] = name.split(" ")
        return " ".join(
            map(lambda str: str[0] + str[1:].lower(), [firstname, *lastname])
        )

    def start_requests(self):
        yield scrapy.Request(
            "file://%s" % Path("spider/data/%s.csv" % self.name).resolve()
        )

    def parse(self, response):
        reader = csv.DictReader(
            response.body.decode("utf-8").splitlines(), delimiter=";"
        )
        for row in reader:
            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                duration=row["Time"] + ".0",
                type="MPA",
                names=[self.fixName(row["Name"])],
                rank=ResultRankItem(total=int(row["Position"])),
                bib=row["BIB"],
            )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("MATHEIS STEFAN", "Stefan Matheis"),
        ("DAL FARRA ENRICO", "Enrico Dal Farra"),
        ("MOOZ LUKÁŠ", "Lukáš Mooz"),
    ],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
