from util import Spider, ParticipantItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__
    race_id = "315247"
    race_key = "7e4105dee620c764485e85a405c3988f"

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "rr Timing|Teilnehmerliste_Feuerwehrlauf",
                "contest": "0",
            },
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        for [
            _id1,
            _id2,
            _origin,
            name1,
            name2,
            _yob1,
            _yob2,
            _gender,
        ] in response.json()["data"]["#1_Feuerwehrlauf"]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted([name1, name2]),
            )
