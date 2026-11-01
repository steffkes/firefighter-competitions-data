import scrapy
from util import (
    Spider,
    ParticipantItem,
    SlotItem,
)


class CompetitionSpider(Spider):
    name = __name__

    # registration opened on 2026-11-01 and was fully booked the same day
    # with 80 participants; the organizers don't publish names, so every
    # participant is an entry without a name
    participants = 80

    def start_requests(self):
        yield scrapy.Request("data:,")

    def parse(self, _response):
        yield SlotItem(competition_id=self.competition_id, amount=0)

        for _ in range(self.participants):
            yield ParticipantItem(competition_id=self.competition_id, names=[None])
