from util import FccSpider


class CompetitionSpider(FccSpider):
    name = __name__
    event_day_ids = [45, 46, 47]
