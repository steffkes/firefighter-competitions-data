import scrapy
from util import (
    Spider,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
    SlotItem,
)


class CompetitionSpider(Spider):
    name = __name__

    race_id = "394956"
    race_key = ""

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/registration/config" % self.race_id,
            callback=self.parse_slots,
        )

    def parse_slots(self, response):
        yield SlotItem(
            competition_id=self.competition_id,
            amount=response.json()["Registrations"][0]["Contests"][0]["SlotsLeft"],
        )
