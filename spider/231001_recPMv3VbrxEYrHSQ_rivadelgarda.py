from util import Spider, ParticipantItem, ResultItem, ResultRankItem
from pathlib import Path
import scrapy
import csv


class CompetitionSpider(Spider):
    name = __name__

    delimiter = ";"

    def start_requests(self):
        yield scrapy.Request(
            "file://%s" % Path("spider/data/%s.csv" % self.name).resolve()
        )

    def parse(self, response):
        reader = csv.DictReader(
            response.body.decode("utf-8").splitlines(), delimiter=";"
        )
        for row in reader:
            [firstname, *lastname] = reversed(row["Name"].split(" "))
            names = map(lambda str: str[0] + str[1:].lower(), [firstname, *lastname])

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                duration=row["Time"] + ".0",
                type="MPA",
                category=None,
                names=[" ".join(names)],
                rank=ResultRankItem(total=int(row["Position"])),
                bib=row["BIB"],
            )
