from util import FccSpider


class CompetitionSpider(FccSpider):
    name = __name__
    event_day_ids = [51, 52, 53]
    event_id = 25
