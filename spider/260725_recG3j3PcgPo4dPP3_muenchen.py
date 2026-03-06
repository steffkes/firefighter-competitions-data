from util import Spider, ParticipantItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    race_id = "386070"
    race_key = "57b676840dcaaa17ade096effc44a0ef"

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "02_Teilnehmerlisten|Teilnehmer_Schanzenlauf",
                "contest": "1",
            },
            callback=self.parse_starters,
        )

    def parse_starters(self, response):
        # double nested structure.
        for [[_id1, _id2, name1, name2]] in (response.json()["data"] or {}).values():
            yield ParticipantItem(
                competition_id=self.competition_id, names=sorted([name1, name2])
            )
