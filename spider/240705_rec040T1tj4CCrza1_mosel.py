from util import FccSpider, ParticipantItem
import scrapy


class CompetitionSpider(FccSpider):
    name = __name__
    event_id = 17
    event_day_ids = [34, 35, 36]
