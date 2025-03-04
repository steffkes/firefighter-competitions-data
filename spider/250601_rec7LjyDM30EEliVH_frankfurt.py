from util import Spider, ParticipantItem, ResultItem, ResultRankItem
from datetime import datetime
import scrapy
import itertools


class CompetitionSpider(Spider):
    name = __name__

    race_id = "323081"
    race_key = "14f8a539e0b868f9b00de1050a4d8bb8"

    def start_requests(self):
        for contest in [3, 4]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "listname": "Teilnehmerlisten|TN Startzeit",
                    "contest": str(contest),
                },
                callback=self.parse_starters,
            )

    def parse_starters(self, response):
        fixName = lambda name: " ".join(reversed(list(map(str.strip, name.split(",")))))

        starters = []
        for [
            _id,
            _number2,
            _empty,
            bib,
            name,
            _gender,
            _category,
            _team,
            _nationality,
            _competition,
            _empty,
        ] in response.json()["data"]:
            starters.append((bib[0:-2], fixName(name)))

        for bib, items in itertools.groupby(starters, lambda item: item[0]):
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(lambda item: item[1], items)),
            )
